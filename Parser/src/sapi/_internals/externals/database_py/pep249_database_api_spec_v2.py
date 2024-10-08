from typing import Any, Protocol, Sequence, Tuple, Callable


class Cursor(Protocol):
    def execute(self, operation: str, parameters: Sequence|dict|None = None) -> Any: ...
    def fetchall(self) -> Sequence[Sequence]: ...
    # def fetchone(self) -> Tuple|None: ...
    # def close(self) -> None: ...
    # @property
    # def rowcount(self) -> int: ... # -1 means None
    # @property
    # def description(self) -> Sequence: ... # contains name, type_code and optionally more
    # # additional methods from pep249 that you propably dont need
    #     # executemany( operation, seq_of_parameters )
    #     # .fetchmany([size=cursor.arraysize])
    #     # .arraysize
    #     # .setinputsizes(sizes)
    #     # .setoutputsize(size [, column])


class Connection(Protocol):
    def cursor(self) -> Cursor: ...
    def close(self) -> None: ...
    def commit(self) -> None: ...
    # def rollback(self) -> None: ...


Connect = Callable[..., Connection] # is this really any input, or might it be restricted to int's and str's ?




