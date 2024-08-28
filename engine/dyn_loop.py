from __future__ import annotations
from dataclasses import dataclass
from sqlglot.tokens import Token, TokenType

class ParserError(Exception): ...

@dataclass
class _StrReplacement:
    from_: int
    to: int
    new: str



class DynLoop:
    def __init__(_, tokens: list[Token], sapi_str: str, 
                 previous_token: Token, next_token: Token, start: int = 0):
        _._sapi_str = sapi_str # const
        _._tokens = tokens
        _._previous_token: Token|None = previous_token
        _._next_token: Token|None = next_token
        _._str_replacements: list[_StrReplacement] = []

        _._i = start - 1 # index = token_index, not sapi_str index
        _._count = len(tokens)
        _._breakpoint_index: int|None = None


    def __str__(_): 
        sql_str = ""
        _._str_replacements.sort(key = lambda r: r.from_)
        for i, rep in enumerate(_._str_replacements):
            last_rep_to = _._str_replacements[i - 1].to if i > 0 else 0
            sql_str += _._sapi_str[last_rep_to:rep.from_ - 1] + ' ' + rep.new + ' '
        last_rep_to = _._str_replacements[-1].to
        sql_str += _._sapi_str[last_rep_to:]
        return sql_str

    def tok(_): 
        # if _._i < 0 or _._i >= _._count:
        #     raise Exception("index out of range")
        return _._tokens[_._i]

    def _replace(_, from_: int, to: int, new: list[tuple[TokenType, str]]):
        if to != from_ and to != from_ + 1:
            raise ParserError("øv!")
        if from_ < 0 or to > _._count:
            raise ParserError("index out of bounds")

        from_tok: Token|None = _._tokens[from_] if from_ < _._count else _._next_token

        if from_tok:
            new_tokens = [Token(t[0], t[1], from_tok.line, from_tok.col, from_tok.start, from_tok.end) for t in new]
        else:
            next = _._next_token # also = from_tok and to_tok
            new_tokens: list[Token] = []
            for t in new:
                prev_start = new_tokens[-1].start if new_tokens else next.start if next else len(_._sapi_str)
                # prev_end = new_tokens[-1] if new_tokens else last.end
                new_tokens.append(Token(t[0], t[1], 
                    next.line if next else _._tokens[-1], 
                    next.col if next else _._tokens[-1], 
                    prev_start + len(t[1]), 'invalid data'))

        # save str data
        str_from = from_tok.start if from_tok else len(_._sapi_str)
        width = 0 if to == from_ else len(_.tok().text) # if to == from_ + 1 else error
        str_to = str_from + width # if to_tok else str_from + len(' '.join([t.text for t in _._tokens[from_:to]])) # shitty
        new_str = ' '.join(t.text for t in new_tokens) # make a better formmating of new_str akin to add_token_str
        _._str_replacements.append(_StrReplacement(str_from, str_to, new_str))

        # modify tokens, index and count
        _._tokens[from_:to] = new_tokens
        growth = len(new_tokens) - (to - from_)
        if _._i <= from_:
            _._i += growth
        _._count += growth


    def insert(_, new: list[tuple[TokenType, str]], distance: int = 0):
        at = _._i + distance
        _._replace(at, at, new)



    def replace(_, new: tuple[TokenType, str]):
        _._replace(_._i, _._i + 1, [new])


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


