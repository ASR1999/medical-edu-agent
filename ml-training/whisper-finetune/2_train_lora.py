import torch
from datasets import load_from_disk
from transformers import WhisperForConditionalGeneration, WhisperProcessor, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# --- 1. Load Model and Processor ---
MODEL_NAME = "openai/whisper-medium"
OUTPUT_DIR = "whisper-medium-medical-lora"
DATASET_PATH = "processed_medical_speech_dataset"

processor = WhisperProcessor.from_pretrained(MODEL_NAME, language="english", task="transcribe")
model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME, load_in_8bit=True)

# Prepare model for 8-bit training
model = prepare_model_for_kbit_training(model)

# --- 2. Configure LoRA ---
lora_config = LoraConfig(
    r=8, 
    lora_alpha=32, 
    target_modules=["q_proj", "v_proj"], 
    lora_dropout=0.05, 
    bias="none"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# --- 3. Data Collator ---
from transformers.models.whisper.modeling_whisper import WhisperForConditionalGeneration_forward
import dataclasses

@dataclasses.dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: any
    def __call__(self, features):
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]
        batch["labels"] = labels
        return batch

data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

# --- 4. Load Dataset ---
dataset = load_from_disk(DATASET_PATH)

# --- 5. Training ---
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=2,
    learning_rate=1e-5,
    warmup_steps=50,
    num_train_epochs=3,
    evaluation_strategy="steps",
    eval_steps=100,
    save_steps=100,
    logging_steps=25,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    fp16=True,
    report_to=["tensorboard"],
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    data_collator=data_collator,
    tokenizer=processor.feature_extractor,
)

print("Starting training...")
trainer.train()

print(f"Saving LoRA adapters to {OUTPUT_DIR}")
model.save_pretrained(OUTPUT_DIR)