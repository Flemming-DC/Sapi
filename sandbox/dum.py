from dataclasses import dataclass, field


@dataclass
class TokenTree:
    tokens: list[int]
    _sapi_str: str # const (evt. only store at the root tree)
    _previous_token: int|None
    _next_token: int|None
    _str_replacements: list[int] = field(default_factory=list)

tt = TokenTree(
    tokens = [],
    _sapi_str = "s",
    _previous_token = 1,
    _next_token = 1,
    _str_replacements = [],
    )

print(tt)




