from engine.tokenizer import flat_tokenize
from engine.token_tree import Token

def has_passed(tokens: list[Token], i: int, code_snippet: str) -> bool:
    prior_tokens_str = ' '.join([t.text for t in tokens[:i]])
    tokens_snippet_str = ' '.join([t.text for t in flat_tokenize(code_snippet)])
    return tokens_snippet_str in prior_tokens_str

