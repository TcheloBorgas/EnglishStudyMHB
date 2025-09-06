
import json
from openai import OpenAI
from src.domain.models import ExamplePair

SYSTEM_PROMPT = (
    "You are an English teacher. "
    "Write simple, natural American English for A2–B1 learners. "
    "Keep it short and avoid rare words."
)

USER_TEMPLATE = (
    "Target word: '{target}'.\n"
    "1) Give ONE example sentence that naturally includes the target word.\n"
    "2) Then, give ONE short question that prompts the student to reply using that word.\n"
    "Return JSON with keys: sentence, question. Do not add extra text."
)

class GeneratorService:
    """
    Gera (sentence, question) usando Chat Completions (JSON mode),
    compatível com versões do SDK que não suportam 'response_format' na Responses API.
    """

    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = client
        self._model = model

    def generate_pair(self, target_word: str) -> ExamplePair:
        user_prompt = USER_TEMPLATE.format(target=target_word)
        chat = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            # JSON mode garante um objeto JSON no 'message.content'
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        content = chat.choices[0].message.content

        # Parse robusto (com fallback simples se vier algo estranho)
        try:
            data = json.loads(content)
        except Exception:
            # fallback ingênuo: tenta extrair objeto JSON bruto entre { }
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and start < end:
                data = json.loads(content[start:end+1])
            else:
                raise ValueError(f"Modelo não retornou JSON válido: {content!r}")

        sentence = (data.get("sentence") or "").strip()
        question = (data.get("question") or "").strip()
        if not sentence or not question:
            raise ValueError(f"Campos ausentes no JSON: {data}")

        return ExamplePair(sentence=sentence, question=question)
