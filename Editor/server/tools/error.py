from typing import TypeVar, Callable
from functools import wraps
from tools.server import server
from lsprotocol import types as t
from .log import log
import traceback

OK = TypeVar('OK')

def try_(old_func: Callable[[], OK], message: str) -> OK: #, *args, **kwargs):
    try:
        return old_func()
    except Exception as e:
        e.args = (message, )
        raise 
    
def as_log_and_popup(old_func: Callable[..., OK]):
    @wraps(old_func)
    def new_func(*args, **kwargs) -> OK:
        try:
            return old_func(*args, **kwargs)
        except Exception as e:
            server.show_message(e.args[0], t.MessageType.Error)
            log("--- ARGS, KWARGS --- (for error.as_log_and_popup decorated function)")
            log(args, kwargs, '\n')
            log(traceback.format_exc())
            return None
    return new_func

_release_mode = False
def dev_assert(requirement: bool, message: str):
    if not requirement and not _release_mode:
        raise Exception(message)

