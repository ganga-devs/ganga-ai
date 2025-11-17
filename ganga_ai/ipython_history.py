from IPython.core.getipython import get_ipython
from IPython.core.history import HistoryAccessor

"""
This class is responsible for accessing and maintaining the ipython history.
"""


class IpythonHistory:
    def __init__(self):
        self.ipython_instance = get_ipython()
        self.ipython_history_manager = HistoryAccessor()
        self.session_id = self.ipython_history_manager.get_last_session_id()

    def get_command_history(self, count: int = 10) -> str:
        current_exec_count = self.ipython_instance.execution_count
        starting_count = max(current_exec_count - count, 1)
        messages = (
            "The past few commands ran in the ipython terminal and their outputs are:"
        )
        for _, _, (input_text, output_text) in self.ipython_history_manager.get_range(
            session=self.session_id,
            start=starting_count,
            stop=current_exec_count,
            output=True,
        ):
            if input_text == "%load_ext ganga_ai":
                continue
            if output_text:
                messages += f"\nIn: {input_text}\nOut: {output_text}"
            else:
                messages += f"\nIn: {input_text}"
        return messages

ipython_history = IpythonHistory()
