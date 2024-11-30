from . import insert_generator
from sapi._internals.token_tree import TokenTree


def parse_insert(token_tree: TokenTree) -> TokenTree:
    info = analyze_insert(token_tree)
    token_tree = insert_generator.generate_insert(info)
    return token_tree



def analyze_insert(token_tree: TokenTree):
    ...

