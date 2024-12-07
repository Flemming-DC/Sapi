# from sqlglot import Dialect
from sqlglot.tokens import Token as glotToken
from .token_tree import TokenTree, TokenType, Token
from .db_contact import data_model
from sapi._internals.error import CompilerError, QueryError


def tokenize(sapi_stmt: str) -> TokenTree|None:
    # tokens is a list of builtins.token, which seems to behave like sqlglot-Token, except for type checks.
    glot_tokens: list[glotToken] = data_model.dialect().sqlglot_dialect().tokenize(sapi_stmt) 
    # cast to our own Token class and drop useless and / or unreliable data from raw_tokens
    tokens: list[Token] = [Token(t.token_type, t.text, t.line, t.start, t.end) for t in glot_tokens]
    _cut_leading_junk(tokens)
    if tokens == []: return None
    tree, _ = _make_nested_tok_tree(tokens, 0, sapi_stmt)
    return tree

    


def _make_nested_tok_tree(all_tokens: list[Token], i: int, sapi_str: str) -> tuple[TokenTree, int]:
    if all_tokens[i].type == TokenType.L_PAREN:
        raise (QueryError if i == 0 else CompilerError)("TokenTree should not start with (") 
    depth = 0 # parenthesis nesting depth
    token_count = len(all_tokens)
    tokens_at_this_level: list[Token] = []

    def _continue(i: int, depth: int): 
        if i >= token_count: 
            return False
        depth_goes_negative = (all_tokens[i].type == TokenType.R_PAREN and depth <= 0)
        return all_tokens[i].type != TokenType.SEMICOLON and not depth_goes_negative
       
    
    while _continue(i, depth):
        token = all_tokens[i]
        match token.type:
            case TokenType.L_PAREN: depth += 1 # evt. check if next token if a sub query start
            case TokenType.R_PAREN: depth -= 1
            # case TokenType.SEMICOLON: depth = -1000 # exit tokentree
            case TokenType.SELECT | TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE: 
                if depth > 0: # we don't want to recursively parse the outermost select
                    sub_tree, i = _make_nested_tok_tree(all_tokens, i, sapi_str)
                    token = sub_tree
        tokens_at_this_level.append(token) # token can be overridden by a sub_tree
        i += 1
    if i < len(all_tokens) and all_tokens[i].type == TokenType.R_PAREN:
        i -= 1 # dont include finishing parenthesis
    next_token = Token(**all_tokens[i + 1].__dict__) if i + 1 < len(all_tokens) else None
    # if next_token is not None and next_token.line > all_tokens[i].line:
    #     next_token.line = all_tokens[i].line
    # make single layer of token_tree
    token_tree = TokenTree(tokens_at_this_level, sapi_str, next_token)
    return token_tree, i


def _cut_leading_junk(tokens: list[Token]):
    for i, tok in enumerate(tokens):
        if tok.type in _keywords:
            tokens = tokens[i:] # modifying list is ok, since we break the loop
            return

def keywords(): return _keywords

