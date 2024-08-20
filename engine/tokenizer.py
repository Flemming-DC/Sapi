from __future__ import annotations
from textwrap import indent
from dataclasses import dataclass, field
from sqlglot import Dialect
from sqlglot.tokens import Token, TokenType, auto
# from sqlglot.expressions import Expression, Select, Insert, Update, Delete, Column, Table, Create, Drop, With # many kinds of alter 

TokenType.TOKEN_TREE = auto()
TokenType.AUTO_JOIN = auto() # token type for an auto generated collection of join clauses. A fairly big token, I must admit.
_TOKENTYPE_TOKEN_TREE = TokenType.TOKEN_TREE
TOKENTYPE_AUTO_JOIN = TokenType.AUTO_JOIN


_dialect = Dialect.get_or_raise("postgres") # dialect gribes fra et config object
# dette skiller tokenizing og parsing ad
class SyntaxError(Exception): ...
class ParserError(Exception): ...


@dataclass
class TokenTree:
    # a token was <class 'builtins.Token'>. Get control over their types
    tokens: list[Token|TokenTree] = field(default_factory=list) # = []

    # make TokenTree compatible with Token
    token_type: TokenType = _TOKENTYPE_TOKEN_TREE
    @property 
    def text(self): return "[SubTree]" # str(self)
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
        clauses = [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, 
                    TokenType.RIGHT, TokenType.OUTER, TokenType.WHERE, 
                    TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]
        s = '['
        for tok in self.tokens:
            if isinstance(tok, TokenTree):
                # s += indent(repr(tok), '    ').lstrip()
                s += tok.text + ' '
            elif tok.token_type in clauses:
                s += '\n' + tok.text + ' '
            elif tok.text == '.':
                s = s.rstrip(' ')
                s += tok.text
            elif tok.text in ['(', '[', '{']:
                s += tok.text
            elif tok.text in [',', ')', ']', '}']:
                s = s.rstrip(' ')
                s += tok.text + ' '
            else:
                s += tok.text + ' '
        s = s.rstrip(' ')
        s += ']'
        return s

    # def first_leaf(self):
    #     for token in self.tokens:
    #         if not isinstance(token, TokenTree):
    #             return token
    #     raise ParserError(f"TokenTree contains no leaf tokens. This is unexpected: \n {self}")

    # def leaves(self) -> Iterator[Token]:
    #     for tok in self.tokens:
    #         if not isinstance(tok, TokenTree):
    #             yield tok

    # def sub_trees(self) -> Iterator[TokenTree]:
    #     for tok in self.tokens:
    #         if isinstance(tok, TokenTree):
    #             yield tok


def tokenize(sapi: str) -> list[TokenTree]:
    tokens: list[Token] = _dialect.tokenize(sapi)

    i = 0
    trees: list[TokenTree] = []
    while i < len(tokens) - 1:
        token_tree, i = _parse_token_tree(tokens, i)
        trees.append(token_tree)
        i += 1
    
    return trees

    


def _parse_token_tree(tokens: list[Token], i: int) -> tuple[TokenTree, int]:
    if tokens[i].token_type == TokenType.L_PAREN:
        _raise_parse_error("TokenTree must not start with (") 
    token_tree = TokenTree()
    depth = 0 # parenthesis nesting depth
    token_count = len(tokens)
    def continue_(i: int, depth: int): 
        if i >= token_count: 
            return False
        depth_goes_negative = (tokens[i].token_type == TokenType.R_PAREN and depth == 0)
        return tokens[i].token_type != TokenType.SEMICOLON and not depth_goes_negative
        # depth_goes_negative = tokens[i].token_type == TokenType.R_PAREN and depth == 0
        # return depth >= 0 and i < token_count and tokens[i].token_type != TokenType.SEMICOLON
        # return (i < token_count and tokens[i].token_type != TokenType.SEMICOLON 
        #     and not (tokens[i].token_type == TokenType.R_PAREN and depth == 0))
    
    while continue_(i, depth):
        token = tokens[i]
        match token.token_type:
            case TokenType.L_PAREN: depth += 1 # evt. check if next token if a sub query start
            case TokenType.R_PAREN: depth -= 1
            case TokenType.SELECT | TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE: 
                if depth > 0: # we don't want to recursively parse the outermost select
                    token, i = _parse_token_tree(tokens, i)
        token_tree.tokens.append(token) # token can be overridden by a sub_tree
        # if continue_(i, depth):
        #     i += 1
        i += 1
    i -= 1 # dont include finishing parenthesis
    return token_tree, i



def _replace_from_with_not_from(sapi_str: str, tokens: list[Token]):
    pieces: list[str] = []
    last_piece_index = 0
    replacement = "not_from"
    for token in tokens:
        if token.token_type == TokenType.FROM:
            pieces.append(sapi_str[last_piece_index: token.start])
            pieces.append(replacement)
            last_piece_index = token.end + 1
    
    sql_str = ''.join(pieces)
    return sql_str


def _raise_parse_error(tokens: list[Token], i: int, msg: str) -> str:
    code_str = ' '.join(t.text for t in tokens[:i + 1])
    msg_tot = f'\nParserError: {code_str}...\n {msg}'
    raise ParserError(msg_tot)
    

def _raise_syntax_error(tokens: list[Token], i: int, msg: str) -> str:
    code_str = ' '.join(t.text for t in tokens[:i + 1])
    msg_tot = f'\nSyntaxError: {code_str}...\n {msg}'
    raise SyntaxError(msg_tot)


def flat_tokenize(code: str) -> list[Token]: # probably going to become dead code
    return _dialect.tokenize(code)


if __name__ == '__main__':
    q = """
        with cte as (SELECT a2.* from g)
        SELECT 1, a1.*, a2_2
        from g
        /*
        comment
        comment
        */
        join cte using (k)
        where a2_2 != 0 -- comment
        ;
        /*
        comment
        comment
        */
        SELECT 1
        """
    # trees = tokenize(q)

    q = "SELECT $few$This isn't a date$few$"
    # trees = tokenize(q)

    q = """
    WITH cte AS (
      SELECT i, sh FROM tab_in_cte
    ) -- comment
    -- comment
    /* comments
    comments */
    /* comments
    comments */
    -- comment
    SELECT 
        sh,
        o,
        (SELECT su FROM sub)
    FROM cte 
    join outer_tab using (k)
    ;

    select 1"""
    trees = tokenize(q)

    for tr in trees:
        print("--- tree ---")
        print(tr)

