# from IPython import get_ipython

from llama_index.llms.ollama.base import ChatMessage


class Context:
    def __init__(self):
        # This is a list of the form list[ChatMessaage]
        # ChatMessaage is a typed tuple
        # Eg, 
        # ChatMessage( role="system", content="You are a pirate with a colorful personality"),
        # ChatMessage(role="user", content="What is your name"),
        self._context: list[ChatMessage] = []
        
    #TODO: complete this function
    # def initial_context(self) -> None:
    #     ipython = get_ipython()
    #     ipython_session_history = ipython.history_manager
    #     context_window_stop = ipython.execution_count
    #     context_window_start = context_window_stop - 5 
    #     return
        
    def add_user_msg_to_context(self, message: str) -> None:
        self._context.append(ChatMessage(role="user", content=message))
        return

    def add_system_msg_to_context(self, message: str) -> None:
        self._context.append(ChatMessage(role="system", content=message))

    def get_contxt(self):
        return self._context
