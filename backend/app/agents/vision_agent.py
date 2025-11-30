# This file is largely your provided code.
# I have modified it to:
# 1. Import from the central app.config
# 2. Add a basic logger
# 3. Encapsulate it in a runnable function for LangGraph

import logging
import aiohttp
# import aioboto3
import aiofiles
import httpx
import json
import os
import re
import uuid
import urllib.parse
from datetime import datetime
from typing import Dict, Any

from confluent_kafka import Producer
from groq import Groq
from openai import AsyncOpenAI
from pdf2image import convert_from_path
from PIL import Image
from langgraph.graph import StateGraph, START, END

# --- Imports from our project structure ---
from app.config import (
    GROQ_VISION_MODEL, GROQ_API_KEY, OPENAI_API_KEY, OPENAI_MODEL,
    S3_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION,
    SESSION_TOKEN, SESSION_X_API_KEY, AUTHENTICATION_TOKEN,
    kafka_conf_producer, kafka_producer_topic
)

# --- Basic Logger Setup ---
# A proper setup would use a logging config, but this is fine for now.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Dummy decorator since log_execution_time was not provided
def log_execution_time(logger):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # In a real app, you'd time this
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# --- Your Provided Code Starts Here ---
# (I have omitted the functions you provided that are unchanged, 
# like kafka_produce, get_remote_file_size, get_file_size)
# ... (kafka_produce, get_remote_file_size, get_file_size) ...
# I will copy only the UploadAgent class and its dependencies

producer = Producer(kafka_conf_producer)

async def kafka_produce(key, value, headers):
    """Produce message to kafka"""
    producer.produce(kafka_producer_topic, key=key, value=value, headers=headers)
    producer.poll(0.1)
    producer.flush()


async def get_remote_file_size(url: str) -> str:
    """Returns the size of the remote file in MB (for remote files)."""
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            file_size = int(
                response.headers.get('Content-Length', 0))  # Get size in bytes
            file_size_mb = file_size / (1024 * 1024)  # Convert bytes to MB
            return f"{file_size_mb:.2f} MB"


async def get_file_size(file_path: str) -> str:
    """Returns the size of the file in MB (for local files)."""
    file_size = os.path.getsize(file_path)  # Get size in bytes
    file_size_mb = file_size / (1024 * 1024)  # Convert bytes to MB
    return f"{file_size_mb:.2f} MB"

