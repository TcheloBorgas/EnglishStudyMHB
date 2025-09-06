
"""Global configuration and constants."""
from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

APP_TITLE = "🎧 English Trainer — 3K Words"
APP_ICON = "🎧"
WORD_LIMIT = 5
SUPPORTED_VOICES = ["alloy", "verse", "sage", "aria", "ember"]
TTS_FORMAT = "mp3"

@dataclass(frozen=True)
class Paths:
    root: Path
    data: Path
    words_file: Path
    state_file: Path
    audio_cache: Path

def build_paths(project_root: Path) -> Paths:
    data_dir = project_root / "data"
    return Paths(
        root=project_root,
        data=data_dir,
        words_file=data_dir / "top_3000_words.txt",
        state_file=data_dir / "word_state.json",
        audio_cache=data_dir / "audio_cache",
    )

def get_openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return key

def configure_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="centered")
