import torch
from peft import PeftModel
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from ctranslate2.converters.transformers import TransformersConverter

MODEL_NAME = "openai/whisper-medium"
LORA_ADAPTER_PATH = "whisper-medium-medical-lora" # Path from step 2
MERGED_MODEL_PATH = "whisper-medium-medical-merged"
CT2_MODEL_PATH = "../../backend/ct2_models/whisper-medium-med" # Final path

# --- 1. Load Base Model ---
print("Loading base model...")
base_model = WhisperForConditionalGeneration.from_pretrained(
    MODEL_NAME, 
    torch_dtype=torch.float16, 
    device_map="auto"
)

# --- 2. Merge LoRA Adapters ---
print(f"Loading LoRA adapters from {LORA_ADAPTER_PATH}...")
peft_model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)
print("Merging model...")
merged_model = peft_model.merge_and_unload()

# --- 3. Save Merged HF Model ---
print(f"Saving merged Hugging Face model to {MERGED_MODEL_PATH}...")
merged_model.save_pretrained(MERGED_MODEL_PATH)

# Save the processor as well
processor = WhisperProcessor.from_pretrained(MODEL_NAME, language="english", task="transcribe")
processor.save_pretrained(MERGED_MODEL_PATH)
print("Merged model saved.")

# --- 4. Convert to CTranslate2 ---
print(f"Converting merged model to CTranslate2 format...")
converter = TransformersConverter(
    model_name_or_path=MERGED_MODEL_PATH,
    copy_files=["config.json", "preprocessor_config.json", "vocab.json", "merges.txt"],
    output_dir=CT2_MODEL_PATH,
    quantization="float16" # Use float16 for good speed/accuracy balance
)
converter.convert()

print(f"CTranslate2 model saved to {CT2_MODEL_PATH}")
print("ASR model pipeline complete. 🚀")