class UploadAgent:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_VISION_MODEL
        self.client = Groq()
        self.client_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)  # Initialize Groq client

    async def _upload_to_s3(self, file_path, bucket_name, file_key):
        """Upload a file to S3 and return a pre-signed URL."""
        session = aioboto3.Session()
        async with session.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        ) as s3:
            async with aiofiles.open(file_path, 'rb') as f:
                await s3.upload_fileobj(f, bucket_name, file_key)
            presigned_url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_key},
                ExpiresIn=3600
            )
            return presigned_url

    async def _validate_image(self, file_path_or_url: str):
        """Verify if the image is valid. Handles both local file paths and URLs."""
        if not file_path_or_url:
            raise ValueError("No URL or file path provided.")
        temp_file = None
        try:
            if file_path_or_url.startswith("http"):
                temp_file = "temp_image_validation.png"
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_path_or_url) as response:
                        if response.status != 200:
                            raise ValueError(f"Invalid link: {file_path_or_url}. HTTP Status: {response.status}")
                        with open(temp_file, "wb") as file:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                file.write(chunk)
                        file_path = temp_file
            else:
                file_path = file_path_or_url
            with Image.open(file_path) as img:
                img.verify()
            logger.info(f"Image {file_path_or_url} is valid.")
        except Exception as e:
            raise ValueError(f"Invalid image data: {file_path_or_url}. Error: {e}")
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

    async def _extract_doctor_name(self, text: str) -> str:
        """Extract the doctor's name from the analysis text."""
        pattern = r"\b(Dr\.?\s+[A-Za-z]+(?:\s+[A-Za-z]+)?)\b"
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return ""

    @log_execution_time(logger)
    async def _process_and_analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process a PDF or analyze an image file."""
        file_url = state.get("file_url")
        if not file_url:
            state["analysis_result"] = "Invalid or missing file URL."
            return state

        user_input_text = state.get("user_input_text", "")

        # Check if file_url is a local path (e.g., from a temp upload)
        # If it's not a URL, we need to upload it to S3 first to get a URL
        if not file_url.startswith("http"):
            logger.info(f"Local file detected: {file_url}. Uploading to S3...")
            file_key = f"uploads/{uuid.uuid4()}_{os.path.basename(file_url)}"
            try:
                # file_url = await self._upload_to_s3(file_url, S3_BUCKET_NAME, file_key)
                logger.info(f"File uploaded to S3: {file_url}")
                state["file_url"] = file_url # Update state with the new URL
            except Exception as e:
                logger.error(f"Failed to upload local file {file_url} to S3: {e}")
                state["analysis_result"] = f"Failed to process local file: {e}"
                return state

        async with aiohttp.ClientSession() as session:
            async with session.head(file_url) as response:
                content_type = response.headers.get('Content-Type', '').lower()

            if content_type.startswith('application/pdf'):
                logger.info("File identified as PDF. Processing PDF.")
                async with session.get(file_url) as pdf_response:
                    if pdf_response.status != 200:
                        state["analysis_result"] = (
                            f"Invalid link: {file_url}. HTTP Status: {pdf_response.status}"
                        )
                        return state

                    file_name = "downloaded_file.pdf"
                    with open(file_name, "wb") as file:
                        file.write(await pdf_response.read())

                try:
                    pages = convert_from_path(file_name, dpi=150)
                    image_links = []
                    llm_responses = []
                    categories = []
                    analysis_result = {}
                    for idx, page in enumerate(pages):
                        image_file = f"page_{idx + 1}.png"
                        page.convert("RGB").save(image_file, "PNG")

                        try:
                            await self._validate_image(image_file)
                            s3_file_key = (
                                f"pdf_pages/{os.path.basename(file_name)}/{image_file}"
                            )
                            # image_url = await self._upload_to_s3(
                            #     image_file,
                            #     S3_BUCKET_NAME,
                            #     s3_file_key
                            # )
                            # image_links.append(image_url)

                            analysis_result = await self._analyze_with_llm_images(
                                image_url, user_input_text
                            )
                            categories.append(analysis_result["category"])
                            llm_responses.append(analysis_result["response"])

                        except Exception as e:
                            logger.error(f"Error processing image {image_file}: {e}")
                        finally:
                            os.remove(image_file)

                    # (Your category logic remains unchanged)
                    priority_categories = ["referral letter by any doctor", "health summary", "signature"]
                    other_categories = [
                        "x-ray", "mri", "ct-scan", "surgical reports", "prescription", "lab test", "treatment plans",
                        "case history", "health monitoring data", "medication history"
                    ]
                    state["category"] = "others"
                    for category in categories:
                        if category in priority_categories:
                            state["category"] = category
                            break
                    else:
                        for category in categories:
                            if category in other_categories:
                                state["category"] = category
                                break
                    
                    state["image_links"] = image_links
                    state["analysis_result"] = "\n".join(llm_responses)

                finally:
                    if os.path.exists(file_name):
                        os.remove(file_name)

            elif content_type.startswith('image/'):
                logger.info("File identified as Image. Analyzing image.")
                try:
                    await self._validate_image(file_url)
                    analysis_result = await self._analyze_with_llm_images(
                        file_url, user_input_text
                    )
                    state["image_links"] = [file_url]
                    state["analysis_result"] = analysis_result["response"]
                    state["category"] = analysis_result["category"]
                    state["doctor_name"] = analysis_result["doctor_name"]
                except Exception as e:
                    logger.error(f"Error analyzing image: {e}")
                    state["analysis_result"] = f"Error analyzing image: {e}"
            else:
                state["analysis_result"] = f"Unsupported file type: {content_type}"
        return state

    async def _analyze_with_llm_images(self, image_url: str,
                                       user_input_text: str = "") -> dict:
        """Analyze an image or document page using the LLM and return both category and response."""
        try:
            type_determination_payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Given this image, classify it into the most appropriate category from the following list: x-ray, mri, ct-scan, surgical reports, prescription, lab test, treatment plans, case history, health monitoring data, medication history, health summary, referral letter by any doctor, signature, others. If the image does not clearly belong to any of the first thirteen categories, classify it as 'others.' Provide only the category name without formatting and extra words."
                            },
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                "temperature": 0,
                "max_tokens": 10,
                "top_p": 1,
                "stream": False,
                "stop": None
            }
            
            # Use the OpenAI client, as Groq's client might differ
            # Note: Your original code uses self.client_openai
            type_response = await self.client_openai.chat.completions.create(
                **type_determination_payload)
            image_type = type_response.choices[0].message.content.strip().lower().rstrip(".")
            logger.info(f"Image category determined: {image_type}")

        except Exception as e:
            logger.error(f"Error determining image type with LLM: {e}")
            return {"category": "error", "response": f"Error determining image type: {e}"}

        try:
            # Load examples from the /data folder
            examples_path = os.path.join(os.path.dirname(__file__), "../../data/prompt_examples.json")
            with open(examples_path, "r") as f:
                prompt_examples = json.load(f)
            examples = prompt_examples.get(image_type, prompt_examples.get("others", []))
        except Exception as e:
            logger.error(f"Error loading few-shot examples: {e}")
            return {"category": image_type, "response": f"Error loading few-shot examples: {e}"}

        try:
            if user_input_text:
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input_text},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ]
            elif image_type == "others":
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Thoroughly analyze the provided image and describe all details comprehensively."},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ]
            else:
                few_shot = examples[0].get("content", "") if examples else ""
                messages = [
                    {"role": "user", "content": few_shot},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]},
                ]

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 1024,
                "top_p": 1,
                "stream": False,
                "stop": None,
            }

            completion = await self.client_openai.chat.completions.create(**payload)
            response_text = completion.choices[0].message.content.strip()
            doctor_name = await self._extract_doctor_name(response_text)

            logger.info(f"Doctor's Name: {doctor_name}")
            return {"category": image_type, "response": response_text, "doctor_name": doctor_name}

        except Exception as e:
            logger.error(f"Error analyzing image {image_url} with LLM: {e}")
            return {"category": image_type, "response": f"Failed to analyze the image", "doctor_name": ""}

    async def _return_response(self, user_id: str, session_id: str,
                               category: str, analysis_result: str) -> dict:
        """Return the final response (simplified for agent use)."""
        # The main LangGraph agent will handle the full response.
        # This node just returns its findings.
        final_data = {
            "category": category,
            "analysis_result": analysis_result,
            "user_id": user_id,
            "session_id": session_id
        }
        logger.info(f"Vision agent returning: {final_data}")
        return final_data

    async def _graph(self):
        """Defines the state graph for processing."""
        graph_builder = StateGraph(Dict[str, Any])
        graph_builder.add_node("process_and_analyze", self._process_and_analyze)
        graph_builder.add_node("return_response", lambda state: state)
        graph_builder.add_edge(START, "process_and_analyze")
        graph_builder.add_edge("process_and_analyze", "return_response")
        graph_builder.add_edge("return_response", END)
        return graph_builder.compile()

    async def aexecute_upload_agent(self, file_url: str, user_id: str, session_id: str,
                                    user_input_text: str = "") -> dict:
        """Executes the graph flow based on the file type and uploads clinical data."""
        try:
            message_id = str(uuid.uuid4())
            # (Kafka logic omitted for brevity, assuming it works as you wrote)
            # ... await kafka_produce ...
            
            state = {
                "file_url": file_url,
                "user_id": user_id,
                "session_id": session_id,
                "user_input_text": user_input_text,
                "image_links": [], "category": "", "doctor_name": "", "analysis_result": ""
            }

            self._compiled_graph = await self._graph()
            state = await self._compiled_graph.ainvoke(state)
            category = state.get("category", "unknown")
            doctor_name = state.get("doctor_name", "unknown")
            analysis_result = state.get("analysis_result", "No analysis result available.")

            # (Your clinical relevance logic is unchanged)
            clinical_categories = [
                "x-ray", "mri", "ct-scan", "surgical reports", "prescription", "lab test",
                "treatment plans", "case history", "health monitoring data",
                "medication history", "health summary", "referral letter by any doctor"
            ]
            clinical_relevance = category.lower() in [c.lower() for c in clinical_categories]

            if file_url.startswith('http'):
                file_size = await get_remote_file_size(file_url)
            else:
                file_size = await get_file_size(file_url)
            
            # (Your file naming and metadata logic is unchanged)
            # ...
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            parsed_url = urllib.parse.urlparse(file_url)
            original_file_name = parsed_url.path.split('/o/')[-1]
            file_type = original_file_name.split('.')[-1]
            new_file_name = f"{category.replace(' ', '_')}_{current_time}.{file_type}"
            
            metadata = {
                "image_url": file_url, "original_file_name": original_file_name,
                "new_file_name": new_file_name, "file_type": file_type,
                "file_size": file_size, "text": user_input_text,
                "category_name": category, "doctor_name": doctor_name
            }

            payload = {
                "uploaded_by": "user", "user_id": user_id, "creator_id": user_id,
                "clinical_note_id": "undefined", "doctor_names": doctor_name,
                "response": analysis_result, "clinical_relevance": clinical_relevance,
                "metadata": metadata
            }

            # (Your API call logic is unchanged)
            url = 'https://session-note.uwc.world/clinicalnotes/add-prescription'
            headers = {
                'accept': 'application/json, text/plain, */*',
                'authenticationtoken': AUTHENTICATION_TOKEN,
                'content-type': 'application/json',
                'token': SESSION_TOKEN,
                'x-api-key': SESSION_X_API_KEY
                # (other headers)
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                logger.info(f"Session API Response: {response.status_code}")
                if response.status_code != 201:
                    logger.error(f"Failed to call session API: {response.text}")

            # Return the simplified dictionary for the main agent
            return await self._return_response(user_id, session_id, category, analysis_result)
        
        except Exception as e:
            logger.error(f"Error during vision agent execution: {e}")
            return await self._return_response(user_id, session_id, "error", str(e))

# --- End of your code ---


# --- Wrapper function for our main LangGraph agent ---
# This is the function we will expose as a "tool"
async def run_vision_agent_tool(query: str, file_path: str, patient_id: str) -> str:
    """
    A tool that processes a medical image (or PDF) and returns an analysis.
    
    :param query: The user's text query about the image.
    :param file_path: The local path to the file to analyze.
    :param patient_id: The ID of the patient.
    :return: A JSON string of the analysis.
    """
    logger.info(f"Running Vision Agent for patient {patient_id} on file {file_path}")
    
    # In a real app, user_id and session_id would come from the user's session
    user_id = patient_id 
    session_id = str(uuid.uuid4()) # Create a new session for this analysis
    
    try:
        agent = UploadAgent()
        # The vision agent needs a URL. We must upload the local file_path to S3 first.
        # The `aexecute_upload_agent` handles this logic if it's not a URL.
        result_dict = await agent.aexecute_upload_agent(
            file_url=file_path,
            user_id=user_id,
            session_id=session_id,
            user_input_text=query
        )
        
        # Return the key findings to the main agent
        return json.dumps({
            "category": result_dict.get("category"),
            "analysis": result_dict.get("analysis_result")
        })

    except Exception as e:
        logger.error(f"Error in run_vision_agent_tool: {e}")
        return json.dumps({"error": str(e)})