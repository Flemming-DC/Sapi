from __future__ import annotations
from textwrap import indent
from dataclasses import dataclass, field
from sqlglot.tokens import auto
from sqlglot.tokens import Token, TokenType
# from dyn_loop import Token, TokenType, ParserError, DynLoop
# from sqlglot.expressions import Expression, Select, Insert, Update, Delete, Column, Table, Create, Drop, With # many kinds of alter 

TokenType.TOKEN_TREE = auto()
_TOKENTYPE_TOKEN_TREE = TokenType.TOKEN_TREE
# TokenType.AUTO_JOIN = auto() # token type for an auto generated collection of join clauses. A fairly big token, I must admit.
# TOKENTYPE_AUTO_JOIN = TokenType.AUTO_JOIN

class ParserError(Exception): ...

@dataclass # go away
class _StrReplacement:
    from_: int
    to: int
    new: str

class AutoToken(Token):...

_common_select_clauses = [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
    TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]

@dataclass
class TokenTree:
    # a token was <class 'builtins.Token'>. Get control over their types
    tokens: list[Token|TokenTree]
    # dyn_loop: DynLoop # go away

    _sapi_str: str # const (evt. only store at the root tree)
    # _tokens = tokens
    # _previous_token: Token|None
    _next_token: Token|None
    _str_replacements: list[_StrReplacement] = field(default_factory=list)

    #region Token Compatibility
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
    def end(self): raise ParserError(f"the end property is extremely unreliable. Don't use it!")
    @property 
    def comments(self): return None
    #endregion

    def __repr__(self) -> str: return self.__repr__1()

    def __repr__1(self) -> str: 
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
        

    def __repr__2(_): 
        sql_str = ""
        _._str_replacements.sort(key = lambda r: r.from_)
        for i, rep in enumerate(_._str_replacements):
            last_rep_to = _._str_replacements[i - 1].to if i > 0 else 0
            sql_str += _._sapi_str[last_rep_to:rep.from_ - 1] + ' ' + rep.new + ' '
        last_rep_to = _._str_replacements[-1].to
        sql_str += _._sapi_str[last_rep_to:]
        return sql_str

    def replace(_, from_: int, to: int, new: list[tuple[TokenType, str]]):
        # checks
        count = len(_.tokens)
        if to != from_ and to != from_ + 1:
            raise ParserError("øv!")
        if from_ < 0 or to > count:
            raise ParserError("index out of bounds")

        # make from_tok and new_tokens
        from_tok: Token|None = _.tokens[from_] if from_ < count else _._next_token
        if from_tok:
            new_tokens = [Token(t[0], t[1], from_tok.line, from_tok.col, from_tok.start, from_tok.end) for t in new]
        else:
            next = _._next_token # also = from_tok and to_tok
            new_tokens: list[Token] = []
            for t in new:
                prev_start = new_tokens[-1].start if new_tokens else next.start if next else len(_._sapi_str)
                # prev_end = new_tokens[-1] if new_tokens else last.end
                new_tokens.append(Token(t[0], t[1], 
                    next.line if next else _.tokens[-1], 
                    next.col if next else _.tokens[-1], 
                    prev_start + len(t[1]), 'invalid data'))

        # save str data
        str_from = from_tok.start if from_tok else len(_._sapi_str)
        width = 0 if to == from_ else len(from_tok.text) # len(_.tok().text)
        str_to = str_from + width
        new_str = ' '.join(t.text for t in new_tokens)
        _._str_replacements.append(_StrReplacement(str_from, str_to, new_str))

        # modify tokens
        _.tokens[from_:to] = new_tokens




