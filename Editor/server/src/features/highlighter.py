import operator
from typing import Type
from functools import reduce
from enum import IntFlag, auto
from lsprotocol import types as t
from tools.server import server, serverType
from sapi import _editor_tok
from dataclasses import dataclass
from tools.log import log
from tools.settings import Settings
from tools import error
from sqlglot.tokens import Token as GlotToken, TokenType as GlotType

class _TokenModifier(IntFlag):
    definition = auto()

@dataclass
class _EditorToken:
    delta_line: int
    delta_offset: int
    text: str
    type_str: str
    modifiers: list[_TokenModifier]

@dataclass
class _EditorAbsToken:
    line: int
    offset: int
    text: str
    type_str: str
    modifiers: list[_TokenModifier]

_COMMENT = 'COMMENT'

@server.feature(
    t.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    t.SemanticTokensLegend(token_types=_editor_tok.token_type_names(), 
                           token_modifiers=[m.name for m in _TokenModifier])
    )
@error.as_popup
def semantic_tokens_full(_: serverType, params: t.SemanticTokensParams) -> t.SemanticTokens | None:
    """Return the semantic tokens for the entire document"""
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return None
    document = server.workspace.get_text_document(uri)
    sapi_code = document.source
    # log('----')
    # log(server.client_capabilities)
    # log('----')

    
    # editor_abs_tokens = _little_tokenize(sapi_code)
    # return _semantic_tokens([])
    editor_abs_tokens = _tokenize(sapi_code)
    editor_rel_tokens = _editor_rel_tokens(editor_abs_tokens)
    return _semantic_tokens(editor_rel_tokens)

    # line_start_indices = _line_start_indices(document.lines)
    # glot_tokens = Settings.load_database().dialect.sqlglot_dialect().tokenize(sapi_code)
    # # glot_tokens = _glot_tokens_including_comments(sapi_code, line_start_indices, len(sapi_code) - 1)
    # line_start_indices = _line_start_indices(document.lines)
    # editor_tokens = _editor_tokens(glot_tokens, sapi_code, line_start_indices)
    # return _semantic_tokens(editor_tokens)
    



def _line_start_indices(lines: list[str]) -> list[int]:
    line_start_indices = []
    last_line_length = 0
    current_line_start_index = 0
    for line in lines:
        current_line_start_index += last_line_length
        line_start_indices.append(current_line_start_index)
        last_line_length = len(line)#.strip('\n\r'))# + 1
    return line_start_indices


# class _ExtGlotToken:
#     token_type
#     text = None, # unused. could be set to sapi_code[last_end : tok.start]
#     line = start_line(tok.start, tok.line), # line where comment ends and the next tok starts.
#     col = None, # unused
#     start = last_end,
#     end = tok.start,


