
from pathlib import Path
import hashlib
import requests

class TTSService:
    def __init__(self, api_key: str, cache_dir: Path, model: str = "gpt-4o-mini-tts", fmt: str = "mp3") -> None:
        self._api_key = api_key
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = model
        self._fmt = fmt

    def _key(self, text: str, voice: str) -> str:
        raw = f"{voice}::{text}".encode("utf-8")
        return hashlib.sha1(raw).hexdigest() + f".{self._fmt}"

    def synthesize(self, text: str, voice: str) -> Path:
        filename = self._key(text, voice)
        path = self._cache_dir / filename
        if not path.exists():
            url = "https://api.openai.com/v1/audio/speech"
            headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
            payload = {"model": self._model, "voice": voice, "input": text, "format": self._fmt}
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            path.write_bytes(r.content)
        return path
