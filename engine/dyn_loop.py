from typing import Callable
from collections import namedtuple
from dataclasses import dataclass
from sqlglot.tokens import Token, TokenType
# from .token_tree import Token, TokenType

class ParserError(Exception): ...
_Replacement = namedtuple('_Replacement', ['from_', 'to', 'new'])
# _TokenInput = namedtuple('_TokenInput', ['text', 'TokenType'])
# @dataclass
# class _Replacement:
#     from_: int
#     to: int
#     new: int
# @dataclass
# class _TokenInput:
#     TokenType: str
#     text: str

class DynLoop:
    def __init__(_, tokens: list[Token], sapi_str: str, start: int = 0):
        _._sapi_str = sapi_str # const
        _._tokens = tokens
        _._i = start - 1 # index = token_index, not sapi_str index
        _._count = len(tokens)
        _._replacements: list[_Replacement] = []
        _._breakpoint_index: int|None = None

    def __iter__(_): return _
    def __next__(_):
        _._i += 1
        if _._i >= _._count:
            raise StopIteration
        if _._i >= _._breakpoint_index:
            breakpoint()
        return _._tokens[_._i]

    def __str__(_): 
        sql_str = _._sapi_str
        for rep in _._replacements:
            sql_str = sql_str[:rep.from_] + rep.new + sql_str[rep.to:]
        return sql_str

    def _tok(_, distance: int = 0): return _._tokens[_._i + distance]

    def _replace(_, from_: int, to: int, new: list[tuple[TokenType, str]]):
        # evt. eliminate from_ by setting it to _._i
        from_tok = _._tokens[from_]
        new_tokens = [Token(t[0], t[1], from_tok.line, from_tok.col, from_tok.start, from_tok.end) for t in new]
        _._tokens[from_:to] = new_tokens
        growth = len(new_tokens) - (to - from_)
        _._i += growth
        _._count += growth
        new_str = ' '.join(t.text for t in new_tokens) # make a better formmating of new_str akin to add_token_str
        _._replacements = _Replacement(from_, to, new_str)


    def insert(_, new: list[tuple[TokenType, str]]):
        _._replace(_._i, _._i, new)

    def replace(_, new: list[tuple[TokenType, str]]):
        _._replace(_._i, _._i + 1, new)


    # def peek(s): return s._tok(1)
    # def peekBack(self): return self.tokens[self.index - 1] if self.index > 0 else raise error
    # def peek(self, distance: int): return self.tokens[self.index + distance]

    # def step(s): return next(s) # evt. step_count
    # def step_until(s, token: Token):
    #     while s._i != token:
    #         s.step()
    #     return s._tok()
    # def step_through(s, token: Token):
    #     while s._i != token:
    #         s.step()
    #     return s.step()
    # step_until(s, condition: Callable[[], bool])
    # def require(s, token: Token, msg: str):
    #     if s._tok(1) != token:
    #         raise ParserError(msg) # parser or user error ?

    def break_on(_, stopping_obj: TokenType|str):
        # find first example of stopping_obj in remaining code to be parsed and store its index
        if isinstance(stopping_obj, str):
            remaining_str = _._sapi_str[_._tok().start:]
            _._breakpoint_index = remaining_str.find(stopping_obj)
            if _._breakpoint_index == -1:
                raise ParserError(f"Cannot break on {stopping_obj}, since it is not in the sapi_str")
        elif isinstance(stopping_obj, TokenType):
            remaining_tokens = _._tokens[_._i:]
            _._breakpoint_index = None
            for i, tok in enumerate(remaining_tokens):
                if tok.token_type == stopping_obj:
                    _._breakpoint_index = i
                    break
            if _._breakpoint_index == None:
                raise ParserError(f"Cannot break on {stopping_obj}, since it is not in the sapi_str")
        else:
            raise ParserError(f"Cannot break on {stopping_obj}, since it is an unrecognized type")
            

    # def step_if(s, tok: Token): ...
    # def step_until(s, tok: Token): ...
    # def step_through(s, tok: Token): ...
    # def step_while(s, condition: Callable): ...





