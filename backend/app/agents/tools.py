import json
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.utilities.serpapi import SerpAPIWrapper

from app.config import GROQ_API_KEY, SERPER_API_KEY
from app.services.ehr_provider_factory import get_ehr_provider

# Get the configured EHR provider (mock or FHIR)
ehr_provider = get_ehr_provider()

# ==================== EHR Retrieval Tools ====================

@tool
def get_ehr_data(patient_id: str) -> str:
    """
    Fetches a comprehensive, human-readable summary of the patient's Electronic Health Record (EHR).
    This includes demographics, conditions, medications, recent labs, and doctor's notes.
    Use this as your primary source of patient-specific information.
    
    Args:
        patient_id: The unique identifier for the patient
        
    Returns:
        Multi-line formatted summary of the patient's medical history
    """
    print(f"[TOOL] get_ehr_data: Fetching EHR summary for patient {patient_id}")
    return ehr_provider.get_summary(patient_id)


@tool
def get_ehr_json(patient_id: str) -> str:
    """
    Returns the complete EHR data as a JSON string.
    Use this when you need to access specific structured data fields or perform
    detailed analysis of the raw medical data.
    
    Args:
        patient_id: The unique identifier for the patient
        
    Returns:
        JSON string containing all EHR data
    """
    print(f"[TOOL] get_ehr_json: Fetching complete EHR JSON for patient {patient_id}")
    data = ehr_provider.get_patient_json(patient_id)
    return json.dumps(data, indent=2)


@tool
def ehr_rag_search(patient_id: str, query: str, k: int = 5) -> str:
    """
    Performs semantic search over the patient's EHR data using RAG (Retrieval-Augmented Generation).
    This is the most powerful tool for finding relevant medical information from the patient's history.
    
    Use this when:
    - The patient asks about specific symptoms, conditions, or treatments
    - You need to find context about a particular medical term or value
    - The patient references something from their history
    
    Args:
        patient_id: The unique identifier for the patient
        query: Natural language query (e.g., "What was my latest blood sugar level?")
        k: Number of relevant passages to retrieve (default: 5)
        
    Returns:
        JSON string with list of relevant EHR passages, each with text, metadata, and relevance score
    """
    print(f"[TOOL] ehr_rag_search: Searching EHR for patient {patient_id} with query: '{query}'")
    
    # Ensure patient is indexed
    try:
        ehr_provider.index_patient(patient_id)
    except Exception as e:
        print(f"[TOOL] Warning: Could not index patient {patient_id}: {e}")
    
    results = ehr_provider.rag_search(patient_id, query, k=k)
    return json.dumps(results, indent=2)


@tool
def ehr_get_latest_lab(patient_id: str, lab_name: str) -> str:
    """
    Retrieves the most recent lab result for a specific test.
    
    Common lab names:
    - HbA1c (diabetes marker)
    - Blood Pressure
    - Cholesterol
    - Glucose
    - Complete Blood Count (CBC)
    
    Args:
        patient_id: The unique identifier for the patient
        lab_name: Name of the lab test
        
    Returns:
        JSON string with lab result details or empty object if not found
    """
    print(f"[TOOL] ehr_get_latest_lab: Fetching '{lab_name}' for patient {patient_id}")
    result = ehr_provider.get_latest_lab(patient_id, lab_name)
    return json.dumps(result if result else {})


@tool
def ehr_get_all_labs(patient_id: str) -> str:
    """
    Retrieves all lab results for a patient.
    
    Args:
        patient_id: The unique identifier for the patient
        
    Returns:
        JSON string with list of all lab results
    """
    print(f"[TOOL] ehr_get_all_labs: Fetching all labs for patient {patient_id}")
    labs = ehr_provider.get_all_labs(patient_id)
    return json.dumps(labs, indent=2)


@tool
def ehr_get_medications(patient_id: str) -> str:
    """
    Retrieves all current medications for a patient.
    Each medication includes name, dosage, and frequency.
    
    Args:
        patient_id: The unique identifier for the patient
        
    Returns:
        JSON string with list of medications
    """
    print(f"[TOOL] ehr_get_medications: Fetching medications for patient {patient_id}")
    meds = ehr_provider.get_medications(patient_id)
    return json.dumps(meds, indent=2)


@tool
def ehr_get_conditions(patient_id: str) -> str:
    """
    Retrieves all diagnosed conditions for a patient.
    Each condition includes name and diagnosis date.
    
    Args:
        patient_id: The unique identifier for the patient
        
    Returns:
        JSON string with list of conditions
    """
    print(f"[TOOL] ehr_get_conditions: Fetching conditions for patient {patient_id}")
    conditions = ehr_provider.get_conditions(patient_id)
    return json.dumps(conditions, indent=2)

# --- 2. Web Search Tool (Serper) ---
@tool
def web_search(query: str) -> str:
    """
    Performs a web search to find general information about medical conditions,
    treatments, or terminology. Use this to answer non-personal medical questions.
    """
    print(f"Tool: Searching web for '{query}'")
    try:
        # SerpAPIWrapper uses the SerpAPI key, not Serper. Reuse the env var for simplicity.
        search = SerpAPIWrapper(serpapi_api_key=SERPER_API_KEY)
        result = search.run(query)
        return result
    except Exception as e:
        print(f"Error in web search: {e}")
        return "Error performing web search."

# --- 3. SOS / Harmful Question Tool ---
# This isn't a "tool" but a router/check we'll use in the graph.
# We define the logic for it here.
llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)
sos_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a medical safety classification agent. Your job is to determine if a user's question is harmful or indicates a medical emergency.
- If the question is about a life-threatening situation, self-harm, or severe distress (e.g., "I can't breathe", "I want to kill myself", "I am having a heart attack"), respond with 'SOS'.
- If the question is rude, offensive, or tries to jailbreak you, respond with 'HARMFUL'.
- For all other normal medical questions (e.g., "What is diabetes?", "Explain my lab results"), respond with 'SAFE'.
Your response must be ONLY ONE WORD: 'SOS', 'HARMFUL', or 'SAFE'.
"""),
    ("user", "{query}")
])
sos_chain = sos_prompt | llm | StrOutputParser()

async def check_for_harmful_intent(query: str) -> str:
    """
    Checks a user query for harmful intent or medical emergencies.
    Returns: 'SOS', 'HARMFUL', or 'SAFE'
    """
    print(f"Tool: Checking query safety: '{query}'")
    response = await sos_chain.ainvoke({"query": query})
    return response.strip().upper()

# --- 4. Vision Tool Wrapper ---
# We import the function from your vision agent file to expose it as a tool
from .vision_agent import run_vision_agent_tool

@tool
async def analyze_medical_image(query: str, file_path: str, patient_id: str) -> str:
    """
    A tool that processes a medical image (or PDF) and returns an analysis.
    Use this when the user uploads a file and asks a question about it.
    
    :param query: The user's text query about the image.
    :param file_path: The local path to the file to analyze. (This will be a temp path)
    :param patient_id: The ID of the patient.
    :return: A JSON string of the analysis.
    """
    return await run_vision_agent_tool(query, file_path, patient_id)

# --- List of all tools for the agent ---
all_tools = [
    get_ehr_data,
    get_ehr_json,
    ehr_rag_search,
    ehr_get_latest_lab,
    ehr_get_all_labs,
    ehr_get_medications,
    ehr_get_conditions,
    web_search,
    analyze_medical_image
]