def _tokenize(sapi_code: str) -> list[_EditorAbsToken]:
    glot_dialect = Settings.load_database().dialect.sqlglot_dialect()
    glot_tokens = glot_dialect.tokenize(sapi_code)
    comment_markers: list[str | tuple[str, str]] = glot_dialect.tokenizer.COMMENTS
    if len(glot_tokens) == 0: 
        return

    next_glot_tok_idx: int = 0
    
    
    # check that comment_markers are in [1_char_single_line, 2_char_single_line, 2_char_multi_line ]
    
    # '--', '#', '#!', '//'
    # ('/*', '*/')
    single_line_1_char_comment_markers = [m for m in comment_markers if isinstance(m, str) and len(m) == 1]
    single_line_2_char_comment_markers = [m for m in comment_markers if isinstance(m, str) and len(m) == 2]
    # multi_line_comment_marker_pairs = [mp for mp in comment_markers if isinstance(mp, tuple)]
    # multi_line_comment_start_markers = [mp[0] for mp in multi_line_comment_marker_pairs]
    multi_line_comment_end_by_start_markers = {mp[0]: mp[1] for mp in comment_markers if isinstance(mp, tuple)}
    line_nr = 0
    line_start_index = 0
    editor_tokens: list[_EditorAbsToken] = [] # just go directly to editor tokens, since you anyway have to recalculate. 
    i = 0
    count = len(sapi_code)
    def char(i: int): return sapi_code[i]
    def two_char(i: int): return sapi_code[i] + (sapi_code[i + 1] if i + 1 < count else '')
    while i < count:
        next_glot_tok: GlotToken = glot_tokens[next_glot_tok_idx] if next_glot_tok_idx < len(glot_tokens) else None
        editor_tok = editor_tokens[-1] if editor_tokens != [] else None

        if next_glot_tok and i == next_glot_tok.start:
            # eat to end_index and collect glot_token, seperately for each line
            next_glot_tok_idx += 1
            stuff_start = i, line_nr, line_start_index
            while i < next_glot_tok.end and i < count: 
                i += 1
                if char(i) == '\n':
                    stuff_end = i, line_nr, line_start_index
                    editor_tok = _make_editor_token(sapi_code, next_glot_tok.token_type, stuff_start, stuff_end, editor_tok)
                    editor_tokens.append(editor_tok)
                    line_nr += 1
                    line_start_index = i + 1
                    i += 1
                    stuff_start = i, line_nr, line_start_index
            # if i > stuff_start[0]:
            stuff_end = i, line_nr, line_start_index
            editor_tok = _make_editor_token(sapi_code, next_glot_tok.token_type, stuff_start, stuff_end, editor_tok)
            editor_tokens.append(editor_tok)
        elif char(i) in single_line_1_char_comment_markers or two_char(i) in single_line_2_char_comment_markers:
            # eat to end of line and collect comment_token
            stuff_start = i, line_nr, line_start_index
            while char(i) != '\n' and i < count: 
                i += 1
            stuff_end = i, line_nr, line_start_index
            editor_tok = _make_editor_token(sapi_code, None, stuff_start, stuff_end, editor_tok)
            editor_tokens.append(editor_tok)

            line_nr += 1
            line_start_index = i + 1
            # i += 1
        elif two_char(i) in multi_line_comment_end_by_start_markers.keys():
            # eat to end marker and collect comment_token, seperately for each line
            stuff_start = i, line_nr, line_start_index
            end_marker = multi_line_comment_end_by_start_markers[two_char(i)]
            while two_char(i) != end_marker and i < count: 
                i += 1
                if char(i) == '\n':
                    stuff_end = i, line_nr, line_start_index
                    editor_tok = _make_editor_token(sapi_code, None, stuff_start, stuff_end, editor_tok)
                    editor_tokens.append(editor_tok)
                    line_nr += 1
                    line_start_index = i + 1
                    i += 1
                    stuff_start = i, line_nr, line_start_index
            i += 1 # end_marker is two characters long, so we make an extra step
            # if i > stuff_start[0]:
            stuff_end = i, line_nr, line_start_index
            editor_tok = _make_editor_token(sapi_code, None, stuff_start, stuff_end, editor_tok)
            editor_tokens.append(editor_tok)
        elif char(i) == '\n':
            line_nr += 1
            line_start_index = i + 1
        
        i += 1
        
        
        # match next_tok start_index: eat to end_index and collect glot_token, seperately for each line
        # match single_line_comment_markers: eat to end of line and collect comment_token
        # match multi_line_comment_start_markers: eat to end marker and collect comment_token, seperately for each line
        # match \n: eat \n and update line_nr, line_start_index
    
    return editor_tokens

