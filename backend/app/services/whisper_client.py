import os
import tempfile
from typing import BinaryIO
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"


class WhisperService:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or OPENAI_API_KEY

    def transcribe_audio(self, audio_file: BinaryIO | str) -> str:
        if not self.api_key:
            return ""
        if isinstance(audio_file, str):
            with open(audio_file, "rb") as handle:
                return self._send_request(handle)
        return self._send_request(audio_file)

    def _send_request(self, audio_file) -> str:
        files = {"file": ("audio.wav", audio_file, "audio/wav")}
        data = {"model": "whisper-1", "response_format": "json"}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = httpx.post(WHISPER_URL, headers=headers, files=files, data=data, timeout=60.0)
            response.raise_for_status()
            return response.json().get("text", "")
        except Exception:
            return ""
