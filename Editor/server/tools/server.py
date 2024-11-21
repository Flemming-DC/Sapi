from typing import Any
from lsprotocol import types as t
from pygls.server import LanguageServer
from tools import embedding

class SapiLanguageServer(LanguageServer):
   
    def send_output(self, data: Any):
        self.send_notification('output', str(data))

    def file_types(_): return [".sapi", ".sapir", ".py"]

    # def sapi_lines(_, uri: str, use_os_line_ending: bool) -> list[str]:
    #     all_lines = [line.rstrip('\r\n') for line in _.workspace.get_text_document(uri).lines] 
    #     return all_lines if uri.endswith(".sapi") else embedding.sapi_lines(all_lines, use_os_line_ending)

    def sapi_sections(_, uri: str, use_os_line_ending: bool, range: t.Range = None) -> list[embedding.Section]:
        lines = [line.rstrip('\r\n') for line in _.workspace.get_text_document(uri).lines] 
        if uri.endswith(".sapi"):
            return embedding.freeform_single_section(lines, use_os_line_ending)
        else:
            return embedding.sapi_sections(lines, use_os_line_ending, range)



server = SapiLanguageServer("sapi-server", "v1")
serverType = SapiLanguageServer


