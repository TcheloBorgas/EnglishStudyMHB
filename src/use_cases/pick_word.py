
import random
from typing import Dict, Iterable, List, Set

class WordPicker:
    def __init__(self, max_count: int) -> None:
        self._max = max_count

    def pick(self, words: Iterable[str], counts: Dict[str, int], restricted: Iterable[str]) -> str | None:
        rest: Set[str] = set(restricted)
        candidates: List[str] = [w for w in words if w not in rest]
        if not candidates:
            return None
        weights = [1.0 / (counts.get(w, 0) + 1) for w in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]

    def update_counts(self, word: str, counts: Dict[str, int]) -> int:
        new_val = counts.get(word, 0) + 1
        counts[word] = new_val
        return new_val

    def should_restrict(self, count_value: int) -> bool:
        return count_value >= self._max
