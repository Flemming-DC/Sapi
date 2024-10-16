from dataclasses import dataclass, field
from sapi._internals.token_tree import Token


@dataclass
class TreeJoin:
    tree_tok: Token
    tree_tok_index: int
    on_clause_end_index: int
    first_table: str|None = None # the unique element of on_clause_tables except prior_tables
    referenced_tables: list[str] = field(default_factory=list) # referenced tables. aka. those tables that must be autojoined.

    def __str__(_):
        return 'JoinData(' + ', '.join([
        'tree_tok: ' + str(_.tree_tok.text), 
        'tree_tok_index: ' + str(_.on_clause_end_index), 
        'first_table: ' + str(_.first_table), 
        'referenced_tables: ' + str(_.referenced_tables), 
        ]) + ')'



