from enum import Enum, auto
from sapi._editor import editor_tok
from .tokenizer import EditorAbsToken
from tools import data_model
from sapi import DataModel


class _ColorType(Enum): # evt. replace auto with color literal
    LanguageBoundary = auto()
    Number = auto()
    String = auto()
    Comment = auto()
    Keyword = auto() # Keyword or SemiColon
    # evt. SecondaryKeyword
    Type = auto() # DataType
    Other = auto()
    # sql-specific
    Routine = auto()
    Trigger = auto()
    Schema = auto()
    Tree = auto()
    View = auto()
    Table = auto()
    Column = auto()
    # evt Alias = auto()
    # evt. UnrecognizedIdentifier = auto()


# violating interface with editor_tok. Find out what to do with it later.
def _verv(abs_tok: EditorAbsToken) -> _ColorType:
    glot_type_group = editor_tok._group_type_by_glot_type[abs_tok.type]
    dataModel = data_model.make_datamodel()

    # Routine, Trigger, Schema, View
    # Tree, Table, Column

    is_col = _is_var(dataModel, abs_tok.text)
    is_tree = _is_tree(dataModel, abs_tok.text)
    is_table = _is_table(dataModel, abs_tok.text)
    


# temporary code
def _is_var(dataModel: DataModel, tok_text: str):           return tok_text in dataModel._tables_by_var.keys()
def _is_tree(dataModel: DataModel, tok_text: str):          return tok_text in dataModel._table_tree_names
def _is_table(dataModel: DataModel, tok_text: str):         return tok_text in dataModel._all_tables








