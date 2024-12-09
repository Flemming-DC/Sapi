import json
from . import insert_generator
from sapi._internals.token_tree import TokenType, Token
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
        
        
        
        
        
        
        
        


def parse_insert(tokens: list[Token]) -> str|None:
    data = _analyze_insert(tokens)
    if data is None:
        return None # not a tree insert
    query, args = insert_generator.generate_insert(data)
    return _put_args_into_query(query, args) # not injection safe



def _analyze_insert(tokens: list[Token]) -> dict[list[dict]]|None:
    if len(tokens) < 2: raise QueryError(f"{len(tokens)} is not enough to form a valid insert statement.")
    _expect(tokens[0], TokenType.INSERT)
    if tokens[1].type == TokenType.INTO:
        return None # not a tree insert, just a normal insert

    # _expect(tokens[3], TokenType.VALUES)
    # _expect(tokens[4], TokenType.L_PAREN)
    if tokens[1].type not in _stringtypes: raise QueryError( # allow placeholder
        f"Expected a json-string. Found '{tokens[1].text}', which is not a string, let alone a json-string.")

    json_str = tokens[1].text
    try: data = json.loads(json_str)
    except Exception as e: raise QueryError(
        f"Expected a json-string. Found '{json_str}', which is a string, but not a json-string: "
        f"Json parsing error: {e}")

    # if not any(tok.type == TokenType.R_PAREN for tok in tokens[6:]): QueryError(
    #     f"Opening brace before values was never closed.")

    if len(tokens) > 2: raise QueryError(f"Trailing junk in insert statement.")
    return data


# def _analyze_insert_old(tokens: list[Token]) -> tuple[str|None, dict|None]:
#     if len(tokens) < 6: raise QueryError("Cannot have fewer tokens in insert statement, than [insert, into, identifier, values, (, )]")
#     _expect(tokens[0], TokenType.INSERT)
#     _expect(tokens[1], TokenType.INTO)

#     insertable = tokens[2].text
#     if not data_model.is_tree(insertable):
#         return None, None # not a tree
#     if tokens[3].type == TokenType.L_PAREN: raise QueryError(
#         f"Expected 'values' found '('. \nHint: Don't specify column names, when inserting into a tree.")
#     if tokens[3].type == TokenType.SELECT: raise QueryError(
#         f"Expected 'values' found 'select'. \n'Insert into select from' cannot be used upon trees.")
#     _expect(tokens[3], TokenType.VALUES)
#     _expect(tokens[4], TokenType.L_PAREN)
#     if tokens[5].type not in _stringtypes: raise QueryError( # allow placeholder
#         f"Expected a json-string. Found '{tokens[5].text}', which is not a string, let alone a json-string.")

#     value = tokens[5].text
#     try: data = json.loads(value)
#     except Exception as e: raise QueryError(
#         f"Expected a json-string. Found '{value}', which is a string, but not a json-string: "
#         f"Json parsing error: {e}")

#     if not any(tok.type == TokenType.R_PAREN for tok in tokens[6:]): QueryError(
#         f"Opening brace before values was never closed.")

#     # hey, this only works for inserting a single json. expand this into a list of json.
#     # well technically a single json can contain a list of json. 

#     return insertable, data


def _put_args_into_query(query: str, args: list): # doesnt handle dict args
    for arg in args:
        arg_str = f"'{arg}'" if isinstance(arg, str) else f"{arg}"
        if '%s' not in query: raise CompilerError("too few placeholders in query")
        query = query.replace('%s', arg_str, 1)
    if '%s' in query: raise CompilerError("too many placeholders in query")
    return query


def _expect(token: Token, tok_type: TokenType):
    if token.type != tok_type: raise QueryError(f"Expected '{tok_type.name}' found '{token.text}'")


# "update tree set tab = json  where ..." should replace a dict / json with a new one, whereever a new value is specified.
# "update tree set col = value where ..." should reduce to a sql update on table(col).
    # its equivalent to "update tree set tab = {col: value} where ..."

# evt. "delete from tree where ..." should remove dicts from a subtree. The where clause may only reference one subtree
# 
