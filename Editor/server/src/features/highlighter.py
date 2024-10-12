import operator
from functools import reduce
from enum import IntFlag, auto
from lsprotocol import types as t
from tools.server import server, serverType
# from tools import data_model
import sapi
from sqlglot import TokenType # temp
# from sqlglot.tokens import _ALL_TOKEN_TYPES # temp
from sapi._internals import tokenizer # temp
from dataclasses import dataclass
from tools.log import log
token_type_names = [name for name, type in TokenType.__members__.items()] # temp
if 'TOKEN_TREE' not in token_type_names:
    token_type_names.append('TOKEN_TREE')
    token_type_names.append('keyword')
# log(token_type_names)
# log(_ALL_TOKEN_TYPES)


class TokenModifier(IntFlag):
    # deprecated = auto()
    # readonly = auto()
    # defaultLibrary = auto()
    definition = auto()
modifier_names = [m.name for m in TokenModifier]
# get TokenTypes as list[str] from sapi parser
# also contruct modifier information in parser e.g. via optional out flag


@dataclass
class Token_:
    delta_line: int
    delta_offset: int
    text: str
    tok_type_str: str #= ""
    tok_modifiers: list[TokenModifier] # = field(default_factory=list)


@server.feature(
    t.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    t.SemanticTokensLegend(token_types=token_type_names, token_modifiers=modifier_names)
    )
def semantic_tokens_full(_: serverType, params: t.SemanticTokensParams) -> t.SemanticTokens:
    """Return the semantic tokens for the entire document"""
    # repeated code
    document_uri = params.text_document.uri
    if not document_uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(document_uri)
    # repeated code
    # fal_dataModel = data_model.make_datamodel()
    # if fal_dataModel.is_err():
    #     server.show_message(fal_dataModel.err, t.MessageType.Error)
    #     return []
    
    sapi_code = ''.join([line for line in document.lines])  # .strip('\n\r')
    # line_lengths = [len(line.strip('\n\r')) for line in document.lines]
    line_start_indices: list[int] = []
    last_line_length = 0
    current_line_start_index = 0
    for line in document.lines:
        current_line_start_index += last_line_length
        line_start_indices.append(current_line_start_index)
        last_line_length = len(line)#.strip('\n\r'))# + 1

    tokens = sapi.dialect.postgres().sqlglot_dialect().tokenize(sapi_code) # temp
    tokens_: list[Token_] = []
    last_line = 0
    last_offset = 0
    log([' '.join([f"{t.text}" for t in tokens])])
    for tok in tokens:
        line = tok.line - 1
        log(len(line_start_indices), line, tok)
        
        line_start_index = line_start_indices[line] if line > 0 else 0
        offset = (tok.start - 0) - line_start_index
        # offset = (tok.col - len(tok.text)) # tok.col seems to be tok.end.offset - indention_of_line
        # log(f"offset: {tok.text}, {offset}, {old_offset}")
        if offset < 0:
            log(tok.start, line_start_index, line, line_start_indices)
            raise Exception("offset < 0")
        # if tok.token_type in tokenizer._keywords:
        #     log(f"{tok.token_type.name}: {tok.text}, {line}, {tok.start - 1}, {offset}")
        # start
        # line_length = line_lengths[i]
        _delta_line = line - last_line
        _delta_offset = offset - last_offset if _delta_line == 0 else offset
        if _delta_line < 0:
            raise Exception("_delta_line < 0")
        if _delta_offset < 0:
            raise Exception("_delta_offset < 0")
        # log(f"{type(tok.line)}, {type(last_line)}, {type(_delta_line)}, {type(_delta_offset)}")

        tok_ = Token_(
            delta_line = _delta_line,
            delta_offset = _delta_offset,
            text = tok.text,
            # tok_type_str = 'keyword' if tok.token_type.name == 'WITH' else tok.token_type.name,
            tok_type_str = 'keyword' if tok.token_type in tokenizer._keywords else tok.token_type.name,
            tok_modifiers = [], # no modifiers to begin with
            )
        tokens_.append(tok_)
        if last_line > line:# or last_offset > offset:
            raise Exception(f"{last_line} > {line}")# or {last_offset} > {offset}")
        last_line = line
        last_offset = offset

    data = []
    for tok_ in tokens_:
        if tok_.tok_type_str  == 'keyword':
            a = (
                tok_.delta_line,
                tok_.delta_offset,
                len(tok_.text),
                token_type_names.index(tok_.tok_type_str), # returns index into token_type_names
                reduce(operator.or_, tok_.tok_modifiers, 0), # returns bitmap into modifier_names)}, {tok.line}, {tok.start}")
            )
            log(f"{tok_.tok_type_str}: {tok_.text}, {a}")
        # log(f"{tok_.tok_type}: {tok_.tok_type in token_type_names} "
        #     f"{tok_.tok_type.lower() in token_type_names} {tok_.tok_type.upper() in token_type_names}")
        data.extend(
            [
                tok_.delta_line,
                tok_.delta_offset,
                len(tok_.text),
                token_type_names.index(tok_.tok_type_str), # returns index into token_type_names
                reduce(operator.or_, tok_.tok_modifiers, 0), # returns bitmap into modifier_names
            ]
        )
    log('\n')

    return t.SemanticTokens(data=data)


