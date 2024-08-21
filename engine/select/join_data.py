from dataclasses import dataclass, field
from engine.tokenizer import Token


@dataclass
class JoinData:
    join_obj: Token
    is_tree: bool # evt. replace with enum { table | view | cte | tree }
    # index if treeToken is changed into a str, then we store the index seperately
    tables: list[str] = field(default_factory=list) # = []
    # columns: list[Token] = field(default_factory=list) # = []
    path: list[tuple[str, str]] = field(default_factory=list) # = []



"""
table_finder: 
    find tables and trees in from clause in addition to required tables
        -> list[tree, previous, index] 
    try sort unprefixed columns (and thus also tables) by tree (else report a user-error)
    evt. insert the table prefix
        -> list[tree, previous, index, tables, evt. columns] 
loop over trees:
    run path_finder starting at previous (or have tables preordered to begin at previous)
        -> list[tree, previous, index, tables, evt. columns, path]
run join_generator:
    go directly to index (no loop) and auto generate using the associated data.
"""

