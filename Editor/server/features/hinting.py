from lsprotocol import types as t
from tools.server import server
from tools.log import log
from sapi._editor import TokenTree, common_select_clauses
from tools import data_model
from tools import error
import sapi


@server.feature(t.TEXT_DOCUMENT_INLAY_HINT)
@error.as_log_and_popup
def inlay_hints(params: t.InlayHintParams) -> list[t.InlayHint]:
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(uri)
    r = params.range
    lines = document.lines[r.start.line : r.end.line + 1]
    return _inlay_hints_work(lines)


def _inlay_hints_work(lines: list[str]) -> list[t.InlayHint]:
    sapi_code = '\r\n'.join([line.strip('\n\r') for line in lines]) # does this work for multiple queries?
    dataModel = data_model.make_datamodel()
    sql_token_trees = sapi.parse(sapi_code, dataModel, list[TokenTree])
    line_start_indices = _line_start_indices(lines)
    hints = []
    for tok_tree in sql_token_trees:
        hints.extend(_get_hints(tok_tree, line_start_indices))
    return hints


def _get_hints(tok_tree: TokenTree, line_start_indices: list[int]) -> list[t.InlayHint]:
    str_replacements = tok_tree.recursive_str_replacements() # collect replacements in subtrees
    if not str_replacements:
        return [] # handle the None case
    
    hints = []
    put_on_new_line_sequence_len = 0 # used to put join_clauses on seperate lines.
    str_replacements.sort(key = lambda r: r.str_from_)
    for rep in str_replacements:
        if not rep.new_tokens:
            continue
        put_on_new_line = rep.new_tokens[0].type in common_select_clauses()
        prefix = '' if put_on_new_line else ' '
        hint_text = prefix + ' '.join([t.text for t in rep.new_tokens])

        index = rep.str_to # hints goes after replaced code. This is relevant for "join tree on ..." followed by hint.
        line_nr, line_start_index = _round_down_to_nearest_element(index, line_start_indices)
        char = index - line_start_index
        error.dev_assert(char >= 0, f"char = {char} = {index} - {line_start_index}")
        line_nr += put_on_new_line_sequence_len

        hint = t.InlayHint(
            label=hint_text,
            kind=t.InlayHintKind.Type,
            padding_left=True,
            padding_right=True,
            position=t.Position(line=line_nr, character=char),
            )
        hints.append(hint)

        put_on_new_line_sequence_len = put_on_new_line_sequence_len + 1 if put_on_new_line else 0

    return hints



def _line_start_indices(lines: list[str]) -> list[int]:
    line_start_indices = []
    last_line_length = 0
    current_line_start_index = 0
    for line in lines:
        current_line_start_index += last_line_length
        line_start_indices.append(current_line_start_index)
        last_line_length = len(line)
    return line_start_indices



def _round_down_to_nearest_element(number: int, sorted_list: list[int]) -> tuple[int, int] | tuple[None, None]:
    """
    Found target down to the nearest element in the list in log time.
    Returns None if target < sorted_list[0]
    Returns the index and value of the rounded down.
    """
    left = 0 
    right = len(sorted_list) - 1
    nearest_lower_value = None
    idx = None
    mid = None # resulting index
    while left <= right:
        mid = left + (right - left) // 2
        if sorted_list[mid] <= number:
            nearest_lower_value = sorted_list[mid] # update the result
            idx = mid
            left = mid + 1  # search in the right half
        else:
            right = mid - 1  # search in the left half
    
    return idx, nearest_lower_value





