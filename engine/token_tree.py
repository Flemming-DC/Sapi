from __future__ import annotations
from textwrap import indent
from dataclasses import dataclass, field
from sqlglot.tokens import auto
from dyn_loop import Token, TokenType, ParserError, DynLoop
# from sqlglot.expressions import Expression, Select, Insert, Update, Delete, Column, Table, Create, Drop, With # many kinds of alter 

TokenType.TOKEN_TREE = auto()
TokenType.AUTO_JOIN = auto() # token type for an auto generated collection of join clauses. A fairly big token, I must admit.
_TOKENTYPE_TOKEN_TREE = TokenType.TOKEN_TREE
TOKENTYPE_AUTO_JOIN = TokenType.AUTO_JOIN



class AutoToken(Token):...

_common_select_clauses = [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
    TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]

@dataclass
class TokenTree:
    # a token was <class 'builtins.Token'>. Get control over their types
    tokens: list[Token|TokenTree] #= field(default_factory=list) # = []
    dyn_loop: DynLoop #= field(default_factory=)

    # make TokenTree compatible with Token
    token_type: TokenType = _TOKENTYPE_TOKEN_TREE
    @property 
    def text(self): return "[TokenTree]" # str(self)
    @property 
    def line(self): return self.tokens[0].line if self.tokens else None
    @property 
    def col(self): return self.tokens[0].col if self.tokens else None
    @property 
    def start(self): return self.tokens[0].start if self.tokens else None
    @property 
    def end(self): return self.tokens[-1].end if self.tokens else None
    @property 
    def comments(self): return None



    def __repr__(self) -> str: 
        s = '['
        for tok in self.tokens:
            if isinstance(tok, TokenTree):
                s += indent(repr(tok), '    ').lstrip()
                # s += tok.text + ' '
            else:
                s = TokenTree.add_token_str(s, tok)
        return s.rstrip(' ') + ']'

    @staticmethod
    def add_token_str(so_far: str, tok: Token) -> str:
        if tok.token_type in _common_select_clauses:
            return so_far + '\n' + tok.text + ' '
        elif tok.text == '.':
            return so_far.rstrip(' ') + tok.text
        elif tok.text in ['(', '[', '{']:
            return so_far + tok.text
        elif tok.text in [',', ')', ']', '}']:
            return so_far.rstrip(' ') + tok.text + ' '
        else:
            return so_far + tok.text + ' '
        
    def flatten(self) -> list[Token]:
        all_tokens: list[Token] = []
        for tok in self.tokens:
            if isinstance(tok, TokenTree):
                all_tokens += tok.flatten()
            else:
                all_tokens.append(tok)
        return all_tokens



