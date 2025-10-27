from MeloTTS.melo.api import TTS
import soundfile as sf
import os
import torch

# Speed for speech
SPEED = 1.0
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_DIR = "app/api/generated_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TTSService:
    def __init__(self):
        try:
            self.model = TTS(language='EN', device=DEVICE)
            self.speaker_ids = self.model.hps.data.spk2id
            print(f"TTS Service: Loaded MeloTTS model on {DEVICE}")
        except Exception as e:
            print(f"Error loading TTS model: {e}")
            self.model = None

    def synthesize(self, text: str, output_filename: str = "response.wav") -> str:
        if self.model is None:
            return "Error: TTS model not loaded."

        output_path = os.path.join(OUTPUT_DIR, output_filename)

        try:
            print("TTS Service: Synthesizing...")
            self.model.tts_to_file(
                text, 
                self.speaker_ids['EN-US'], # Using a standard US speaker
                output_path, 
                speed=SPEED
            )
            print(f"TTS Service: Saved audio to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error during TTS synthesis: {e}")
            return f"Error: {e}"

# Singleton instance
tts_service = TTSService()