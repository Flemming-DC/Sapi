
from typing import Callable
from dataclasses import dataclass

@dataclass
class Dialect:
    dialect_str: str
    blank_from_clause: str
    columns_query: str
    foreign_keys_query: str
    connect: Callable

def foo(): ...

postgress = Dialect(
    dialect_str = "dum",
    blank_from_clause = "dum",
    columns_query = "dum",
    foreign_keys_query = "dum",
    connect = foo,
)
print(postgress)


