from typing import Callable, Any, TypeVar
from pygls.server import LanguageServer

# starts reacting when start io is called
server: LanguageServer = LanguageServer("color-server", "v1")

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


