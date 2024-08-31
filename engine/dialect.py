from .token_tree import TokenType


dialect_str = "postgres"


blank_from_clause: dict[str, list[tuple[TokenType, str]]] = {
    'postgres': [],
    'oracle': [
        (TokenType.FROM, 'FROM'),
        (TokenType.VAR, 'dual'),
        ],
}

