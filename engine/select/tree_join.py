from dataclasses import dataclass, field
from engine.token_tree import Token


@dataclass
class TreeJoin: # data for a single join. evt. restrict this to a tree-join
    join_obj: Token
    on_clause_end_index: int
    first_table: str|None = None # the unique element of on_clause_tables except prior_tables
    on_clause_tables: list[str] = field(default_factory=list) # is this needed?
    tables: list[str] = field(default_factory=list) # referenced tables. aka. those tables that must be autojoined.
    # path: list[tuple[str, str]] = field(default_factory=list)

    def __str__(_):
        return 'JoinData(' + ', '.join([
        'join_obj: ' + str(_.join_obj.text), 
        'on_clause_end_index: ' + str(_.on_clause_end_index), 
        'on_clause_tables: ' + str(_.on_clause_tables), 
        'first_table: ' + str(_.first_table), 
        'tables: ' + str(_.tables), 
        ]) + ')'


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

