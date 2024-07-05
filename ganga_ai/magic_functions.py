from IPython.core.ultratb import AutoFormattedTB

from .helpers.sanitize_user_input import sanitize_user_input
from .terminal import Terminal

terminal = Terminal()
itb = AutoFormattedTB(mode = "Plain", tb_offset = 1)

"""
This custom_exception callback is registered with ipython such that anytime any exception occurs this callback is run.
If the exception is caused by a <C-c> or <C-d> we let it take place. Else we grather the error and send it to the llm for help.
If the user wants they can exit before llm finishes responding by <C-c>
"""
def custom_exception(shell, etype, evalue, tb, tb_offset=None):
    # show the err in the terminal also and dont just swallow it
    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)
    
    # if the user wants to interrupt or the process let the user do so
    if etype in ["KeyboardInterrupt", "SystemExit"]:
        return
    try:
        stb = itb.structured_traceback(etype, evalue)
        sstb = itb.stb2text(stb)
        terminal.handle_error(sstb)
    except Exception as err:
        pass
    # if user interrupts it
    except KeyboardInterrupt:
        pass

def assist(line, cell):
    """
    In
    %%assist foo
    bar
    foo is the content of the line variable and bar content of the cell
    variable provided to us by IPython.
    So we need to sanitize and combine both before passing it to the llm.
    """
    user_input = sanitize_user_input(line, cell)
    terminal.handle_input(user_input)
