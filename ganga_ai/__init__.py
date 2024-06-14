from .generate import generate_response

def load_ipython_extension(ipython):
    ipython.register_magic_function(generate_response, 'cell')

def unload_ipython_extension(ipython):
    ipython.set_custom_exc(Exception, None)
