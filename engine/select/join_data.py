from dataclasses import dataclass, field
from engine.token_tree import Token


@dataclass
class JoinData: # data for a single join. evt. restrict this to a tree-join
    join_obj: Token
    is_tree: bool # evt. replace with enum { table | view | cte | tree }
    on_clause_end_index: int
    on_clause_tables: list[str] = field(default_factory=list) # is this needed?
    first_table: str|None = None # the unique element of on_clause_tables - prior_tables
    # index if treeToken is changed into a str, then we store the index seperately
    tables: list[str] = field(default_factory=list) # referenced tables. aka. thoses tables that must be autojoined.
    # columns: list[Token] = field(default_factory=list)
    path: list[tuple[str, str]] = field(default_factory=list)

    def __str__(_):
        return 'JoinData(' + ', '.join([
        'join_obj: ' + str(_.join_obj.text), 
        'is_tree: ' + str(_.is_tree), 
        'on_clause_end_index: ' + str(_.on_clause_end_index), 
        'on_clause_tables: ' + str(_.on_clause_tables), 
        'first_table: ' + str(_.first_table), 
        'tables: ' + str(_.tables), 
        'path: ' + str(_.path)]) + ')'


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

