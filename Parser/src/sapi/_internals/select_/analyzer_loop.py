from __future__ import annotations
from sapi._internals.token_tree import TokenTree, Token, TokenType


class AnalyzerLoop:
    def __init__(_, token_tree: TokenTree, start: int = 0):
        _._token_tree = token_tree
        _._tokens = token_tree.tokens # could be eliminated in favor of _._token_tree.tokens
        _._i = start - 1 # index = token_index, not sapi_str index
        _._count = len(_._tokens)
        _._breakpoint_index: int|None = None

    
    def tok(_): 
        return _._tokens[_._i]


    
    def peek(_, distance: int = 1) -> Token|None: 
        index = _._i + distance
        if index < 0 or index >= _._count:
            return None
        return _._tokens[index]

    
    def next(_) -> bool:
        "Step to next element and return True, if a next element was found"
        _._i += 1
        if _._i >= _._count:
            return False
        if _._breakpoint_index is not None and _._i >= _._breakpoint_index:
            breakpoint()
            _._breakpoint_index = None
        return True
    
    
    def found(_, tokenType: TokenType|list[TokenType], after_steps: int) -> bool:
        "Checks for tokenType after presicely the specified number of steps."
        index = _._i + after_steps
        if index < 0 or index >= _._count:
            return False
        tokenTypes = tokenType if isinstance(tokenType, list) else [tokenType]
        return _._tokens[index].type in tokenTypes
    
    
    def index(_): return _._i 
    
    
    def has_passed(_, stopping_obj: str) -> bool:
        return _.at_end() or _._token_tree.has_passed(stopping_obj, _.tok().start)
    
    def at_end(_, distance: int = 0): return _._i + distance >= _._count

    def view(_, from_: int|None = None, to: int = 0):
        "Meant for debugging"
        from_ = from_ + _._i if from_ is not None else 0
        to = to + _._i if to is not None else -1
        return ' '.join(t.text for t in _._tokens[from_:to])


