from typing import TypeVar, Callable
from functools import wraps
from tools.server import server
from lsprotocol import types as t

OK = TypeVar('OK')

def handle_error(fallible: OK|Exception, message: str = None) -> bool:
    if not isinstance(fallible, Exception): 
        return False
    server.show_message(message if message else str(fallible), t.MessageType.Error)
    return True

def handle_condition(condition: bool, message: str) -> bool:
    if not condition: 
        return False
    server.show_message(message, t.MessageType.Error)
    return True



def is_err(fallible: OK|Exception): return isinstance(fallible, Exception)


def fallible(old_func: Callable[..., OK]):
    @wraps(old_func)
    def new_func(*args, **kwargs) -> OK | Exception:
        try:
            return old_func(*args, **kwargs)
        except Exception as e:
            return e
    return new_func

