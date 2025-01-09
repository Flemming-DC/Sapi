
use bumpalo::Bump;
use sqlparser::{keywords::Keyword, tokenizer::{Token, TokenWithSpan}}; // sqlglot.tokens import TokenType
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


#[derive(Debug, Clone, PartialEq)]
pub struct StrReplacement<'a> {
    pub str_from: usize,
    pub str_to: usize,
    pub text: &'a str,
    pub is_new_clause: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TokNode<'a> { Leaf(Token), Tree(&'a TokenTree<'a>) } // size_of Token and TokenWithSpan are 56, 88 Bytes. Unnecesarily large.

impl<'a> TokNode<'a> {
    pub fn text(&self) -> &'static str { "" } // where to put this?
    pub fn start(&self) -> usize { 0 } // where to put this?
    pub fn end(&self) -> usize { 0 } // where to put this?
    pub fn is_identifier(&self) -> bool { 
        if let TokNode::Leaf(Token::Word(word)) = self { 
            word.keyword == Keyword::NoKeyword // check if word.keyword is empty (whatever that means)
        } else {false} 
    }
    pub fn is_kw(&self, keyword: Keyword) -> bool { 
        if let TokNode::Leaf(Token::Word(word)) = self { 
            word.keyword == keyword // check if word.keyword is empty (whatever that means)
        } else {false} 
    }
    
}

#[derive(Debug, PartialEq)]
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
        

    pub fn make_replacement(&mut self, from_: usize, to: usize, new_text: &'a str, is_new_clause: bool) {
        let count = self.tokens.len();
        if to > count { panic!("index out of bounds"); }
        if to < from_ { panic!("to < from_ is an error."); }

        // save str data
        let next = self.next_token.as_ref().map(|n|TokNode::Leaf(n.clone())); // also = from_tok and to_tok
        let from_tok = if from_ < count {Some(self.tokens[from_].clone())} else {next.clone()};
        let str_from = if from_tok != None {from_tok.expect("checked").start()} else {self.len_sapi_str};

        let before_to_tok = if to > 0 && to - 1 < count {Some(self.tokens[to - 1].clone())} else if to > 0 {next} else {None};
        let str_to = if to == from_ {str_from} else if before_to_tok != None {before_to_tok.expect("checked").end() + 1} else {self.len_sapi_str}; // traditional
        
        self.str_replacements.push(StrReplacement {str_from, str_to, text: new_text, is_new_clause });
    }



    pub fn recursive_str_replacements(&self, bump: &'a Bump) -> bVec<'a, StrReplacement<'a>> {
        // used by editor, but not by other parts of parser.
        let mut str_replacements = bVec::from_iter_in(self.str_replacements.iter().cloned(), bump);
        for tok in &self.tokens {
            if let TokNode::Tree(tok) = tok {
                str_replacements.extend_from_slice(&tok.recursive_str_replacements(bump)); }}
        return str_replacements;
    }
}


// fn common_select_clauses(): 
//     return [TokenType.SELECT, TokenType.FROM, TokenType.JOIN, TokenType.LEFT, TokenType.RIGHT, 
//             TokenType.OUTER, TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.ORDER_BY, TokenType.LIMIT]
