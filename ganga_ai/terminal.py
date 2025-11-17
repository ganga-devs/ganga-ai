from rich.console import Console
from rich.markdown import Markdown
from ganga_ai.vector_store import vector_store
from ganga_ai.ipython_history import ipython_history

"""
This class is responsible for maintaining terminal state and does all the heavy lifting wrt what is displayed in the terminal. It exposes apis the magic commands can use.
"""


class Terminal:
    def __init__(self):
        self.console = Console()

    def display_formatted_output(self, rawOutput: str) -> None:
        markdownOutput = Markdown(rawOutput)
        self.console.print(markdownOutput)

    def sanitize_user_input(self, line: str, cell: str) -> str:
        line_txt = line.strip()
        cell_txt = cell.strip()
        return line_txt + cell_txt

    def handle_empty_input(self) -> None:
        self.display_formatted_output("Please enter an input\n")

    def handle_input_with_existing_context(self, user_input: str) -> None:
        llm_response = vector_store.query_vector_store(user_input)
        self.display_formatted_output(str(llm_response))

    def handle_fresh_input(self, user_input: str) -> None:
        command_history: str = ipython_history.get_command_history()
        combined_input = command_history + "\n" + user_input
        llm_response = vector_store.query_vector_store(combined_input)
        self.display_formatted_output(str(llm_response))

    def handle_input(self, line: str, cell: str) -> None:
        user_input: str = self.sanitize_user_input(line, cell)

        if not user_input:
            self.handle_empty_input()

        if ipython_history.history:
            self.handle_input_with_existing_context(user_input)
        else:
            self.handle_fresh_input(user_input)

    def handle_error(self, err_value: str) -> None:
        self.display_formatted_output("Processing the error to help you...")
        message = (
            "The command ran at the terminal and the error I got from it is:\n"
            + err_value
            + "\nHow do I fix it?"
        )
        llm_response = vector_store.query_vector_store(message)
        self.display_formatted_output(str(llm_response))


terminal = Terminal()
