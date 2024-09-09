from dataclasses import dataclass, field
from engine.token_tree import Token


@dataclass
class TreeJoin: # data for a single join. evt. restrict this to a tree-join
    tree_tok: Token
    tree_tok_index: int
    on_clause_end_index: int
    first_table: str|None = None # the unique element of on_clause_tables except prior_tables
    referenced_tables: list[str] = field(default_factory=list) # referenced tables. aka. those tables that must be autojoined.

    def __str__(_):
        return 'JoinData(' + ', '.join([
        'join_obj: ' + str(_.tree_tok.text), 
        'on_clause_end_index: ' + str(_.on_clause_end_index), 
        'first_table: ' + str(_.first_table), 
        'tables: ' + str(_.referenced_tables), 
        ]) + ')'



