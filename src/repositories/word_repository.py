from pathlib import Path
from typing import List

class WordRepository:
    def __init__(self, words_file: Path) -> None:
        self._words_file = words_file

    def load_words(self) -> List[str]:
        if not self._words_file.exists():
            raise FileNotFoundError(f"Words file not found: {self._words_file}")
        words: List[str] = []
        with self._words_file.open("r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if w and w.isalpha():
                    words.append(w)
        seen = set()
        unique_words: List[str] = []
        for w in words:
            if w not in seen:
                seen.add(w)
                unique_words.append(w)
        return unique_words