_keywords = {
    TokenType.ALIAS,
    TokenType.ALTER,
    TokenType.ALWAYS,
    TokenType.ALL,
    TokenType.ANTI,
    TokenType.ANY,
    TokenType.APPLY,
    TokenType.ARRAY,
    TokenType.ASC,
    TokenType.ASOF,
    TokenType.AUTO_INCREMENT,
    TokenType.BEGIN,
    TokenType.BETWEEN,
    TokenType.CACHE,
    TokenType.CASE,
    TokenType.CHARACTER_SET,
    TokenType.CLUSTER_BY,
    TokenType.COLLATE,
    TokenType.COMMAND,
    TokenType.COMMENT,
    TokenType.COMMIT,
    TokenType.CONNECT_BY,
    TokenType.CONSTRAINT,
    TokenType.COPY,
    TokenType.CREATE,
    TokenType.CROSS,
    TokenType.CUBE,
    TokenType.CURRENT_DATE,
    TokenType.CURRENT_DATETIME,
    TokenType.CURRENT_TIME,
    TokenType.CURRENT_TIMESTAMP,
    TokenType.CURRENT_USER,
    TokenType.DECLARE,
    TokenType.DEFAULT,
    TokenType.DELETE,
    TokenType.DESC,
    TokenType.DESCRIBE,
    TokenType.DICTIONARY,
    TokenType.DISTINCT,
    TokenType.DISTRIBUTE_BY,
    TokenType.DIV,
    TokenType.DROP,
    TokenType.ELSE,
    TokenType.END,
    TokenType.ESCAPE,
    TokenType.EXCEPT,
    TokenType.EXECUTE,
    TokenType.EXISTS,
    TokenType.FALSE,
    TokenType.FETCH,
    TokenType.FILTER,
    TokenType.FINAL,
    TokenType.FIRST,
    TokenType.FOR,
    TokenType.FORCE,
    TokenType.FOREIGN_KEY,
    TokenType.FORMAT,
    TokenType.FROM,
    TokenType.FULL,
    TokenType.FUNCTION,
    TokenType.GLOB,
    TokenType.GLOBAL,
    TokenType.GRANT,
    TokenType.GROUP_BY,
    TokenType.GROUPING_SETS,
    TokenType.HAVING,
    TokenType.HINT,
    TokenType.IGNORE,
    TokenType.ILIKE,
    TokenType.ILIKE_ANY,
    TokenType.IN,
    TokenType.INDEX,
    TokenType.INNER,
    TokenType.INSERT,
    TokenType.INTERSECT,
    TokenType.INTERVAL,
    TokenType.INTO,
    TokenType.INTRODUCER,
    TokenType.IRLIKE,
    TokenType.IS,
    TokenType.ISNULL,
    TokenType.JOIN,
    TokenType.JOIN_MARKER,
    TokenType.KEEP,
    TokenType.KEY,
    TokenType.KILL,
    TokenType.LANGUAGE,
    TokenType.LATERAL,
    TokenType.LEFT,
    TokenType.LIKE,
    TokenType.LIKE_ANY,
    TokenType.LIMIT,
    TokenType.LIST,
    TokenType.LOAD,
    TokenType.LOCK,
    TokenType.MAP,
    TokenType.MATCH_CONDITION,
    TokenType.MATCH_RECOGNIZE,
    TokenType.MEMBER_OF,
    TokenType.MERGE,
    TokenType.MOD,
    TokenType.MODEL,
    TokenType.NATURAL,
    TokenType.NEXT,
    TokenType.NOTNULL,
    TokenType.NULL,
    TokenType.OBJECT_IDENTIFIER,
    TokenType.OFFSET,
    TokenType.ON,
    TokenType.ONLY,
    TokenType.OPERATOR,
    TokenType.ORDER_BY,
    TokenType.ORDER_SIBLINGS_BY,
    TokenType.ORDERED,
    TokenType.ORDINALITY,
    TokenType.OUTER,
    TokenType.OVER,
    TokenType.OVERLAPS,
    TokenType.OVERWRITE,
    TokenType.PARTITION,
    TokenType.PARTITION_BY,
    TokenType.PERCENT,
    TokenType.PIVOT,
    TokenType.PLACEHOLDER,
    TokenType.POSITIONAL,
    TokenType.PRAGMA,
    TokenType.PREWHERE,
    TokenType.PRIMARY_KEY,
    TokenType.PROCEDURE,
    TokenType.PROPERTIES,
    TokenType.PSEUDO_TYPE,
    TokenType.QUALIFY,
    TokenType.QUOTE,
    TokenType.RANGE,
    TokenType.RECURSIVE,
    TokenType.REFRESH,
    TokenType.RENAME,
    TokenType.REPLACE,
    TokenType.RETURNING,
    TokenType.REFERENCES,
    TokenType.RIGHT,
    TokenType.RLIKE,
    TokenType.ROLLBACK,
    TokenType.ROLLUP,
    TokenType.ROW,
    TokenType.ROWS,
    TokenType.SELECT,
    TokenType.SEMI,
    TokenType.SEPARATOR,
    TokenType.SEQUENCE,
    TokenType.SERDE_PROPERTIES,
    TokenType.SET,
    TokenType.SETTINGS,
    TokenType.SHOW,
    TokenType.SIMILAR_TO,
    TokenType.SOME,
    TokenType.SORT_BY,
    TokenType.START_WITH,
    TokenType.STORAGE_INTEGRATION,
    TokenType.STRAIGHT_JOIN,
    TokenType.STRUCT,
    TokenType.SUMMARIZE,
    TokenType.TABLE_SAMPLE,
    TokenType.TAG,
    TokenType.TEMPORARY,
    TokenType.TOP,
    TokenType.THEN,
    TokenType.TRUE,
    TokenType.TRUNCATE,
    TokenType.UNCACHE,
    TokenType.UNION,
    TokenType.UNNEST,
    TokenType.UNPIVOT,
    TokenType.UPDATE,
    TokenType.USE,
    TokenType.USING,
    TokenType.VALUES,
    TokenType.VIEW,
    TokenType.VOLATILE,
    TokenType.WHEN,
    TokenType.WHERE,
    TokenType.WINDOW,
    TokenType.WITH,
    TokenType.UNIQUE,
    TokenType.VERSION_SNAPSHOT,
    TokenType.TIMESTAMP_SNAPSHOT,
    TokenType.OPTION,
}


