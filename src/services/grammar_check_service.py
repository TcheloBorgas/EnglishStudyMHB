import json
from typing import List
from openai import OpenAI
from src.domain.models import GrammarFeedback

SYSTEM_PROMPT = (
    "You are an English teacher for A2–B1 learners. "
    "Evaluate grammar and naturalness BRIEFLY. "
    "Be concise and practical. Keep suggestions short and simple."
)

USER_TEMPLATE = (
    "Target word: '{target}'.\n"
    "Student answer: '''{answer}'''\n\n"
    "Evaluate if the sentence is acceptable for an A2–B1 learner.\n"
    "- Return JSON ONLY with keys: ok (boolean), score (number 0-5), issues (array of short strings), corrected (string short natural fix).\n"
    "- 'ok' should be true if the answer is understandable and reasonably correct.\n"
    "- 'corrected' must include the target word and be a single sentence."
)

class GrammarCheckService:
    """
    Avalia a resposta do aluno (gramática e naturalidade) e retorna um feedback estruturado.
    Usa Chat Completions em JSON mode para máxima compatibilidade.
    """

    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = client
        self._model = model

    def check(self, answer: str, target_word: str) -> GrammarFeedback:
        user_prompt = USER_TEMPLATE.format(target=target_word, answer=answer)
        chat = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = chat.choices[0].message.content
        data = json.loads(content)

        ok = bool(data.get("ok", False))
        score = float(data.get("score", 0.0))
        issues: List[str] = list(data.get("issues", [])) if isinstance(data.get("issues", []), list) else []
        corrected = (data.get("corrected") or "").strip()

        return GrammarFeedback(ok=ok, score=score, issues=issues, corrected=corrected)
