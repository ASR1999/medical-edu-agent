import os
from datasets import Audio, Dataset

# --- 1. Load your raw data ---
# This step is CUSTOM. You must adapt this to load your specific data.
# Let's assume you have a folder '/data' with 'audio/' and 'transcripts.json'
# transcripts.json looks like: {"file1.wav": "transcription...", "file2.wav": "transcription..."}
import json

data_dir = "data"
audio_dir = os.path.join(data_dir, "audio")
metadata_path = os.path.join(data_dir, "transcripts.json")

with open(metadata_path, 'r') as f:
    metadata = json.load(f)

data = []
for filename, transcription in metadata.items():
    audio_path = os.path.join(audio_dir, filename)
    if os.path.exists(audio_path):
        data.append({"audio": audio_path, "sentence": transcription})

# Create a Hugging Face Dataset
dataset = Dataset.from_list(data)

# --- 2. Pre-process the dataset ---
from transformers import WhisperProcessor

MODEL_NAME = "openai/whisper-medium"
processor = WhisperProcessor.from_pretrained(MODEL_NAME, language="english", task="transcribe")

# Resample audio to 16kHz
dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))

def prepare_dataset(batch):
    # load and resample audio data from 48 to 16kHz
    audio = batch["audio"]

    # compute log-Mel input features from input audio array 
    batch["input_features"] = processor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]

    # encode target text to label ids 
    batch["labels"] = processor.tokenizer(batch["sentence"]).input_ids
    return batch

print("Processing dataset...")
dataset = dataset.map(prepare_dataset, remove_columns=dataset.column_names, num_proc=2)

# Split into train and test
dataset = dataset.train_test_split(test_size=0.1)

print("Saving processed dataset to disk...")
dataset.save_to_disk("processed_medical_speech_dataset")

print("Done!")
print(dataset)