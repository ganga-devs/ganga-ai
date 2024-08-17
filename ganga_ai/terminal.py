from llama_index.core.base.llms.types import ChatMessage, ChatResponse
from rich.console import Console
from rich.markdown import Markdown
from IPython.core.getipython import get_ipython
from IPython.core.history import HistoryAccessor

from ganga_ai.config import Config
from ganga_ai.llm import generate_response

"""
This class is responsible for maintaing terminal state and does all the heavy lifting. It exposes apis the magic commands can use.
"""


class Terminal:
    def __init__(self):
        self.console = Console()
        self.config = Config()
        self.context: list[ChatMessage] = []
        self.ipython_instance = get_ipython()
        self.ipython_history_manager = HistoryAccessor()

    def _display_formatted_output(self, rawOutput: str) -> None:
        markdownOutput = Markdown(rawOutput)
        self.console.print(markdownOutput)

    def _add_system_prompt_to_context(self, system_prompt: str) -> None:
        self.context.append(ChatMessage(role="system", content=system_prompt))

    def _add_user_input_to_context(self, user_input: str) -> None:
        self.context.append(ChatMessage(role="user", content=user_input))

    def _add_llm_response_to_context(self, llm_str_response: str) -> None:
        self.context.append(ChatMessage(role="system", content=llm_str_response))

    def _add_error_to_context(self, err_value: str) -> None:
        context: str = (
            "The command ran at the terminal and the error I got from it is\n"
            + err_value
            + "How do I fix it?"
        )
        self.context.append(ChatMessage(role="user", content=context))

    def _trim_context(self, size: int) -> None:
        pass

    def _reset_context(self) -> None:
        self.context.clear()

    def _build_context_for_assists(self, count: int = 5) -> str:
        # Need the session id to be able to extract history of the current session to feed it as context to the llm
        current_ipython_session_id: int = (
            self.ipython_history_manager.get_last_session_id()
        )
        # If current_execution_count is smaller than count starting_count is 1 as current_execution_count - count < 0 in that case
        current_execution_count: int = self.ipython_instance.execution_count
        starting_count = max(current_execution_count - count, 1)
        context: str = (
            "The past few commands ran in the ipython terminal and their outputs are"
        )
        for _, _, (input_text, output_text) in self.ipython_history_manager.get_range(
            session=current_ipython_session_id,
            start=starting_count,
            stop=current_execution_count,
            output=True,
        ):
            if input_text == "%load_ext ganga_ai":
                continue
            elif output_text:
                context += "\nIn:" + input_text + "\nOut:" + output_text
            else:
                context += "\nIn:" + input_text
        return context

    def _handle_initial_error(self, err_value: str) -> None:
        self._display_formatted_output("Processing the error to help you...")
        self._add_error_to_context(err_value)
        llm_json_response: ChatResponse = generate_response(
            context=self.context, model_name=self.config.get_model()
        )
        llm_str_response: str = llm_json_response.message.content or ""
        self._display_formatted_output(llm_str_response)
        self._add_llm_response_to_context(llm_str_response)

    def _handle_empty_input(self) -> None:
        self._display_formatted_output("Please enter an input\n")

    def _handle_input_with_existing_context(self, user_input: str) -> None:
        self._add_user_input_to_context(user_input)
        llm_json_response: ChatResponse = generate_response(
            context=self.context, model_name=self.config.get_model()
        )
        llm_str_response: str = llm_json_response.message.content or ""
        self._display_formatted_output(llm_str_response)
        self._add_llm_response_to_context(llm_str_response)

    def _handle_fresh_input(self, user_input: str) -> None:
        self._add_system_prompt_to_context(self.config.get_system_prompt())
        context: str = self._build_context_for_assists()
        self._add_user_input_to_context(context + user_input)
        llm_json_response: ChatResponse = generate_response(
            context=self.context, model_name=self.config.get_model()
        )
        llm_str_response: str = llm_json_response.message.content or ""
        self._display_formatted_output(llm_str_response)
        self._add_llm_response_to_context(llm_str_response)

    def handle_input(self, user_input: str) -> None:
        # if not new run
        if self.context:
            # if user input is not empty
            if user_input:
                self._handle_input_with_existing_context(user_input)
            else:
                self._handle_empty_input()
        else:
            self._handle_fresh_input(user_input)

    def handle_error(self, err_value: str) -> None:
        self._handle_initial_error(err_value)
