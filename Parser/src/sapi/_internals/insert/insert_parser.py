import json
from . import insert_generator
from sapi._internals.token_tree import TokenTree, TokenType
from sapi._internals.db_contact import data_model

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
    tree_name, data = analyze_insert(token_tree)
    if tree_name is not None: # its a tree
        token_tree = insert_generator.generate_insert(tree_name, data)
    return token_tree



def analyze_insert(token_tree: TokenTree) -> tuple[str|None, dict|None]:
    if len(token_tree.tokens) < 6: raise Exception("Cannot have fewer tokens in insert statement, than [insert, into, identifier, values, (, )]")
    token_tree.expect(0, TokenType.INSERT)
    token_tree.expect(1, TokenType.INTO)

    insertable = token_tree.tokens[2].type
    if not data_model.is_tree(insertable):
        return None, None # not a tree
    if token_tree.tokens[3].type == TokenType.L_PAREN: raise Exception(
        f"Expected 'values' found '('. \nHint: Don't specify column names, when inserting into a tree.")
    if token_tree.tokens[3].type == TokenType.SELECT: raise Exception(
        f"Expected 'values' found 'select'. \n'Insert into select from' cannot be used upon trees.")
    token_tree.expect(3, TokenType.VALUES)
    token_tree.expect(4, TokenType.L_PAREN)
    # token_tree.expect(5, TokenType.HEREDOC_STRING)
    if token_tree.tokens[5].type not in _stringtypes: raise Exception(
        f"Expected a json-string. Found '{token_tree.tokens[5].text}', which is not a string, let alone a json-string.")

    value = token_tree.tokens[5].text
    try: data = json.load(value)
    except Exception as e: raise Exception(
        f"Expected a json-string. Found '{value}', which is a string, but not a json-string: "
        f"Json parsing error: {e}")

    if not any(tok.type == TokenType.R_PAREN for tok in token_tree.tokens[6:]): Exception(
        f"Opening brace before values was never closed.")

    # hey, this only works for inserting a single json. expand this into a list of json.
    # well technically a single json can contain a list of json. 

    return insertable, data



# "update tree set tab = json  where ..." should replace a dict / json with a new one, whereever a new value is specified.
# "update tree set col = value where ..." should reduce to a sql update on table(col).
    # its equivalent to "update tree set tab = {col: value} where ..."

# evt. "delete from tree where ..." should remove dicts from a subtree. The where clause may only reference one subtree
# 
