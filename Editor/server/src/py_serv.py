import logging
import re
from lsprotocol import types
from pygls.server import LanguageServer
import greet
import os
import pathlib
import sapi_demo

COLOR = re.compile(r"""\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})(?!\w)""")
server = LanguageServer("color-server", "v1")


@server.feature(types.TEXT_DOCUMENT_DOCUMENT_COLOR)
def document_color(params: types.CodeActionParams):
    """Return a list of colors declared in the document."""
    
    # document = server.workspace.get_text_document(params.text_document.uri)
    # current_line = document.lines[params.position.line].strip()
    # server.send_notification("hi. server is here")
    # server.show_message(f"""
    #     server.workspace.root_path, os.getcwd(), '.'
    #     {server.workspace.root_path}
    #     {os.getcwd()}
    #     {str(pathlib.Path('.').resolve())}
    #     """)
    server.show_message(sapi_demo.get_sql())
    if not server.workspace.root_path:
        raise Exception("failed to find root directory")
    # greet.greet(server.workspace.root_path, 'rp')
    # greet.greet(os.getcwd(), 'cwd')
    # greet.greet('.', '.')
    # greet.greet(str(pathlib.Path('.').resolve()), 'p.')
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    for linum, line in enumerate(document.lines):
        for match in COLOR.finditer(line.strip()):
            start_char, end_char = match.span()

            # Is this a short form color?
            if (end_char - start_char) == 4:
                color = "".join(c * 2 for c in match.group(1))
                value = int(color, 16)
            else:
                value = int(match.group(1), 16)

            # Split the single color value into a value for each color channel.
            blue = (value & 0xFF) / 0xFF
            green = (value & (0xFF << 8)) / (0xFF << 8)
            red = (value & (0xFF << 16)) / (0xFF << 16)

            items.append(
                types.ColorInformation(
                    color=types.Color(red=red, green=green, blue=blue, alpha=1.0),
                    range=types.Range(
                        start=types.Position(line=linum, character=start_char),
                        end=types.Position(line=linum, character=end_char),
                    ),
                )
            )

    return items


@server.feature(types.TEXT_DOCUMENT_COLOR_PRESENTATION)
def color_presentation(params: types.ColorPresentationParams):
    """Given a color, instruct the client how to insert the representation of that
    color into the document"""
    color = params.color

    b = int(color.blue * 255)
    g = int(color.green * 255)
    r = int(color.red * 255)

    # Combine each color channel into a single value
    value = (r << 16) | (g << 8) | b
    return [types.ColorPresentation(label=f"#{value:0{6}x}")]


ADDITION = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=(?=\s*$)")

@server.feature(
    types.TEXT_DOCUMENT_CODE_ACTION,
    types.CodeActionOptions(code_action_kinds=[types.CodeActionKind.QuickFix]))
def code_actions(params: types.CodeActionParams):
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line

    lines = document.lines[start_line : end_line + 1]
    for idx, line in enumerate(lines):
        match = ADDITION.match(line)
        if match is not None:
            range_ = types.Range(
                start=types.Position(line=start_line + idx, character=0),
                end=types.Position(line=start_line + idx, character=len(line) - 1),
            )

            left = int(match.group(1))
            right = int(match.group(2))
            answer = left + right

            text_edit = types.TextEdit(
                range=range_, new_text=f"{line.strip()} {answer}!"
            )

            action = types.CodeAction(
                title=f"Evaluate '{match.group(0)}'",
                kind=types.CodeActionKind.QuickFix,
                edit=types.WorkspaceEdit(changes={document_uri: [text_edit]}),
            )
            items.append(action)

    return items

@server.command('hi')
def foo(a):
    return a


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    server.start_io()
