from typing import Any
from pygls.server import LanguageServer

# F = TypeVar("F", bound=Callable)
class SapiLanguageServer(LanguageServer):
    
    def send_output(self, data: Any):
        self.send_notification('output', str(data))

    
#     def feature(self, feature_name: str, options: Any = None) -> Callable[[F], F]:
#         return super().feature(feature_name, options)

#     def _filter_file_type(self, func):
#         ...


# starts reacting when start io is called
server = SapiLanguageServer("sapi-server", "v1")
serverType = SapiLanguageServer

# def _lazy_init():
#     global _server
#     if _server is None:
#         _server = LanguageServer("color-server", "v1")
#         _server.start_io()

# F = TypeVar("F", bound=Callable)
# def feature(feature_name: str, options: Any = None) -> Callable[[F], F]:
#     # _lazy_init()
#     _server.feature(feature_name, options)

# def command(command_name: str) -> Callable[[F], F]:
#     # _lazy_init()
#     _server.command(command_name)


