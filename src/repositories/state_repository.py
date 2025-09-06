
import json
from pathlib import Path
from typing import Dict, List, Tuple

class StateRepository:
    def __init__(self, state_file: Path) -> None:
        self._state_file = state_file

    def load(self) -> Tuple[Dict[str, int], List[str]]:
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                counts = data.get("counts", {})
                restricted = data.get("restricted", [])
                return counts, restricted
            except Exception:
                pass
        return {}, []

    def save(self, counts: Dict[str, int], restricted: List[str]) -> None:
        payload = {"counts": counts, "restricted": sorted(list(set(restricted)))}
        self._state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
