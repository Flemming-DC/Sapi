from __future__ import annotations
from dataclasses import dataclass, field
from sqlglot.tokens import auto
from sqlglot.tokens import TokenType, Token
# from sqlglot.expressions import Expression, Select, Insert, Update, Delete, Column, Table, Create, Drop, With # many kinds of alter 



TokenType.TOKEN_TREE = auto()
_TOKENTYPE_TOKEN_TREE = TokenType.TOKEN_TREE
# TokenType.AUTO_JOIN = auto() # token type for an auto generated collection of join clauses. A fairly big token, I must admit.
# TOKENTYPE_AUTO_JOIN = TokenType.AUTO_JOIN

class ParserError(Exception): ...

@dataclass 
class _StrReplacement:
    str_from_: int
    str_to: int
    new_tokens: list[Token]

class AutoToken(Token):...

common_select_clauses = [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
    TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]

@dataclass
class TokenTree:
    tokens: list[Token|TokenTree] # variable
    _sapi_str: str # const (evt. only store at the root tree) # contains sapi code for one statement
    _next_token: Token|None # const
    _str_replacements: list[_StrReplacement] = field(default_factory=list) # variable

    #region ---------- Token ---------- 
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
    #endregion -------------------------------------- 

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
        width = 0 if to == from_ else len(from_tok.text) # this line imposes the restriction of removing at most one token at a time
        str_to = str_from + width
        # new_str = ' '.join(t.text for t in new_tokens)

        # str_from -= _.tokens[0].start
        # str_to -= _.tokens[0].start
        _._str_replacements.append(_StrReplacement(str_from, str_to, new_tokens))

        # modify tokens
        _.tokens[from_:to] = new_tokens


#region -------------- cast to str --------------

    def __str__(_) -> str:
        if len(_._sapi_str.split(' ')) < 6:
            ...
        # collect replacements in subtrees
        str_replacements = _._str_replacements
        for tok in _.tokens:
            if isinstance(tok, TokenTree):
                str_replacements += tok._str_replacements
        # handle the None case
        if not str_replacements:
            return _._sapi_str

        # make string
        # sql_str is on the form: 
        #   sapi-segment + replacement +
        #   ...
        #   sapi-segment + replacement +
        #   sapi-segment 
        sql_str = ""
        str_replacements.sort(key = lambda r: r.str_from_)
        for i, rep in enumerate(str_replacements):
            last_rep_to = str_replacements[i - 1].str_to if i > 0 else 0 # helper-data
            sql_str += _._sapi_str[last_rep_to:rep.str_from_]            # appending a sapi-segment
            for tok in rep.new_tokens:
                sql_str = TokenTree._add_token_str2(sql_str, tok)        # appending a token of replacement
            if _._if_new_clause_add_newline(sql_str, rep.str_from_):
                sql_str += '\n'

        last_rep_to = str_replacements[-1].str_to
        sql_str += _._sapi_str[last_rep_to:]
        return sql_str
    
    
    @staticmethod
    def _add_token_str2(so_far: str, tok: Token) -> str:
        no_space_prefix = [')', ']', '}', '.', ',']
        no_space_suffix = ['(', '[', '{', '.'     ]

        if tok.token_type in common_select_clauses:
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
        common_select_clauses_str = [str(t).lstrip('TokenType.') for t in common_select_clauses]
        for clause in common_select_clauses_str:
            if remainder.startswith(clause):
                return True
        return False


#endregion --------------------------------------