# get tokens
# loop over tokens and color by TokenType
# indications of nullability, triggers, checks and no-access comes later and elsewhere.
# autocompletion is later and elsewhere.
# embddedment is also later and elsewhere.
# hinting autogenerated text is in another file. it can also be toggled on/off in settings

# ----------- colors -------------
# keywords, identifiers, parameter (e.g. var), literals, strings, comments, types, 
# comma, brackets, operators, functions, errors, default for unrecognized
# evt. give separate colors to schema, tree, table, column, view, aliases
# 

# ----------- ChatGPT suggests ----------- #
# Bad Token: #FF0000 (bright red) – typically indicates errors or invalid tokens.
# Braces: #A9B7C6 (light gray-blue) – for {} characters.
# Brackets: #A9B7C6 (light gray-blue) – for [] characters.
# Column: #9876AA (light purple) – for database column names.
# Comma: #A9B7C6 (light gray-blue) – for commas , in code.
# Comment: #808080 or #629755 (grayish-green) – for comments in SQL or other code.
# Database Object: #CC7832 (orange) – for database objects such as tables, views, etc.
# Dot: #A9B7C6 (light gray-blue) – for dots . in expressions.
# External Command: #9876AA (light purple) – for external references or commands.
# Keyword: #CC7832 (orange) – for SQL keywords like SELECT, FROM, WHERE.
# Label: #E8BF6A (light yellow) – for labels used in procedures or loops.
# Number Token: #6897BB (light blue) – for numeric literals like 123, 1.23.
# Outer Query Column: #9876AA (light purple) – for columns used in outer queries.
# Parameter: #9876AA (light purple) – for SQL parameters (e.g., in prepared statements).
# Parenthesis: #A9B7C6 (light gray-blue) – for () characters.
# Procedure or Function: #FFC66D (light orange) – for procedure or function names.
# Schema: #9876AA (light purple) – for schema names in fully qualified names.
# Semicolon: #A9B7C6 (light gray-blue) – for semicolons ; in SQL or other code.
# String Token: #6A8759 (green) – for string literals like 'text', "text".
# Synthetic Entity: #A9B7C6 (light gray-blue) – for system-generated entities.
# Table: #FFC66D (light orange) – for table names in SQL queries.
# Table or Columns Alias: #9876AA (light purple) – for aliases in SQL queries.
# Type: #CC7832 (orange) – for SQL types like VARCHAR, INT, DATE.
# Variable: #9876AA (light purple) – for variables in SQL procedures or scripts.


# ----------- Junk ----------- #

    # tok_trees = sapi.parse(sapi_query, fal_dataModel.ok, list[TokenTree]) # try-parse

    ## get tokens from tok_trees
    # tokens: list[Token_] = []
    # last_line = 0
    # last_offset = 0
    # for tok_tree in tok_trees: # should tok trees be sorted?
    #     log(f"tok_tree: {tok_tree.line}, {tok_tree.start}")
    #     log([' '.join([f"{t.text}" for t in tok_tree.tokens])])
    #     for tok in tok_tree.tokens:
    #         log(f"{tok.token_type.name}: {tok.text}, {tok.line}, {tok.start}")
    #         tok_ = Token_(
    #             delta_line = tok.line - last_line,
    #             delta_offset = tok.start - last_offset,
    #             text = tok.text,
    #             tok_type = 'keyword' if tok.token_type in tokenizer._keywords else tok.text,
    #             tok_modifiers = [], # no modifiers to begin with
    #             )
    #         tokens.append(tok_)
    #         if last_line > tok.line or last_offset > tok.start:
    #             raise Exception(f"{last_line} > {tok.line} or {last_offset} > {tok.start}")
    #         last_line = tok.line
    #         last_offset = tok.start
            
        # tokens.extend([Token_(
        #     delta_line = tok.line,
        #     delta_offset = tok.start,
        #     text = tok.text,
        #     tok_type = 'keyword' if tok.token_type in _keywords else tok.text,
        #     tok_modifiers = [], # no modifiers to begin with
        # ) for tok in tok_tree.tokens])
    # __slots__ = ("token_type", "text", "line", "col", "start", "end", "comments")

        # log(token)
        # Token(line=12, offset=228, text='col0_1', tok_type='VAR', tok_modifiers=[])
        # Token(line=<Token token_type: TokenType.VAR, text: col0_1, line: 12, col: 36, start: 228, end: None, comments: []>, 
        # offset=238, text='JOIN', tok_type='JOIN', tok_modifiers=[])
        # bullshit! thats not a line number.
        
        # 'keyword' if tok.token_type in _keywords else tok.text
                        # Token(
                        #     line=current_line - prev_line,
                        #     offset=current_offset - prev_offset,
                        #     text=match.group(0),
                        #     tok_