from typing import TypeVar, Generic, Callable
from functools import wraps

OK = TypeVar('OK') # OK cannot be an Exception or a Fallible 

class Fallible(Generic[OK]):
    def __init__(self, value: OK|Exception):
        # nested fallibles gets unwrapped.
        self._value = value._value if isinstance(value, Fallible) else value

    def is_ok(self): return not isinstance(self._value, Exception)
    def is_err(self): return isinstance(self._value, Exception)

    @property
    def ok(self, error_message: str = None) -> OK:
        if isinstance(self._value, Exception):
            raise Exception(error_message if error_message 
                            else f"Attempted to get ok value from Fallible, but found {self} ")
        return self._value
    
    @property
    def err(self, error_message: str = None) -> Exception:
        if not isinstance(self._value, Exception):
            raise Exception(error_message if error_message 
                            else f"Attempted to get error from Fallible, but found {self} ")
        return self._value
    
    @ok.setter
    def ok(self, value: OK):
        if isinstance(value, Exception):
            raise Exception("The ok value must not be an exception.")
        self._value = value._value if isinstance(value, Fallible) else value
    
    @err.setter
    def err(self, value: Exception):
        if not isinstance(value, Exception):
            raise Exception("The err value must be an exception.")
        self._value = value #if isinstance(value, Exception) else Exception(value)

    def ok_or(self, alternative_ok: OK) -> OK: 
        return self.ok if self.is_ok() else alternative_ok

    def err_or(self, alternative_error: str) -> Exception: 
        return self.err if self.is_err() else Exception(alternative_error)

    def raise_(self): raise self.err

    def ok_or_raise(self, error: str|Exception): 
        if self.is_ok():             return self.ok
        elif isinstance(error, str): raise Exception(error)
        else:                        raise error

    def __repr__(self):
        variant = 'ok' if self.is_ok() else 'err'
        return f"{variant}({self._value})"

    def __bool__(self): return self.is_ok()


def ok(value: OK):
    if isinstance(value, Exception):
        raise Exception("The ok value must not be an exception.")
    return Fallible(value)

def err(value: str, excType: type[Exception] = Exception): 
    return Fallible(excType(value))


def try_(func: Callable[..., OK], *args, **kwargs) -> Fallible[OK]:
    try:
        return ok(func(*args, **kwargs))
    except Exception as e:
        return err(e)


def fallible(old_func: Callable[..., OK]):
    @wraps(old_func)
    def new_func(*args, **kwargs) -> Fallible[OK]:
        try:
            return ok(old_func(*args, **kwargs))
        except Exception as e:
            return err(e)
    return new_func



# ---------- usage ---------- #
if __name__ == '__main__':

    def bar(i: int) -> Fallible[str]:
        if i == 0: 
            return err("mustn't be zero")
        return ok(str(i))



    fal = bar(0)
    if fal: fal.ok.upper() # noqa
    else: fal.err # noqa



    if fal.is_ok(): print(fal.ok) # noqa
    if fal.is_err(): print(fal.err) # noqa
    fal.ok = 2
    print(fal.ok, type(fal.ok))
    fal.err = "wrong"
    print(fal.err, type(fal.err))
    fal.err = Exception("bad")
    print(fal.err, type(fal.err))
    # print(fal)

    if fal: print('if check passed') # noqa
    else: print('if check failed') # noqa

    if fal: print(fal.ok) # noqa
    else: print(fal.err) # noqa

    # x = fal.ok if fal else fal.raise_()
    x = fal.ok if fal else 0
    print('done')

    def high() -> Fallible[str]:
        f = bar(1)
        if not f: return f # noqa
        f.ok = f.ok.capitalize()
        return f

    def high2() -> str:
        f = bar(1)
        if not f: return str(f.err) # noqa
        return f.ok.capitalize()

    def high3() -> str:
        f = bar(1)
        # if f: return f.ok.capitalize() # noqa
        # else: return str(f.err) # noqa
        return f.ok.capitalize() if f else str(f.err)



