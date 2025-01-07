use crate::internals::token_tree::TokenTree; // , Token, TokenType

pub struct AnalyzerLoop<'a> {
    token_tree: &'a TokenTree<'a>,
    // tokens, // could be eliminated in favor of _._token_tree.tokens
    i: i32, // index = token_index, not sapi_str index
    count: usize,
    breakpoint_index: Option<usize>,
}

impl<'a> AnalyzerLoop<'a> {
    pub fn new(token_tree: &'a TokenTree<'a>) -> Self {
        AnalyzerLoop {
            token_tree: token_tree,
            // tokens: token_tree.tokens // could be eliminated in favor of _._token_tree.tokens
            i: 0 - 1, // index = token_index, not sapi_str index (it starts with one less than the value at the first step)
            count: token_tree.tokens.len(),
            breakpoint_index: None,
        }
    }
}
//     pub fn tok(_): 
//         return _._tokens[_._i]


    
//     pub fn peek(_, distance: int = 1) -> Token|None: 
//         index = _._i + distance
//         if index < 0 or index >= _._count:
//             return None
//         return _._tokens[index]

    
//     pub fn next(_) -> bool:
//         "Step to next element and return True, if a next element was found"
//         _._i += 1
//         if _._i >= _._count:
//             return False
//         if _._breakpoint_index is not None and _._i >= _._breakpoint_index:
//             breakpoint()
//             _._breakpoint_index = None
//         return True
    
    
//     pub fn found(_, tokenType: TokenType|list[TokenType], after_steps: int) -> bool:
//         "Checks for tokenType after presicely the specified number of steps."
//         index = _._i + after_steps
//         if index < 0 or index >= _._count:
//             return False
//         tokenTypes = tokenType if isinstance(tokenType, list) else [tokenType]
//         return _._tokens[index].type in tokenTypes
    
    
//     pub fn index(_): return _._i 
    
    
//     pub fn has_passed(_, stopping_obj: str) -> bool:
//         return _.at_end() or stopping_obj in _.view() #_._token_tree.has_passed(stopping_obj, _.tok().start)
    
//     pub fn at_end(_, distance: int = 0): return _._i + distance >= _._count

//     pub fn view(_, from_: int|None = None, to: int = 0):
//         "Meant for debugging"
//         from_ = from_ + _._i if from_ is not None else 0
//         to = to + _._i if to is not None else -1
//         return ' '.join(t.text for t in _._tokens[from_:to])





