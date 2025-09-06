from dataclasses import dataclass
from typing import List

@dataclass
class ExamplePair:
    sentence: str
    question: str

@dataclass
class GrammarFeedback:
    ok: bool                 # se a frase está aceitável para A2–B1
    score: float             # 0–5 (maior é melhor)
    issues: List[str]        # lista de problemas encontrados
    corrected: str           # sugestão corrigida (curta e natural)
