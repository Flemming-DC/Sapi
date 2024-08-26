from __future__ import annotations
from collections import namedtuple
from dataclasses import dataclass
from sqlglot.tokens import Token, TokenType

class ParserError(Exception): ...
# _Replacement = namedtuple('_Replacement', ['from_', 'to', 'new'])

@dataclass
class _Replacement:
    from_: int
    to: int
    new_str: str

# could evt. make a similar replace function
# def insert(tokens: list[Token], at: int, new: list[tuple[TokenType, str]]):
#     # evt. eliminate from_ by setting it to _._i
#     from_tok = tokens[at]
#     new_tokens = [Token(t[0], t[1], from_tok.line, from_tok.col, from_tok.start, from_tok.end) for t in new]
#     tokens[from_:to] = new_tokens
#     growth = len(new_tokens) - (to - from_)
#     if _._i <= from_:
#         _._i += growth
#     _._count += growth
#     new_str = ' '.join(t.text for t in new_tokens) # make a better formmating of new_str akin to add_token_str
#     _._replacements.append(_Replacement(at, at, new_str))


class DynLoop:
    def __init__(_, tokens: list[Token], sapi_str: str, start: int = 0):
        _._sapi_str = sapi_str # const
        _._tokens = tokens
        _._replacements: list[_Replacement] = []

        _._i = start - 1 # index = token_index, not sapi_str index
        _._count = len(tokens)
        _._breakpoint_index: int|None = None


    def __str__(_): 
        sql_str = _._sapi_str
        for rep in _._replacements:
            str_from = _._tokens[rep.from_].start
            str_to = _._tokens[rep.to].start # start or end ?

            sql_str = sql_str[:str_from] + rep.new_str + sql_str[str_to:]
            print(sql_str)
        return sql_str

    def tok(_): 
        # if _._i < 0 or _._i >= _._count:
        #     raise Exception("index out of range")
        return _._tokens[_._i]

    def _replace(_, from_: int, to: int, new: list[tuple[TokenType, str]]):
        # evt. eliminate from_ by setting it to _._i
        if from_ > 0:
            from_tok = _._tokens[from_ - 1]
            new_tokens = [Token(t[0], t[1], from_tok.line, from_tok.col, from_tok.start, from_tok.end) for t in new]
        else:
            new_tokens = [Token(t[0], t[1], 0, 0, 0, 0) for t in new] # is this correct?
        _._tokens[from_:to] = new_tokens
        growth = len(new_tokens) - (to - from_)
        if _._i <= from_:
            _._i += growth
        _._count += growth
        new_str = ' '.join(t.text for t in new_tokens) # make a better formmating of new_str akin to add_token_str
        _._replacements.append(_Replacement(from_, to, new_str))


    def insert(_, new: list[tuple[TokenType, str]], distance: int = 0):
        at = _._i + distance
        _._replace(at, at, new)

    def replace(_, new: list[tuple[TokenType, str]]):
        _._replace(_._i, _._i + 1, new)


    def peek(_, distance: int = 1) -> Token|None: 
        index = _._i + distance
        if index < 0 or index >= _._count:
            return None
        return _._tokens[index]

    def next(_) -> bool:
        "Step to next element and return True, if a next element was found"
        # if len(_.get_tokens()) != _._count: assert False, ""
        _._i += 1
        if _._i >= _._count:
            return False
        if _._breakpoint_index is not None and _._i >= _._breakpoint_index:
            breakpoint()
            _._breakpoint_index = None
        # print(_._tokens[_._i].text + ' ', 
        #       end = '\n' if _._tokens[_._i].token_type in _common_select_clauses else '') # toggle on or off
        return True
    

    def found(_, tokenType: TokenType|list[TokenType], after_steps: int) -> bool:
        "Checks for tokenType after presicely the specified number of steps."
        index = _._i + after_steps
        if index < 0 or index >= _._count:
            return False
        tokenTypes = tokenType if isinstance(tokenType, list) else [tokenType]
        return _._tokens[index].token_type in tokenTypes
    
    def index(_): return _._i # hopefully temp
    def set_index(_, i): _._i = i # hopefully temp

    def get_tokens_(_): return _._tokens # temp
    def reset_(_): _._i = 0 # temp ???
    def manual_inc_(_, i: int, count: int):  # temp
        _._i = i
        _._count = count
    def set_tokens_(_, tokens: list[Token]): # temp
        _._tokens = tokens

    def break_on(_, stopping_obj: TokenType|str):
        # find first example of stopping_obj in remaining code to be parsed and store its index
        if isinstance(stopping_obj, str):
            remaining_str = _._sapi_str[_.tok().start:]
            _._breakpoint_index = remaining_str.find(stopping_obj)
            if _._breakpoint_index == -1:
                _._breakpoint_index = None
        elif isinstance(stopping_obj, TokenType):
            remaining_tokens = _._tokens[_._i:]
            _._breakpoint_index = None
            for i, tok in enumerate(remaining_tokens):
                if tok.token_type == stopping_obj:
                    _._breakpoint_index = i
                    break
        else:
            raise ParserError(f"Cannot break on {stopping_obj}, since it is an unrecognized type")
            
    def has_passed(_, stopping_obj: str) -> bool:
        location = _._sapi_str.find(stopping_obj)
        return _._i >= location and location != -1

    def at_end(_, distance: int = 0): return _._i + distance >= _._count

    # def before_start(_): return _._i < 0
    # def out_of_bounds(_): return _._i < 0 or _._i >= _._count

    # def set_tokens_and_reset_index(_, tokens: list[Token]):
    #     _._tokens = tokens
    #     _._i = 0
    # def step(_) -> DynLoop:
    #     # if len(_.get_tokens()) != _._count: assert False, ""
    #     _._i += 1
    #     if _._i >= _._count:
    #         return _
    #     if _._breakpoint_index is not None and _._i >= _._breakpoint_index:
    #         breakpoint()
    #         _._breakpoint_index = None
    #     # print(_._tokens[_._i].text + ' ', 
    #     #       end = '\n' if _._tokens[_._i].token_type in _common_select_clauses else '') # toggle on or off
    #     return _
        
    
    # def step_until(_, condition: Callable[[], bool]):
    #     while not condition():
    #         _.next()
    #         # if _.step() is None:
    #         #     break