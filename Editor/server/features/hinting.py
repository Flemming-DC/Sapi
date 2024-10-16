from lsprotocol import types as t
from tools.server import server
from tools.log import log
from tools import error
from lsprotocol import types as t
import sapi
from sapi._editor import TokenTree
from tools.server import server
from tools import data_model
from tools import error
from dataclasses import dataclass


@server.feature(t.TEXT_DOCUMENT_INLAY_HINT)
@error.as_log_and_popup
def inlay_hints(params: t.InlayHintParams) -> list[t.InlayHint]:
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(uri)
    r = params.range
    lines = document.lines[r.start.line : r.end.line + 1]
    return inlay_hints_work(lines)


def inlay_hints_work(lines: list[str]) -> list[t.InlayHint]:
    
    sapi_code = '\r\n'.join([line.strip('\n\r') for line in lines]) # does this work for multiple queries?
    dataModel = data_model.make_datamodel()
    sql_token_trees = sapi.parse(sapi_code, dataModel, list[TokenTree])
    # sql_query = '\n;\n'.join(str(t) for t in sql_token_trees)
    # sql_lines = sql_query.split('\n')
    # hints = []
    # for i, line in enumerate(sql_lines):
    #     hint = t.InlayHint(
    #         label=line.strip(),
    #         kind=t.InlayHintKind.Type,
    #         padding_left=False,
    #         padding_right=True,
    #         position=t.Position(line=i, character=0),
    #     )
    #     hints.append(hint)
    line_start_indices = _line_start_indices(lines)
    hints = []
    for tok_tree in sql_token_trees:
        hints.extend(get_hints(tok_tree, line_start_indices))
    return hints



def get_hints(tok_tree: TokenTree, line_start_indices: list[int]) -> list[t.InlayHint]:
    # collect replacements in subtrees
    str_replacements = tok_tree._str_replacements
    for tok in tok_tree.tokens:
        if isinstance(tok, TokenTree):
            str_replacements += tok._str_replacements
    # handle the None case
    if not str_replacements:
        return tok_tree._sapi_str

    
    hints = []
    str_replacements.sort(key = lambda r: r.str_from_) # is this used ??
    for rep in str_replacements:
        # last_rep_to = str_replacements[i - 1].str_to if i > 0 else 0 # helper-data
        # sql_str += tok_tree._sapi_str[last_rep_to:rep.str_from_]            # appending a sapi-segment
        hint_text = ' '.join([t.text for t in rep.new_tokens]) # probably too simplified. you need something like _add_token_str2
        # for tok in rep.new_tokens:
            # sql_str = TokenTree._add_token_str2(sql_str, tok)        # appending a token of replacement
        # if tok_tree._if_new_clause_add_newline(sql_str, rep.str_from_):
        #     ... # hints can't be multipline. So perhaps you need to handle each line seperately
        
        index = rep.str_to # hints goes after replaced code. This is relevant for "join tree on ..." followed by hint.
        line_nr, line_start_index = _round_down(line_start_indices, index)
        offset = index - line_start_index
        error.dev_assert(offset >= 0, f"offset = {offset} = {index} - {line_start_index}")
        char = offset

        hint = t.InlayHint(
            label=hint_text,
            kind=t.InlayHintKind.Type,
            padding_left=False,
            padding_right=True,
            position=t.Position(line=line_nr, character=char),
            )
        hints.append(hint)

    # last_rep_to = str_replacements[-1].str_to
    # sql_str += tok_tree._sapi_str[last_rep_to:]
    return hints



def _line_start_indices(lines: list[str]) -> list[int]:
    line_start_indices = []
    last_line_length = 0
    current_line_start_index = 0
    for line in lines:
        current_line_start_index += last_line_length
        line_start_indices.append(current_line_start_index)
        last_line_length = len(line)#.strip('\n\r'))# + 1
    return line_start_indices



def _round_down(sorted_list: list[int], target: int) -> tuple[int, int] | tuple[None, None]:
    """
    Found target down to the nearest element in the list in log time.
    Returns None if target < sorted_list[0]
    Returns the index and value of the rounded down.
    """
    left = 0 
    right = len(sorted_list) - 1
    result = None  # This will hold the nearest lower value
    mid = None # resulting index
    while left <= right:
        mid = left + (right - left) // 2
        if sorted_list[mid] <= target:
            result = sorted_list[mid]  # Update the result
            left = mid + 1  # Search in the right half
        else:
            right = mid - 1  # Search in the left half
    return mid, result

# def token_str(so_far: str, tok: Token) -> str:
#     no_space_prefix = [')', ']', '}', '.', ',']
#     no_space_suffix = ['(', '[', '{', '.'     ]

#     if tok.type in _common_select_clauses:
#         so_far = so_far.rstrip(' \n') # remove uncontrolled whitespace and newline
#         so_far += '\n' + TokenTree._last_indention(so_far) # add newline and preserve indention
#         return so_far + tok.text
    
#     elif so_far != "" and so_far[-1] in no_space_suffix: # previous has have no space suffix
#         return so_far.rstrip(' ') + tok.text
#     elif tok.text in no_space_prefix:
#         return so_far.rstrip(' ') + tok.text
#     else:
#         return (so_far if so_far.endswith(' ') else so_far + ' ') + tok.text


