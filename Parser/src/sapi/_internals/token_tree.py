from __future__ import annotations
from dataclasses import dataclass, field
from collections import namedtuple
from sqlglot.tokens import TokenType


@dataclass
class Token:
    type: TokenType # evt. type: TokType
    text: str
    line: int # The line that the token ends on. (maybe usable by editor, but not by parser. could in principle be recalculated)
    start: int # start index (used in parser and maybe editor)
    end: int = None # start + len(text) + 2 * len(string_boundary) 

    def __str__(_): return f"{_.type.name}: {_.text}" # at {_.start} on {_.line}
    # def end(_): return _.start + len(_.text)



class ParserError(Exception): ... # why is this located here ??

@dataclass 
class _StrReplacement:
    str_from: int
    str_to: int
    new_tokens: list[Token]


_common_select_clauses = [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
    TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]
def common_select_clauses(): return _common_select_clauses # used by editor

@dataclass
class TokenTree:
    tokens: list[Token|TokenTree] # variable
    _sapi_str: str # const (evt. only store at the root tree) # contains sapi code for one statement
    _next_token: Token|None # const
    _str_replacements: list[_StrReplacement] = field(default_factory=list) # variable

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
    def end(_): raise Exception("Don't call end() on TokenTree.") # dont use this
    # -------------------------------------- # 

    def has_passed(_, stopping_obj: str, str_index: int) -> bool:
        location = _._sapi_str.find(stopping_obj)
        return str_index >= location and location != -1
        

    def replace(_, from_: int, to: int, new: list[tuple[TokenType, str]]):
        # checks
        count = len(_.tokens)
        if to > from_ + 1:
            # we reduce the case of to >= from_ + 1 into to == from_ + 1, for which the width (str_to - str_from)
            # is known: width = len(from_tok.text)
            for i in range(from_ + 1, to):
                _.replace(i, i + 1, []) 
            to = from_ + 1
        if to != from_ and to != from_ + 1:
            raise ParserError("Replace currently only allows the removal of up to one token at a time")
        if from_ < 0 or to > count:
            raise ParserError("index out of bounds")
        # if _.tokens[from_].type

        # make from_tok and new_tokens
        next = _._next_token # also = from_tok and to_tok
        from_tok: Token|None = _.tokens[from_] if from_ < count else next
        if from_tok:
            new_tokens = [Token(t[0], t[1], from_tok.line, from_tok.start) for t in new]
        else:
            new_tokens: list[Token] = []
            for t in new:
                prev_start = new_tokens[-1].start if new_tokens else next.start if next else len(_._sapi_str)
                # prev_end = new_tokens[-1] if new_tokens else last.end
                new_tokens.append(Token(
                    type = t[0], 
                    text = t[1], 
                    line = next.line if next else _.tokens[-1].line, 
                    start = prev_start + len(t[1])
                    ))

        # save str data
        str_from = from_tok.start if from_tok else len(_._sapi_str)
        # width = 0 if to == from_ else len(from_tok.text) # this line imposes the restriction of removing at most one token at a time
        # str_to = str_from + width
        str_to = str_from if to == from_ else from_tok.end + 1 if from_tok else len(_._sapi_str)
        # new_str = ' '.join(t.text for t in new_tokens)

        # str_from -= _.tokens[0].start
        # str_to -= _.tokens[0].start
        _._str_replacements.append(_StrReplacement(str_from, str_to, new_tokens))

        # modify tokens
        _.tokens[from_:to] = new_tokens


#region -------------- cast to str --------------

    def __str__(_) -> str:
        str_replacements = _.recursive_str_replacements() # collect replacements in subtrees
        if not str_replacements:
            return _._sapi_str # handle the None case

        # make string
        # sql_str is on the form: 
        #   sapi-segment + replacement +
        #   ...
        #   sapi-segment + replacement +
        #   sapi-segment 
        sql_str = ""
        str_replacements.sort(key = lambda r: r.str_from)
        for i, rep in enumerate(str_replacements):
            last_rep_to = str_replacements[i - 1].str_to if i > 0 else 0 # helper-data
            sql_str += _._sapi_str[last_rep_to:rep.str_from]            # appending a sapi-segment
            for tok in rep.new_tokens:
                sql_str = TokenTree._add_token_str2(sql_str, tok)        # appending a token of replacement
            if _._if_new_clause_add_newline(sql_str, rep.str_from):
                sql_str += '\n'

        last_rep_to = str_replacements[-1].str_to
        sql_str += _._sapi_str[last_rep_to:]
        return sql_str # + '\n;'
    
    def recursive_str_replacements(_) -> list[_StrReplacement]:
        "used by editor, but not by other parts of parser."
        str_replacements: list[_StrReplacement] = []
        str_replacements += _._str_replacements
        for tok in _.tokens:
            if isinstance(tok, TokenTree):
                str_replacements += tok.recursive_str_replacements()
        return str_replacements

    @staticmethod
    def _add_token_str2(so_far: str, tok: Token) -> str:
        no_space_prefix = [')', ']', '}', '.', ',']
        no_space_suffix = ['(', '[', '{', '.'     ]

        if tok.type in _common_select_clauses:
            so_far = so_far.rstrip(' \n') # remove uncontrolled whitespace and newline
            so_far += '\n' + TokenTree._last_indention(so_far) # add newline and preserve indention
            return so_far + tok.text
        
        elif so_far != "" and so_far[-1] in no_space_suffix: # previous has have no space suffix
            return so_far.rstrip(' ') + tok.text
        elif tok.text in no_space_prefix:
            return so_far.rstrip(' ') + tok.text
        else:
            return (so_far if so_far.endswith(' ') else so_far + ' ') + tok.text
        
    @staticmethod
    def _last_indention(s: str) -> str:
        last_line = s.split('\n')[-1]
        indention_count = 0
        for char in last_line:
            if char == ' ': indention_count += 1
            else: break
        return indention_count * ' '

    def _if_new_clause_add_newline(_, sql_str: str, str_index_from_: int) -> bool:
        if sql_str[-1] == '\n':
            return False
        remainder = _._sapi_str[str_index_from_:].upper()
        common_select_clauses_str = [str(t).lstrip('TokenType.') for t in _common_select_clauses]
        for clause in common_select_clauses_str:
            if remainder.startswith(clause):
                return True
        return False


#endregion --------------------------------------

