import re
from typing import Any
from pygls.server import LanguageServer
from tools import embedding

class SapiLanguageServer(LanguageServer):
   
    def send_output(self, data: Any):
        self.send_notification('output', str(data))

    def file_types(_): return [".sapi", ".sapir", ".py"]

    def sapi_lines(_, uri: str) -> list[str]:
        all_lines = _.workspace.get_text_document(uri).lines
        return all_lines if uri.endswith(".sapi") else embedding.sapi_lines(all_lines)




server = SapiLanguageServer("sapi-server", "v1")
serverType = SapiLanguageServer


