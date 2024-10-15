from typing import Any
from pygls.server import LanguageServer

class SapiLanguageServer(LanguageServer):
   
    def send_output(self, data: Any):
        self.send_notification('output', str(data))



server = SapiLanguageServer("sapi-server", "v1")
serverType = SapiLanguageServer


