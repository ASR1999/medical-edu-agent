import os
import torch
from faster_whisper import WhisperModel
from app.config import ASR_MODEL_PATH, ASR_DEVICE, ASR_COMPUTE_TYPE

MODEL_PATH = ASR_MODEL_PATH
DEVICE = ASR_DEVICE


class ASRService:
    def __init__(self):
        try:
            self.model = WhisperModel(MODEL_PATH, device=DEVICE, compute_type=ASR_COMPUTE_TYPE)
            print(f"✅ ASR Service: Loaded model from {MODEL_PATH} on {DEVICE} ({ASR_COMPUTE_TYPE})")
        except Exception as e:
            print(f"❌ Error loading ASR model from {MODEL_PATH}: {e}")
            print(f"   Please ensure the CT2 model exists at this path")
            print(f"   Run: cd ml-training && ./convert_to_ct2.sh")
            self.model = None

    def transcribe(self, audio_file_path: str) -> str:
        if self.model is None:
            return "Error: ASR model not loaded. Please convert and configure the model."

        try:
            print(f"🎤 ASR Service: Transcribing audio file: {audio_file_path}")
            segments, info = self.model.transcribe(
                audio_file_path,
                language="en",
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            text_parts = []
            for segment in segments:
                if segment.text:
                    text_parts.append(segment.text.strip())
            
            transcription = " ".join(text_parts).strip()
            print(f"📝 ASR Transcription: {transcription}")
            return transcription or ""
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return f"Error: {e}"


# Singleton instance
asr_service = ASRService()