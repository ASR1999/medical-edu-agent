import json
from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
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
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tool_executor = ToolExecutor(all_tools)

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
    system_prompt = f"""
You are a compassionate and knowledgeable AI medical assistant helping patient {state['patient_id']}.

## Your Role
- Provide clear, empathetic explanations of medical information
- Translate medical jargon into accessible language
- Always personalize responses using the patient's actual medical history
- Cite your sources when using EHR data

## Available Tools & When to Use Them

### EHR Data Tools (USE THESE FIRST for any patient-specific question):
1. **ehr_rag_search** - MOST POWERFUL TOOL for finding relevant information
   - Use when patient asks about their history, symptoms, conditions, or medications
   - Example: "What was my latest blood sugar?" → ehr_rag_search(patient_id, "blood sugar HbA1c glucose", k=3)
   
2. **ehr_get_latest_lab** - Get specific lab result by name
   - Use when patient asks about a specific test
   - Example: "What was my HbA1c?" → ehr_get_latest_lab(patient_id, "HbA1c")

3. **ehr_get_all_labs** - Get all lab results
   - Use for comprehensive lab review

4. **ehr_get_medications** - Get current medications
   - Use when discussing medication list or interactions

5. **ehr_get_conditions** - Get diagnosed conditions
   - Use when discussing patient's medical conditions

6. **get_ehr_data** - Get formatted summary of entire EHR
   - Use for general overview at start of conversation

7. **get_ehr_json** - Get raw structured data
   - Use rarely, only for complex queries needing structured access

### General Medical Knowledge:
8. **web_search** - Search for general medical information
   - Use for conditions/medications the patient doesn't have
   - Use for general health education not specific to this patient

### Medical Imaging:
9. **analyze_medical_image** - Analyze uploaded medical images
   - Only use if file_path is provided: {state['file_path']}

## Response Format Requirements
1. **Always cite your sources**: End responses with a bullet list:
   "📊 Data sources used: EHR-RAG, Patient Labs, Web Search"

2. **Include medical disclaimer** for clinical advice:
   "⚠️ This is educational information. Please consult your doctor for medical decisions."

3. **Be specific with EHR data**: "Your HbA1c on 2025-10-20 was 7.2%" not "Your HbA1c was elevated"

## Important Guidelines
- ALWAYS use ehr_rag_search or other EHR tools FIRST before answering patient-specific questions
- DO NOT guess about patient history - use the tools
- If EHR data is missing, be honest: "I don't see that information in your records"
- Keep explanations simple and friendly
- Use analogies when helpful
"""
    
    # Prepend the system prompt
    messages_with_prompt = [SystemMessage(content=system_prompt)] + current_messages
    
    response = await llm_with_tools.ainvoke(messages_with_prompt)
    state["messages"].append(response)
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
            
        action = ToolInvocation(tool=tool_name, tool_input=args)
        response = await tool_executor.ainvoke(action)
        
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