import inspect
from typing import Any
from functools import wraps
from typing import TypeVar, Callable
from tools.server import server
from tools.error import handle_condition

T = TypeVar('T')
def command(old_func: Callable[..., T]):
    
    @server.command(old_func.__name__)
    @wraps(old_func)
    def new_func(params: list[Any]) -> T:
        required_types: list[type] = [p.annotation if p.annotation != inspect._empty else Any 
                                    for p in inspect.signature(old_func).parameters.values()]
        actual_types = [type(p) for p in params]
        valid_input = (len(params) == len(required_types)
            and all(isinstance(p, t) for p, t in zip(params, actual_types)))
        if handle_condition(not valid_input, 
            f"{old_func.__name__} expects {required_types} containing a single element, namely a query. Received: \n{params}"
            ): return
        
        output = old_func(*params)
        if output != None:
            server.send_output(output)

    return new_func