def _make_editor_token(sapi_code: str, glot_type: GlotType|None,
                       stuff_start: tuple[int, int, int], stuff_end: tuple[int, int, int],
                       last_line, 
        ) -> _EditorAbsToken:
    index_start, line_nr_start, line_start_index_start = stuff_start
    index_end, line_nr_end, line_start_index_end = stuff_end
    if line_nr_end != line_nr_start or line_start_index_start != line_start_index_end:
        raise Exception("differences in line_nr should have been resolved by now")
    line_nr = line_nr_start
    line_start_index = line_start_index_start
    offset = index_start - line_start_index
    if offset < 0:
        raise Exception(f"offset < 0: {offset} = {index_start} - {line_start_index}")

    tok = _EditorAbsToken(
        line = line_nr,
        offset = offset,
        text = sapi_code[index_start : index_end + 1].strip('\r\n'), 
        type_str = _editor_tok.get_group_names(glot_type if glot_type else _COMMENT),
        modifiers = [], # no modifiers to begin with
        ) # ok
    return tok # bad


def _editor_rel_tokens(editor_abs_tokens: list[_EditorAbsToken]) -> list[_EditorToken]:
    editor_rel_tokens: list[_EditorToken] = []
    last_line = 0
    last_offset = 0
    for abs_tok in editor_abs_tokens:
        delta_line = abs_tok.line - last_line
        delta_offset = abs_tok.offset - last_offset if delta_line == 0 else abs_tok.offset

        rel_tok = _EditorToken(
            delta_line = delta_line,
            delta_offset = delta_offset,
            text = abs_tok.text,
            type_str = abs_tok.type_str,
            modifiers = abs_tok.modifiers,
            )
        editor_rel_tokens.append(rel_tok)

        last_line = abs_tok.line
        last_offset = abs_tok.offset

    return editor_rel_tokens

# make abs editor tokens
# make rel editor tokens
# check if identifier is recognized, or evt. just color it white and ignore recognition.
#   its recognized if its a alias in sub-query, variable/column in table, table in schema, 
#   tree, schema, routine in schema, trigger in schema, other db object



def _start_line(line_start_indices: list[int], tok_start_index: int, end_line: int) -> int:
    end_line_start_index = line_start_indices[end_line]
    if tok_start_index == end_line_start_index:
        # tok starts and ends on the same line
        return end_line - 1 # end_line = start_line
    # last_line_index = len(line_start_indices) - 1
    line = len(line_start_indices) - 0
    for line_start_index in reversed(line_start_indices):
        # line = last_line_index - i
        if line_start_index <= tok_start_index:
            # token starts at this line
            return line
        line -= 1
    raise Exception("unreachable code reached")

def _glot_tokens_including_comments(
        sapi_code: str, line_start_indices: list[int], end_of_file_index: int
        ) -> list[GlotToken]:
    for line, line_start_index in enumerate(line_start_indices):
        log(line, line_start_index)
    log("---")
    # line_by_start_index = {}
    # for line, start_indices in enumerate(line_start_indices):
    #     line_by_start_index[start_indices] = line
    

    
    glot_tokens = Settings.load_database().dialect.sqlglot_dialect().tokenize(sapi_code)
    _COMMENT = 'COMMENT' #-1
    # comment_intervals: list[tuple[int, int, int]] = []
    comments: list[GlotToken] = []
    last_end = 0
    for tok in glot_tokens:
        # evt. filter by text being whitespace. if so, then adjust the insertion code
        comment_tok = GlotToken(
            token_type = _COMMENT,
            text = None, # unused. could be set to sapi_code[last_end : tok.start]
            line = _start_line(line_start_indices, tok.start, tok.line), # line where comment ends and the next tok starts.
            col = None, # unused
            start = last_end,
            end = tok.start,
        )
        comments.append(comment_tok)
        # comment_intervals.append((last_end, tok.start, tok.line))
        last_end = tok.end
    
    
    # trailing comment
    comments.append(GlotToken(
        token_type = _COMMENT,
        text = None, # unused
        line = _start_line(tok.start, tok.line), # line where comment ends and the next tok starts.
        col = None, # unused
        start = last_end,
        end = end_of_file_index,
    ))

    last_com = None
    for com in comments:
        log(f"{com.text}: {com.token_type}, {com.line}, {com.start}, {com.end}")
        if last_com != None:
            if last_com.line > com.line:
                raise Exception("1")
            if last_com.start > com.start:
                raise Exception("2")
            if last_com.end > com.end:
                raise Exception("3")
        last_com = com


    # # insert comments
    # i = 0
    # for comment_tok in comments:
    #     glot_tokens.insert(i, comment_tok) # does this handle the trailing comment?
    #     i += 2

    log('-----')
    last_tok = None
    for tok in glot_tokens:
        log(f"{tok.text}: {tok.token_type}, {tok.line}, {tok.start}, {tok.end}")
        if last_tok != None:
            if last_tok.line > tok.line:
                raise Exception(f"11: {last_tok.line} > {tok.line}")
            if last_tok.start > tok.start:
                raise Exception(f"22: {last_tok.start} > {tok.start}")
            if last_tok.end > tok.end:
                raise Exception(f"33: {last_tok.end} > {tok.end}")
        last_tok = tok
    log('-----')

    return glot_tokens



