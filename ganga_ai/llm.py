from llama_index.llms.ollama import Ollama
from llama_index.core.base.llms.types import ChatMessage, ChatResponse
from typing import List


def generate_response(context: List[ChatMessage], model_name: str) -> ChatResponse:
    llm = Ollama(model=model_name, request_timeout=300)
    result = llm.chat(context)
    return result
