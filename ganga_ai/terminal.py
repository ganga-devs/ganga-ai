from llama_index.core.base.llms.types import ChatMessage
from rich.console import Console
from rich.markdown import Markdown
from IPython.core.getipython import get_ipython
from IPython.core.history import HistoryAccessor

"""
This class is responsible for maintaing terminal state. It exposes apis the magic commands can use.
"""


class Terminal:
    def __init__(self):
        self.console = Console()
        self.ipython_instance = get_ipython()
        self.ipython_history_manager = HistoryAccessor()

    def _display_formatted_output(self, rawOutput: str) -> None:
        markdownOutput = Markdown(rawOutput)
        self.console.print(markdownOutput)

    def _build_command_history_for_assists(self, count: int = 5) -> str:
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
        # llm_str_response: str = generate_response(
        #     user_input=err_value,
        #     system_prompt=self.config.get_system_prompt(),
        #     history=self.history,
        #     model_name=self.config.get_model(),
        #     index=self.config._rag_index,
        # )
        # self._display_formatted_output(llm_str_response)

    def _handle_empty_input(self) -> None:
        self._display_formatted_output("Please enter an input\n")

    def _handle_input_with_existing_context(self, user_input: str) -> None:
        # llm_str_response: str = generate_response(
        #     user_input=user_input,
        #     system_prompt=self.config.get_system_prompt(),
        #     history=self.history,
        #     model_name=self.config.get_model(),
        #     index=self.config._rag_index,
        # )
        # self._display_formatted_output(llm_str_response)
        pass

    # def _handle_fresh_input(self, user_input: str) -> None:
        # command_history: str = self._build_command_history_for_assists()
        # self._add_user_input_to_history(command_history + user_input)
        # llm_str_response: str = generate_response(
        #     user_input=user_input,
        #     system_prompt=self.config.get_system_prompt(),
        #     history=self.history,
        #     model_name=self.config.get_model(),
        #     index=self.config._rag_index,
        # )
        # self._display_formatted_output(llm_str_response)

    def handle_input(self, user_input: str) -> None:
        # if not new run
        if self.history:
            # if user input is not empty
            if user_input:
                self._handle_input_with_existing_context(user_input)
            else:
                self._handle_empty_input()
        else:
            self._handle_fresh_input(user_input)

    def handle_error(self, err_value: str) -> None:
        self._handle_initial_error(err_value)
