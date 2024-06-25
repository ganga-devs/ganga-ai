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

from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def generate_initial_response(prompt: str):
    llm = Ollama (model="mistral", request_timeout=300)
    result = llm.complete(prompt)
    return result

# def generate_response(context: list[ChatMessage]):
def generate_response(context):
    llm = Ollama (model="mistral")
    result = llm.chat(context)
    return result

def format_output(rawOutput: str):
    markdownOutput = Markdown(rawOutput)
    console.print(markdownOutput)