def _editor_tokens(glot_tokens: list[GlotToken], sapi_code: str, line_start_indices: list[int]) -> list[_EditorToken]:
    # glot_tokens = Settings.load_database().dialect.sqlglot_dialect().tokenize(sapi_code)
    # glot_tokens_and_comments = _extract_comments(glot_tokens)
    editor_tokens: list[_EditorToken] = []
    last_line = 0
    last_offset = 0
    # last_delta_line = 0 # used for comments or perhaps invalid text. 
    # last_delta_offset = 0 # used for comments or perhaps invalid text. 
    # last_end = 0
    log([' '.join([f"{t.text}" for t in glot_tokens])])
    for glot_tok in glot_tokens:
        start_line = _start_line(line_start_indices, glot_tok.start, glot_tok.line) - 1
        end_line = glot_tok.line - 1
        line_start_index = line_start_indices[start_line] if start_line > 0 else 0 # error line = end_line, which need not be start_line for strings
        offset = (glot_tok.start - 0) - line_start_index
        delta_line = start_line - last_line
        delta_offset = offset - last_offset if delta_line == 0 else offset

        # editor_tok_comment = _EditorToken( # what about trailing comment?
        #     delta_line = last_delta_line, # line = end_line. comment starts on the line where last token ends
        #     delta_offset = last_delta_offset,
        #     text = sapi_code[last_end : glot_tok.start + 1], # tok.text,
        #     type_str = 'comment',
        #     modifiers = [], # no modifiers to begin with
        #     )
        # editor_tokens.append(editor_tok_comment)

        editor_tok = _EditorToken(
            delta_line = delta_line,
            delta_offset = delta_offset,
            text = sapi_code[glot_tok.start : glot_tok.end + 1], # tok.text,
            type_str = _editor_tok.get_group_names(glot_tok.token_type),
            modifiers = [], # no modifiers to begin with
            )
        editor_tokens.append(editor_tok)

        log(f"{glot_tok.text}")
        if offset < 0:
            log(f"{glot_tok.text}: {glot_tok.token_type}, {glot_tok.line}, {glot_tok.start}, {glot_tok.end}")
            log(f"{start_line}, {line_start_index}, {offset}, {delta_line}, {delta_offset}")
            raise Exception(f"offset < 0: ({glot_tok.start} - 0) - {line_start_index}")
        if delta_line < 0:
            log(f"{glot_tok.text}: {glot_tok.token_type}, {glot_tok.line}, {glot_tok.start}, {glot_tok.end}")
            log(f"{start_line}, {line_start_index}, {offset}, {delta_line}, {delta_offset}")
            raise Exception(f"delta_line < 0")
        if delta_offset < 0:
            log(f"{glot_tok.text}: {glot_tok.token_type}, {glot_tok.line}, {glot_tok.start}, {glot_tok.end}")
            log(f"{start_line}, {line_start_index}, {offset}, {delta_line}, {delta_offset}")
            raise Exception(f"delta_offset < 0")
        if last_line > start_line:
            log(f"{glot_tok.text}: {glot_tok.token_type}, {glot_tok.line}, {glot_tok.start}, {glot_tok.end}")
            log(f"{start_line}, {line_start_index}, {offset}, {delta_line}, {delta_offset}")
            raise Exception(f"{last_line} > {start_line}")# or {last_offset} > {offset}")
        last_line = start_line
        last_offset = offset
        # last_delta_line = delta_line
        # last_delta_offset = delta_offset
        # last_end = glot_tok.end
    return editor_tokens

