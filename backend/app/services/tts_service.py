import requests
import os

# Cartesia API Configuration
CARTESIA_API_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", "sk_car_zENPDUAdKvqwFJM6BMgEZ9")
CARTESIA_VERSION = "2025-04-16"
OUTPUT_DIR = "app/api/generated_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TTSService:
    def __init__(self):
        self.api_url = CARTESIA_API_URL
        self.api_key = CARTESIA_API_KEY
        self.version = CARTESIA_VERSION
        print(f"TTS Service: Initialized Cartesia API client")

    def synthesize(self, text: str, output_filename: str = "response.wav") -> str:
        """
        Synthesize speech from text using Cartesia API.
        
        Args:
            text: The text to synthesize
            output_filename: Name of the output audio file
            
        Returns:
            Path to the generated audio file, or error message string
        """
        if not text or not text.strip():
            return "Error: Text cannot be empty."

        output_path = os.path.join(OUTPUT_DIR, output_filename)

        try:
            print(f"TTS Service: Synthesizing text using Cartesia API...")
            
            # Prepare request payload
            payload = {
                "model_id": "sonic-3",
                "transcript": text,
                "voice": {
                    "mode": "id",
                    "id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b"
                },
                "output_format": {
                    "container": "wav",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100
                },
                "speed": "normal",
                "generation_config": {
                    "speed": 1,
                    "volume": 1
                }
            }
            
            # Prepare headers
            headers = {
                "Cartesia-Version": self.version,
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"Cartesia API error: {response.status_code} - {response.text}"
                print(f"TTS Service: {error_msg}")
                return f"Error: {error_msg}"
            
            # Save audio file
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"TTS Service: Saved audio to {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during TTS synthesis: {e}"
            print(f"TTS Service: {error_msg}")
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error during TTS synthesis: {e}"
            print(f"TTS Service: {error_msg}")
            return f"Error: {error_msg}"

# Singleton instance
tts_service = TTSService()