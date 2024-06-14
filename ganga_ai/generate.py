# CODE_ASSITANCE_PROMPT = """
# As a coding assistant, your task is to help users write code in Python within Jupyter Notebooks. Provide comments and code for the user to read and edit, ensuring it can be run successfully. The user will be able to run the code in the cell and see the output.
#
# When the user is interacting with you their message will start with `%%assist`. Otherwise, they are running commands and getting output from the system.
#
# You can use markdown to format your response. For example, to create a code block, use
#
# ```python
# # code
# ```
# """.strip()

CODE_ASSITANCE_PROMPT = """
Write a hello world python code
""".strip()

from llama_index.llms.ollama import Ollama
from typing import Optional

def generate_response(prompt: str = CODE_ASSITANCE_PROMPT, context: Optional[str] = None):
    llm = Ollama (model="mistral")
    result = llm.complete(prompt)
    return result
