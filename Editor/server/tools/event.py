from typing import Callable, TypeVar, Generic, List

ARGS = TypeVar('ARGS')
OUT = TypeVar('OUT')

class Event(Generic[ARGS, OUT]):

    def __init__(_):
        _._functions: list[Callable[..., OUT]] = [] # ... = *ARGS

    def add(_, func: Callable[..., OUT]):
        "func: *ARGS -> OUT"
        if func not in _._functions:
            _._functions.append(func)

    def occur(_, *args: ARGS) -> OUT:
        for func in _._functions:
            func(*args)

    def __call__(_, old_func: Callable[..., OUT]):
        "this call allows Event to be used like a decorator."
        _.add(old_func)
        return old_func


# technically, this should be in the server, but its OK.
on_server_start: Event[None, None] = Event() 