def _semantic_tokens(editor_tokens: list[_EditorToken]) -> t.SemanticTokens:
    data = []
    for tok in editor_tokens:
        data.extend([
            tok.delta_line,
            tok.delta_offset,
            len(tok.text),
            _editor_tok.token_type_names().index(tok.type_str), # returns index into token_type_names
            reduce(operator.or_, tok.modifiers, 0), # returns bitmap into modifier_names
        ])
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

# ----------- ChatGPT suggests ----------- 
"""
Bad Token:        #FF0000 (bright red) 
Braces:           #A9B7C6 (light gray-blue) 
Brackets:         #A9B7C6 (light gray-blue) 
Column:           #9876AA (light purple)
Comma:            #A9B7C6 (light gray-blue) 
Comment:          #808080 or #629755 (grayish-green)
Database Object:  #CC7832 (orange)
Dot:              #A9B7C6 (light gray-blue) 
External Command: #9876AA (light purple) 
Keyword:          #CC7832 (orange)
Label:            #E8BF6A (light yellow)
Number Token:     #6897BB (light blue) 
Outer Query Col:  #9876AA (light purple)
Parameter:        #9876AA (light purple)
Parenthesis:      #A9B7C6 (light gray-blue) 
Routine:          #FFC66D (light orange)
Schema:           #9876AA (light purple)
Semicolon:        #A9B7C6 (light gray-blue) 
String Token:     #6A8759 (green)
Synthetic Entity: #A9B7C6 (light gray-blue)
Table:            #FFC66D (light orange)
Alias:            #9876AA (light 
Type:             #CC7832 (orange) 
Variable:         #9876AA (light purple)

"""



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
    #             tok_type = _keyword_str if tok.token_type in tokenizer._keywords else tok.text,
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
        #     tok_type = _keyword_str if tok.token_type in _keywords else tok.text,
        #     tok_modifiers = [], # no modifiers to begin with
        # ) for tok in tok_tree.tokens])
    # __slots__ = ("token_type", "text", "line", "col", "start", "end", "comments")

        # log(token)
        # Token(line=12, offset=228, text='col0_1', tok_type='VAR', tok_modifiers=[])
        # Token(line=<Token token_type: TokenType.VAR, text: col0_1, line: 12, col: 36, start: 228, end: None, comments: []>, 
        # offset=238, text='JOIN', tok_type='JOIN', tok_modifiers=[])
        # bullshit! thats not a line number.
        
        # _keyword_str if tok.token_type in _keywords else tok.text
                        # Token(
                        #     line=current_line - prev_line,
                        #     offset=current_offset - prev_offset,
                        #     text=match.group(0),
                        #     tok_
                                # if tok_.tok_type_str  == _keyword_str:
        #     a = (
        #         tok_.delta_line,
        #         tok_.delta_offset,
        #         len(tok_.text),
        #         token_type_names.index(tok_.tok_type_str), # returns index into token_type_names
        #         reduce(operator.or_, tok_.tok_modifiers, 0), # returns bitmap into modifier_names)}, {tok.line}, {tok.start}")
        #     )
        #     log(f"{tok_.tok_type_str}: {tok_.text}, {a}")
        # # log(f"{tok_.tok_type}: {tok_.tok_type in token_type_names} "
        # #     f"{tok_.tok_type.lower() in token_type_names} {tok_.tok_type.upper() in token_type_names}")
