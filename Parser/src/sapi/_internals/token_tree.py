from __future__ import annotations
from dataclasses import dataclass, field
from collections import namedtuple
from sqlglot.tokens import TokenType
from sapi._internals.error import CompilerError

@dataclass
class Token:
    type: TokenType # evt. type: TokType
    text: str
    line: int # The line that the token ends on. (maybe usable by editor, but not by parser. could in principle be recalculated)
    start: int # start index (used in parser and maybe editor)
    end: int = None # start + len(text) - 1 (possibly up to an offset that depends on the string boundary width) 

    def __str__(_): return f"{_.type.name}: {_.text}" # at {_.start} on {_.line}
    

    def __post_init__(_):
       if _.end is None: 
           _.end = _.start + len(_.text) - 1


@dataclass 
class StrReplacement:
    str_from: int
    str_to: int
    text: str
    is_new_clause: bool



@dataclass
class TokenTree:
    tokens: list[Token|TokenTree] # variable
    _len_sapi_str: str # const (evt. only store at the root tree) # contains sapi code for one statement
    _next_token: Token|None # const
    _str_replacements: list[StrReplacement] = field(default_factory=list) # variable

    # ---------- Immitate Token ---------- #
    TokenType.TOKEN_TREE = namedtuple('fake_enum_variant', ['name', 'value'])(name='TOKEN_TREE', value='TOKEN_TREE')
    type: TokenType = TokenType.TOKEN_TREE
    @property 
    def text(_): return "[TokenTree]"
    @property 
    def line(_): return _.tokens[0].line if _.tokens else None
    @property 
    def start(_): return _.tokens[0].start if _.tokens else None
    @property 
    def end(_): raise CompilerError("Don't call end() on TokenTree.") # dont use this
    # -------------------------------------- # 

    # def has_passed(_, stopping_obj: str, str_index: int) -> bool:
    #     location = _._sapi_str.find(stopping_obj)
    #     return str_index >= location and location != -1
        

    def make_replacement(_, from_: int, to: int, new_text: str, is_new_clause: bool):
        count = len(_.tokens)
        if from_ < 0 or to > count:
            raise CompilerError("index out of bounds")
        if to < from_:
            raise CompilerError("to < from_ is an error.")
                
        # save str data
        next = _._next_token # also = from_tok and to_tok
        from_tok: Token|None = _.tokens[from_] if from_ < count else next
        str_from = from_tok.start if from_tok else _._len_sapi_str

        before_to_tok: Token|None = _.tokens[to - 1] if to > 0 and to - 1 < count else next if to > 0 else None
        str_to = str_from if to == from_ else before_to_tok.end + 1 if before_to_tok else _._len_sapi_str # traditional
        
        _._str_replacements.append(StrReplacement(str_from, str_to, new_text, is_new_clause))




    def recursive_str_replacements(_) -> list[StrReplacement]:
        "used by editor, but not by other parts of parser."
        str_replacements: list[StrReplacement] = []
        str_replacements += _._str_replacements
        for tok in _.tokens:
            if isinstance(tok, TokenTree):
                str_replacements += tok.recursive_str_replacements()
        return str_replacements


def common_select_clauses(): 
    return [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
            TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]
