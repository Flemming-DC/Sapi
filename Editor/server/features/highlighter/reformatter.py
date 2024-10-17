import operator
from functools import reduce
from dataclasses import dataclass
from lsprotocol import types as t
from sapi._editor import editor_tok
from .tokenizer import EditorAbsToken, TokenModifier

@dataclass
class _EditorRelToken:
    delta_line: int
    delta_offset: int
    text: str
    type_str: str
    modifiers: list[TokenModifier]




def abs_to_semantic_tokens(editor_abs_tokens: list[EditorAbsToken]) -> t.SemanticTokens:
    editor_rel_tokens = _abs_to_rel_tokens(editor_abs_tokens)
    return _rel_to_semantic_tokens(editor_rel_tokens)


def _abs_to_rel_tokens(editor_abs_tokens: list[EditorAbsToken]) -> list[_EditorRelToken]:
    editor_rel_tokens: list[_EditorRelToken] = []
    last_line = 0
    last_offset = 0
    for abs_tok in editor_abs_tokens:
        delta_line = abs_tok.line - last_line
        delta_offset = abs_tok.offset - last_offset if delta_line == 0 else abs_tok.offset
        type_str = editor_tok.get_group_name(abs_tok.type if abs_tok.type else editor_tok.fake_glot_type_comment())

        rel_tok = _EditorRelToken(
            delta_line = delta_line,
            delta_offset = delta_offset,
            text = abs_tok.text,
            type_str = type_str,
            modifiers = abs_tok.modifiers,
            )
        editor_rel_tokens.append(rel_tok)

        last_line = abs_tok.line
        last_offset = abs_tok.offset

    return editor_rel_tokens


def _rel_to_semantic_tokens(editor_tokens: list[_EditorRelToken]) -> t.SemanticTokens:
    data = []
    for tok in editor_tokens:
        data.extend([
            tok.delta_line,
            tok.delta_offset,
            len(tok.text),
            editor_tok.token_type_names().index(tok.type_str), # returns index into token_type_names
            reduce(operator.or_, tok.modifiers, 0), # returns bitmap into modifier_names
        ])
    return t.SemanticTokens(data=data)


