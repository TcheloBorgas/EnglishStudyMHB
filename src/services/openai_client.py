
from openai import OpenAI

class OpenAIClientFactory:
    @staticmethod
    def create(api_key: str) -> OpenAI:
        return OpenAI(api_key=api_key)
