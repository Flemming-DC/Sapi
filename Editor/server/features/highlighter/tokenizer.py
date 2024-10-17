from copy import copy
from dataclasses import dataclass
from enum import IntFlag, auto
from sqlglot.tokens import Token as GlotToken, TokenType as GlotType
from tools.settings import Settings
from tools import error

class TokenModifier(IntFlag):
    definition = auto()

@dataclass
class EditorAbsToken:
    "Output of tokenizer. Must be converted to _EditorRelToken."
    line: int
    offset: int
    text: str
    type: GlotType | None
    modifiers: list[TokenModifier]


@dataclass
class _Location:
    "Used in tokenizer and its helper function"
    line_nr: int = 0
    line_start_index: int = 0
    i: int = 0
    def new_line(_): 
        _.line_nr += 1
        _.line_start_index = _.i + 1
        _.i += 1



def tokenize(sapi_code: str) -> list[EditorAbsToken]:
    """
    match next_tok start_index: eat to end_index and collect glot_token, seperately for each line
    match single_line_comment_markers: eat to end of line and collect comment_token
    match multi_line_comment_start_markers: eat to end marker and collect comment_token, seperately for each line
    match \n: eat \n and update line_nr, line_start_index
    """
    glot_dialect = Settings.load_database().dialect.sqlglot_dialect()
    glot_tokens = glot_dialect.tokenize(sapi_code)
    comment_markers: list[str | tuple[str, str]] = glot_dialect.tokenizer.COMMENTS
    if len(glot_tokens) == 0: 
        return
    next_glot_tok_idx: int = 0
      
    single_line_1_char_comment_markers = [m for m in comment_markers if isinstance(m, str) and len(m) == 1] # subset of ['--']
    single_line_2_char_comment_markers = [m for m in comment_markers if isinstance(m, str) and len(m) == 2] # subset of ['--', '#!', '//']
    multi_line_comment_end_by_start_markers = {mp[0]: mp[1] for mp in comment_markers if isinstance(mp, tuple)} # = {'/*': '*/'}
    

    loc = _Location(0, 0, 0)
    editor_tokens: list[EditorAbsToken] = []
    count = len(sapi_code)
    def char(i: int): return sapi_code[i]
    def two_char(i: int): return sapi_code[i] + (sapi_code[i + 1] if i + 1 < count else '')
    
    while loc.i < count:
        next_glot_tok: GlotToken = glot_tokens[next_glot_tok_idx] if next_glot_tok_idx < len(glot_tokens) else None

        if next_glot_tok and loc.i == next_glot_tok.start:
            # eat to end_index and collect glot_token, seperately for each line
            next_glot_tok_idx += 1
            loc_start = copy(loc)
            while loc.i < next_glot_tok.end and loc.i < count: 
                loc.i += 1
                if char(loc.i) == '\n':
                    editor_tokens.append(_make_editor_token(sapi_code, next_glot_tok.token_type, loc_start, loc.i))
                    loc.new_line()
                    loc_start = copy(loc)
            editor_tokens.append(_make_editor_token(sapi_code, next_glot_tok.token_type, loc_start, loc.i))
            loc.i += 1
        elif char(loc.i) in single_line_1_char_comment_markers or two_char(loc.i) in single_line_2_char_comment_markers:
            # eat to end of line and collect comment_token
            loc_start = copy(loc)
            while char(loc.i) != '\n' and loc.i < count: 
                loc.i += 1
            editor_tokens.append(_make_editor_token(sapi_code, None, loc_start, loc.i))
        elif two_char(loc.i) in multi_line_comment_end_by_start_markers.keys():
            # eat to end marker and collect comment_token, seperately for each line
            end_marker = multi_line_comment_end_by_start_markers[two_char(loc.i)]
            loc_start = copy(loc)
            while two_char(loc.i) != end_marker and loc.i < count: 
                loc.i += 1
                if char(loc.i) == '\n':
                    editor_tokens.append(_make_editor_token(sapi_code, None, loc_start, loc.i))
                    loc.new_line()
                    loc_start = copy(loc)
            loc.i += 2 # end_marker is two characters long, so we make a double step
            editor_tokens.append(_make_editor_token(sapi_code, None, loc_start, loc.i))
        elif char(loc.i) == '\n':
            loc.new_line()
        else:
            loc.i += 1
        
    return editor_tokens


def _make_editor_token(sapi_code: str, glot_type: GlotType|None, loc_start: _Location, index_end: int) -> EditorAbsToken:

    line_start_index = loc_start.line_start_index
    offset = loc_start.i - line_start_index
    error.dev_assert(offset >= 0, f"offset = {offset} = {loc_start.i} - {line_start_index}")

    tok = EditorAbsToken(
        line = loc_start.line_nr,
        offset = offset,
        text = sapi_code[loc_start.i : index_end + 1].strip('\r\n'), 
        type = glot_type, # editor_tok.get_group_names(glot_type if glot_type else editor_tok.fake_glot_type_comment()),
        modifiers = [], # no modifiers to begin with
        )
    return tok


