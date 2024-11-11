import os
from lsprotocol import types as t
from typing import Sequence
import sapi
from tools.server import server
from tools.command import command
from tools import error, settings
from tools.log import log
from tools.embedding import Section

# register code action ideally by ctrl-enter-enter. 
# first connect, then execute or parse (you choose)
# if connect: how to get connection?
# store connection info in sapi_settings.json in .vscode (evt. use some builtin lsp settings feature)
# store dialect (by name) in sapi_settings.
# rely on the builtin dialect class to provide the dialect instance given the name. 
#   The issue of whether and how to expose the dialect class is saved for later

@server.feature(
    t.TEXT_DOCUMENT_CODE_ACTION,
    t.CodeActionOptions(code_action_kinds=[t.CodeActionKind.QuickFix]))
@error.as_log_and_popup
def code_actions(params: t.CodeActionParams) -> list[t.CodeAction]:
    uri = params.text_document.uri
    if not any(uri.endswith(file_type) for file_type in server.file_types()):
        return []
    # r = params.range # range is the selected range.
    # log("r:", r.start.line, r.end.line)
    # evt use [r.start.line : r.end.line + 1]
    sections = server.sapi_sections(uri, False)
    _check_sections(sections, [line.rstrip(os.linesep) for line in server.workspace.get_text_document(uri).lines] )
    return code_actions_work(sections, uri, params.range)


    
def code_actions_work(sections: list[Section], uri: str, range: t.Range) -> list[t.CodeAction]:
    sections = _selected_sections(sections, range)
    if sections == []: return []
    if len(sections) != 1: return [] # this only allows handling queries one at a time.
    # sapi_code = '\n'.join([line.strip('\n\r') for line in lines]) # FAILS FOR EMBEDDED CODE
    # sapi_code = sections[0].leading_whitespace + sections[0].query # temp
    section = sections[0]
    sapi_code = section.query
    # line_len = len(sapi_code.split('\n'))

    dataModel = settings.load_datamodel()
# def _vrewv(section: Section, dataModel: sapi.DataModel):
    try:
        sql_query = sapi.parse(sapi_code, dataModel, str) # try-parse
    except Exception as e: # create a user error class for the parser and filter by it
        code_start = sapi_code if len(sapi_code) < 10 else sapi_code[:10] + '...'
        log(f"Failed to parse ['''{code_start}''']:\nError: {e}")
        return [] # produce error message in output rather than removing code actions
    log('---')
    log(sapi_code)
    log('--')
    log(sql_query)
    if not sql_query.rstrip().endswith(';'):
        if not sql_query.rstrip(' ').endswith('\n'):
            sql_query += '\n;'
        else:
            sql_query += ';'
    log('--')
    log(sql_query)
    log('--')
    range_ = t.Range(
        start=t.Position(line=section.line_nr_start, character=section.char_start + 0),
        end=t.Position(line=section.line_nr_end - 0, character=section.char_end))
    text_edit = t.TextEdit(range=range_, new_text=sql_query)
    cast_to_sql = t.CodeAction(
        title=f"to SQL",
        kind=t.CodeActionKind.Empty,
        edit=t.WorkspaceEdit(changes={uri: [text_edit]}))

    execute = t.CodeAction(
        title=f"Execute",
        kind=t.CodeActionKind.Empty,
        command=t.Command(title=_execute.__name__, command=_execute.__name__, arguments=[sql_query]))
    
    return [execute, cast_to_sql]


def _selected_sections(sections: list[Section], range: t.Range) -> list[Section]:
    "Includes partially selected sections and section at current mouse position."
    out = []
    for section in sections:
        log(section)
        # skip sections before range
        if section.line_nr_end < range.start.line:
            continue
        log(1)
        if section.line_nr_end == range.start.line and section.char_end < range.start.character:
            continue
        log(2)
        # skip sections after range
        if section.line_nr_start > range.end.line:
            continue
        log(3)
        if section.line_nr_start == range.end.line and section.char_start > range.end.character:
            continue
        log(4)
        out.append(section)
    return out

# @command
# @error.as_log_and_popup
# def _print_sapi(msg: str) -> str:
#     return msg

@command
@error.as_log_and_popup
def _execute(sql_query: str) -> Sequence[Sequence]:
    database = settings.load_database()
    # error: multiple _execute calls can fit into the same transaction (unless you autocommit).
    # you need to keep a connection alive between transactions.
    with sapi.Transaction(database) as tr:
        return tr.execute_plain_sql(sql_query).rows()

    # con = database.dialect.connect(**database.connect_kwargs)
    # cur = con.cursor()
    # cur.execute("set search_path to sapi_demo") # temp
    # cur.execute(sql_query)
    # data = cur.fetchall()
    # con.commit()
    # con.close()
    # return data


def _check_sections(sections: list[Section], lines: list[str]):
    for section in sections:
        before_start = lines[section.line_nr_start][section.char_start - 3 : section.char_start]
        assert '"' in before_start or "'''" in before_start, (
            f"Expected \", \"\"\" or ''' before section. \nline: {lines[section.line_nr_start]}\nbefore_start: {before_start}"
            f"\n{section.line_nr_start}, {section.char_start}")
        after_end = lines[section.line_nr_end][section.char_end : section.char_end + 3]
        assert '"' in after_end or "'''" in after_end, (
            f"Expected \", \"\"\" or ''' after section. \nline: {lines[section.line_nr_end]}\nafter_end: {after_end}"
            f"\n{section.line_nr_end}, {section.char_end}")
    


"""

cast to sql removes the trailing semicolon
-------
cast to sql whipes out all the python code

"""

