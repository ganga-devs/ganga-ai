from llama_index.llms.ollama import Ollama
from llama_index.core.base.llms.types import ChatMessage, ChatResponse
from typing import List
from llama_index.core.memory import ChatMemoryBuffer

def generate_response(user_input: str, system_prompt: str, history: List[ChatMessage], model_name: str, index = None) -> str:
    llm = Ollama(model=model_name, request_timeout=300)
    memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
    if index:
        chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=memory,
        system_prompt=(system_prompt))
        result = chat_engine.chat(user_input)
        return result.response or ""
    else:
        result = llm.chat(history)
        return result.message.content or ""
