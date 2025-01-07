
use bumpalo::Bump;
use sqlparser::tokenizer::{Token, TokenWithSpan}; // sqlglot.tokens import TokenType
use bumpalo::collections::Vec as bVec;
// use error::CompilerError;

// #[derive(Debug)]
// pub enum TokenType {} // temp

// #[derive(Debug)]
// #[derive(Debug, Clone, PartialEq, PartialOrd, Eq, Ord, Hash)]
// pub struct Token<'a> { // use SqlToken ??
//     pub type_: TokenType, // evt. type: TokType
//     pub text: &'a str,
//     pub line: u32, // The line that the token ends on. (maybe usable by editor, but not by parser. could in principle be recalculated)
//     pub start: u32, // start index (used in parser and maybe editor)
//     // end: u32 = None // start + len(text) - 1, // (possibly up to an offset that depends on the string boundary width) 

//     // fn __str__(_): return f"{_.type.name}: {_.text}" // at {_.start} on {_.line}
    
//     // fn __post_init__(_):
//     //    if _.end is None: 
//     //        _.end = _.start + len(_.text) - 1
// }


#[derive(Debug, Clone)]
pub struct StrReplacement<'a> {
    pub str_from: usize,
    pub str_to: usize,
    pub text: &'a str,
    pub is_new_clause: bool,
}

#[derive(Debug, Clone)]
pub enum TokNode<'a> { Leaf(Token), Tree(&'a TokenTree<'a>) } // size_of Token and TokenWithSpan are 56, 88 Bytes. Unnecesarily large.

#[derive(Debug)]
pub struct TokenTree<'a> {
    pub tokens: bVec<'a, TokNode<'a>>,
    len_sapi_str: usize, // (evt. only store at the root tree) // contains sapi code for one statement
    next_token: Option<Token>, // Token or TokNode ?
    str_replacements: Vec<StrReplacement<'a>>, 
}

pub fn tok_text(tok: &Token) -> &'static str { "" } // where to put this?

impl<'a> TokenTree<'a> {
    pub fn new(tokens: bVec<'a, TokNode<'a>>, len_sapi_str: usize, next_token: Option<Token>) -> Self {
        TokenTree { tokens, len_sapi_str, next_token, str_replacements: [].into() }
    }


    // ---------- Immitate Token ---------- //
    // TokenType.TOKEN_TREE = namedtuple('fake_enum_variant', ['name', 'value'])(name='TOKEN_TREE', value='TOKEN_TREE')
    // type: TokenType = TokenType.TOKEN_TREE
    // pub fn text(_): return "[TokenTree]"
    // pub fn line(_): return _.tokens[0].line if _.tokens else None
    // pub fn start(_): return _.tokens[0].start if _.tokens else None
    // pub fn end(_): raise CompilerError("Don't call end() on TokenTree.") // dont use this
    // -------------------------------------- // 

    // pub fn has_passed(_, stopping_obj: str, str_index: int) -> bool:
    //     location = _._sapi_str.find(stopping_obj)
    //     return str_index >= location and location != -1
        

//     pub fn make_replacement(_, from_: int, to: int, new_text: str, is_new_clause: bool):
//         count = len(_.tokens)
//         if from_ < 0 or to > count:
//             raise CompilerError("index out of bounds")
//         if to < from_:
//             raise CompilerError("to < from_ is an error.")
                
//         // save str data
//         next = _._next_token // also = from_tok and to_tok
//         from_tok: Token|None = _.tokens[from_] if from_ < count else next
//         str_from = from_tok.start if from_tok else _._len_sapi_str

//         before_to_tok: Token|None = _.tokens[to - 1] if to > 0 and to - 1 < count else next if to > 0 else None
//         str_to = str_from if to == from_ else before_to_tok.end + 1 if before_to_tok else _._len_sapi_str // traditional
        
//         _._str_replacements.append(StrReplacement(str_from, str_to, new_text, is_new_clause))




    pub fn recursive_str_replacements(&self, bump: &'a Bump) -> bVec<'a, StrReplacement<'a>> {
        bVec::new_in(bump)
//         "used by editor, but not by other parts of parser."
//         str_replacements: list[StrReplacement] = []
//         str_replacements += _._str_replacements
//         for tok in _.tokens:
//             if isinstance(tok, TokenTree):
//                 str_replacements += tok.recursive_str_replacements()
//         return str_replacements
    }
}


// fn common_select_clauses(): 
//     return [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
//             TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]
