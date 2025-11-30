import json
import re
from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.config import GROQ_API_KEY
from app.agents.tools import all_tools, check_for_harmful_intent

# --- 1. Define Agent State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    patient_id: str
    file_path: Union[str, None]  # Path to a temporarily uploaded file
    
# --- 2. Initialize LLM and Tool Executor ---
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
# tool_executor = ToolExecutor(all_tools) # Deprecated
tools_map = {t.name: t for t in all_tools}

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(all_tools)

# --- 3. Define Graph Nodes ---

async def sos_node(state: AgentState) -> AgentState:
    """SOS Node: Checks the latest user message for harm or emergencies."""
    last_message = state["messages"][-1].content
    classification = await check_for_harmful_intent(last_message)
    
    if classification == "SOS":
        state["messages"].append(AIMessage(
            content="I am not equipped to handle medical emergencies. Please call your local emergency services immediately."
        ))
        return {**state, "classification": "SOS"} # End graph
        
    if classification == "HARMFUL":
        state["messages"].append(AIMessage(
            content="I cannot respond to that query. Please ask a valid medical question."
        ))
        return {**state, "classification": "HARMFUL"} # End graph
        
    return {**state, "classification": "SAFE"} # Continue graph

async def call_model_node(state: AgentState) -> AgentState:
    """Agent Node: Calls the LLM to decide on actions or respond."""
    print("Node: call_model")
    
    # Build comprehensive system prompt with tool guidance
    current_messages = state["messages"]
    system_prompt = f"""You are a compassionate and knowledgeable AI medical assistant helping patient {state['patient_id']}.

Your role:
- Provide clear, empathetic explanations of medical information
- Translate medical jargon into accessible language
- Always personalize responses using the patient's actual medical history
- Cite your sources when using EHR data

IMPORTANT: When you need patient-specific information, you MUST use the available tools. Do NOT make up or guess patient data.

Available tools:
- ehr_rag_search: Use for finding relevant information from patient records (symptoms, conditions, medications, labs)
- ehr_get_latest_lab: Get specific lab result by name (e.g., "HbA1c", "glucose")
- ehr_get_all_labs: Get all lab results
- ehr_get_medications: Get current medications
- ehr_get_conditions: Get diagnosed conditions
- get_ehr_data: Get formatted summary of entire EHR
- web_search: Search for general medical information (not patient-specific)

Response format:
- Always cite sources at the end: "📊 Data sources used: [tool names]"
- Include disclaimer: "⚠️ This is educational information. Please consult your doctor for medical decisions."
- Be specific with data: "Your HbA1c on 2025-10-20 was 7.2%" not vague statements

Guidelines:
- Use EHR tools FIRST for patient-specific questions
- If EHR data is missing, say: "I don't see that information in your records"
- Keep explanations simple and friendly"""
    
    # Prepend the system prompt
    messages_with_prompt = [SystemMessage(content=system_prompt)] + current_messages
    
    try:
        response = await llm_with_tools.ainvoke(messages_with_prompt)
        
        # Check if response has malformed function calls in content
        if hasattr(response, 'content') and response.content:
            # Check for malformed function call syntax in text
            if "<function=" in response.content or "</function>" in response.content:
                print("Warning: Detected malformed function call in response content. Cleaning...")
                # Remove malformed function call syntax
                response.content = re.sub(r'<function=.*?</function>', '', response.content, flags=re.DOTALL)
                response.content = response.content.strip()
        
        state["messages"].append(response)
    except Exception as e:
        # Handle tool calling errors
        error_msg = str(e)
        print(f"Error in LLM call: {error_msg}")
        
        # If it's a tool calling error, try without tools as fallback
        if "tool_use_failed" in error_msg or "function" in error_msg.lower() or "400" in error_msg:
            print("Tool calling failed, trying without tools as fallback...")
            try:
                # Fallback: call LLM without tools but with instruction to use available data
                fallback_prompt = system_prompt + "\n\nNote: You can provide general medical information, but for patient-specific data, please ask the user to rephrase their question more specifically."
                fallback_messages = [SystemMessage(content=fallback_prompt)] + current_messages
                response = await llm.ainvoke(fallback_messages)
                state["messages"].append(response)
            except Exception:
                # Final fallback: return helpful error message
                state["messages"].append(AIMessage(
                    content="I apologize, but I encountered an error processing your request. Please try rephrasing your question or contact support if the issue persists."
                ))
        else:
            # Other errors: return error message
            state["messages"].append(AIMessage(
                content=f"I apologize, but I encountered an error. Please try again."
            ))
    
    return state

async def call_tools_node(state: AgentState) -> AgentState:
    """Tools Node: Executes tools called by the agent."""
    print("Node: call_tools")
    last_message = state["messages"][-1]
    
    if not last_message.tool_calls:
        # No tools called, just return
        return state

    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        print(f"Executing tool: {tool_name}")
        
        # Special handling for vision agent: inject file_path
        args = tool_call["args"]
        if tool_name == "analyze_medical_image":
            if state.get("file_path"):
                args["file_path"] = state["file_path"]
            else:
                tool_messages.append(ToolMessage(
                    content="Error: User asked to analyze an image, but no file was provided.",
                    tool_call_id=tool_call["id"]
                ))
                continue
        
        # Add patient_id if not present
        if "patient_id" not in args:
            args["patient_id"] = state["patient_id"]
            
        # action = ToolInvocation(tool=tool_name, tool_input=args)
        # response = await tool_executor.ainvoke(action)
        
        if tool_name in tools_map:
            tool = tools_map[tool_name]
            response = await tool.ainvoke(args)
        else:
            response = f"Error: Tool {tool_name} not found."
        
        tool_messages.append(ToolMessage(
            content=str(response),
            tool_call_id=tool_call["id"]
        ))
        
    state["messages"].extend(tool_messages)
    return state

# --- 4. Define Graph Edges ---

def router_edge(state: AgentState) -> str:
    """Router: Decides the next step."""
    
    # If SOS/HARMFUL, end
    if state.get("classification") in ["SOS", "HARMFUL"]:
        return END
    
    # If the last message was an AI message with tool calls, run tools
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "call_tools"
    
    # Otherwise, end (meaning the AI has given its final text answer)
    return END

# --- 5. Assemble the Graph ---

print("Assembling LangGraph...")
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("sos_check", sos_node)
workflow.add_node("call_model", call_model_node)
workflow.add_node("call_tools", call_tools_node)

# Define flow
workflow.set_entry_point("sos_check")
workflow.add_conditional_edges(
    "sos_check",
    lambda state: state.get("classification", "SAFE"),
    {
        "SAFE": "call_model",
        "SOS": END,
        "HARMFUL": END
    }
)
workflow.add_conditional_edges(
    "call_model",
    router_edge,
    {
        "call_tools": "call_tools",
        END: END
    }
)
workflow.add_edge("call_tools", "call_model")

# Compile the graph
app_graph = workflow.compile()
print("LangGraph compiled. 🚀")