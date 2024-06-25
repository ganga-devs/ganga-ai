from .magic_functions import assist

def load_ipython_extension(ipython):
    ipython.register_magic_function(assist, 'cell')

def unload_ipython_extension(ipython):
    ipython.set_custom_exc(Exception, None)
