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
    
def as_popup(old_func: Callable[..., OK]):
    @wraps(old_func)
    def new_func(*args, **kwargs) -> OK:
        try:
            return old_func(*args, **kwargs)
        except Exception as e:
            log(traceback.format_exc())
            server.show_message(e.args[0], t.MessageType.Error)
            return None
    return new_func