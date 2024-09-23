from .magic_functions import assist, enable_rag, custom_exception


def load_ipython_extension(ipython):
    ipython.register_magic_function(assist, "cell")
    ipython.register_magic_function(enable_rag, "cell")
    ipython.set_custom_exc((Exception,), custom_exception)


def unload_ipython_extension(ipython):
    ipython.set_custom_exc(Exception, None)
