from llama_index.llms.ollama import Ollama
from llama_index.core.base.llms.types import ChatMessage, ChatResponse
from typing import List


def generate_response(context: List[ChatMessage]) -> ChatResponse:
    llm = Ollama(model="tinyllama", request_timeout=300)
    result = llm.chat(context)
    return result
