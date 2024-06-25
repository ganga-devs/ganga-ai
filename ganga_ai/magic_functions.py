from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from llama_index.llms.ollama.base import ChatMessage
from .generate import generate_initial_response, generate_response, format_output
from .context import Context

def sanitize_user_input(line: str, cell: str):
    """
    In
    %%assist foo
    bar
    foo is the content of the line variable and bar content of the cell
    variable provided to us by IPython.
    So we need to sanitize and combine both before passing it to the llm.
    """
    line_txt = line.strip()
    cell_txt = cell.strip()
    return line_txt + cell_txt

global firstRun
firstRun = True
context = Context()

# @magic_arguments()
# @argument("--verbose", )
def assist(line, cell):
    INITIAL_PROMPT = """
    Write a hello world python code
    """.strip()

    user_text = sanitize_user_input(line, cell)
    

    #TODO: add types for this json object
    #The type should be ChatMessage
    jsonOutput = ""
    if firstRun:
        if user_text:
            jsonOutput = generate_initial_response(user_text)
        else:
            jsonOutput = generate_initial_response(INITIAL_PROMPT)
    else:
        context.add_user_msg_to_context(user_text)
        jsonOutput = generate_response(context.get_contxt())
    context.add_system_msg_to_context(jsonOutput.text)
    format_output(jsonOutput.text)
    return
