import json
from collections import namedtuple
from . import insert_generator
from sapi._internals.token_tree import TokenTree, TokenType, Token
from sapi._internals.db_contact import data_model
from sapi._internals.error import CompilerError, QueryError

_stringtypes = { # dont dublicate this with editor_tok.py
    TokenType.BIT_STRING,
    TokenType.HEX_STRING,
    TokenType.BYTE_STRING,
    TokenType.NATIONAL_STRING,
    TokenType.RAW_STRING,
    TokenType.HEREDOC_STRING,
    TokenType.UNICODE_STRING,
    TokenType.STRING,
}


def parse_insert(token_tree: TokenTree) -> TokenTree:
    tree_name, data = _analyze_insert(token_tree)
    if tree_name is not None: # its a tree
        query, args = insert_generator.generate_insert(data)
        token_tree = _to_token_tree(token_tree, query, args)

    return token_tree



def _analyze_insert(token_tree: TokenTree) -> tuple[str|None, dict|None]:
    if len(token_tree.tokens) < 6: raise QueryError("Cannot have fewer tokens in insert statement, than [insert, into, identifier, values, (, )]")
    token_tree.expect(0, TokenType.INSERT)
    token_tree.expect(1, TokenType.INTO)

    insertable = token_tree.tokens[2].text
    if not data_model.is_tree(insertable):
        return None, None # not a tree
    if token_tree.tokens[3].type == TokenType.L_PAREN: raise QueryError(
        f"Expected 'values' found '('. \nHint: Don't specify column names, when inserting into a tree.")
    if token_tree.tokens[3].type == TokenType.SELECT: raise QueryError(
        f"Expected 'values' found 'select'. \n'Insert into select from' cannot be used upon trees.")
    token_tree.expect(3, TokenType.VALUES)
    token_tree.expect(4, TokenType.L_PAREN)
    # token_tree.expect(5, TokenType.HEREDOC_STRING)
    if token_tree.tokens[5].type not in _stringtypes: raise QueryError( # allow placeholder
        f"Expected a json-string. Found '{token_tree.tokens[5].text}', which is not a string, let alone a json-string.")

    value = token_tree.tokens[5].text
    try: data = json.loads(value)
    except Exception as e: raise QueryError(
        f"Expected a json-string. Found '{value}', which is a string, but not a json-string: "
        f"Json parsing error: {e}")

    if not any(tok.type == TokenType.R_PAREN for tok in token_tree.tokens[6:]): QueryError(
        f"Opening brace before values was never closed.")

    # hey, this only works for inserting a single json. expand this into a list of json.
    # well technically a single json can contain a list of json. 

    return insertable, data



def _to_token_tree(token_tree: TokenTree, query, args):
    def _put_args_into_query(query: str, args: list): # doesnt handle dict args
        for arg in args:
            arg_str = f"'{arg}'" if isinstance(arg, str) else f"{arg}"
            if '%s' not in query: raise CompilerError("too few placeholders in query")
            query = query.replace('%s', arg_str, 1)
        if '%s' in query: raise CompilerError("too many placeholders in query")
        return query
    query = _put_args_into_query(query, args) # not injection safe

    TokenType.TREE_INSERT = namedtuple('fake_enum_variant', ['name', 'value'])(name='TREE_INSERT', value='TREE_INSERT')
    token = Token(TokenType.TREE_INSERT, query, token_tree.line, token_tree.start, None)
    token_tree = TokenTree([token], query, token_tree._next_token) # private var access?
    # alternative
    # last_index = len(token_tree.tokens) - 1
    # token_tree.replace(0, last_index, [token])
    return token_tree


# "update tree set tab = json  where ..." should replace a dict / json with a new one, whereever a new value is specified.
# "update tree set col = value where ..." should reduce to a sql update on table(col).
    # its equivalent to "update tree set tab = {col: value} where ..."

# evt. "delete from tree where ..." should remove dicts from a subtree. The where clause may only reference one subtree
# 
