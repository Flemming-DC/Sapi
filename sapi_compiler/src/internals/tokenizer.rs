use bumpalo::collections::Vec as bVec;
use bumpalo::Bump;
use sqlparser::keywords::Keyword;
use sqlparser::tokenizer::{Token, TokenWithSpan, Tokenizer, TokenizerError, Whitespace};
use sqlparser::dialect::PostgreSqlDialect;
use super::token_tree::{TokenTree, TokNode};

// Result<Vec<TokenWithSpan>, TokenizerError>
pub fn tokenize<'a>(bump: &'a Bump, sapi_stmt: &str) -> Option<&'a TokenTree<'a>> {
    // glot_tokens: list[glotToken] = data_model.dialect().sqlglot_dialect().tokenize(sapi_stmt) 
    let dialect = PostgreSqlDialect {}; // temp
    // evt use tokenize_with_location_into_buf or tokenize_with_location
    let tokens = Tokenizer::new(&dialect, sapi_stmt).tokenize().unwrap(); // fix unwrap
    // if necesary format tokens

    cut_leading_junk(&bump, &tokens);
    if tokens.is_empty() { return None; }
    let (tree, _) = make_nested_tok_tree(bump, &tokens, 0, sapi_stmt);
    return Some(tree);
}


fn make_nested_tok_tree<'a>(bump: &'a Bump, all_tokens: &[Token], mut i: usize, sapi_str: &str) -> (&'a TokenTree<'a>, usize) {
    // if all_tokens[i] == Token::LParen {
    //     raise (if i == 0 {QueryError}  else {CompilerError})("TokenTree should not start with ("); // fix me
    // }
    let mut depth: usize = 0; // parenthesis nesting depth
    let token_count = all_tokens.len();
    let mut tokens_at_this_level: bVec<TokNode> = bVec::with_capacity_in(10, &bump); // number is a guess

    fn _continue(i: usize, depth: usize, token_count: usize, tok: &Token) -> bool {
        if i >= token_count { return false; } 
        let depth_goes_negative = (*tok == Token::RParen && depth <= 0);
        return (*tok == Token::SemiColon) && !depth_goes_negative;
    }
       
    
    while _continue(i, depth, token_count, &all_tokens[i]) {
        let mut tok_node = TokNode::Leaf(all_tokens[i].clone());
        match &all_tokens[i] {
            Token::LParen => { depth += 1; } // evt. check if next token if a sub query start
            Token::RParen => { depth -= 1; }
            Token::Word(word) => {
                if depth > 0 && matches!(word.keyword, Keyword::SELECT | Keyword::INSERT | Keyword::UPDATE | Keyword::DELETE) {
                    // we don't want to recursively parse the outermost select, ergo depth > 0 check
                    let (sub_tree, i) = make_nested_tok_tree(bump, all_tokens, i, sapi_str);
                    tok_node = TokNode::Tree(sub_tree);
                }
            }
            _ => {}
        }
        tokens_at_this_level.push(tok_node); // token can be overridden by a sub_tree
        i += 1;
    }
    if i < all_tokens.len() && all_tokens[i] == Token::RParen {
        i -= 1; // dont include finishing parenthesis
    }
    let next_token = if i + 1 < all_tokens.len() { Some(all_tokens[i + 1].clone()) } else { None };
    //let next_token = if i + 1 < all_tokens.len() { Some(Token(**all_tokens[i + 1].__dict__)) } else { None };
    // if next_token is not None and next_token.line > all_tokens[i].line:
    //     next_token.line = all_tokens[i].line
    // make single layer of token_tree
    let token_tree = bump.alloc(TokenTree::new(tokens_at_this_level, sapi_str.len(), next_token));
    return (token_tree, i);
}

fn cut_leading_junk<'a>(bump: &'a Bump, tokens: &'a [Token]) -> bVec<'a, Token> {
    for (i, tok) in tokens.iter().enumerate() {
        // if tok.type in _keywords:
        if let Token::Word(word) = tok {
            // check if word.keyword is empty (whatever that means)
            // tokens = tokens[i:] // modifying list is ok, since we break the loop
            for tok in tokens[i..].iter() {}
            return bVec::from_iter_in(tokens[i..].iter().map(|t| (*t).clone()), &bump);
        }
    }
    return bVec::from_iter_in(tokens.iter().map(|t| (*t).clone()), &bump);
}

//     /// A keyword (like SELECT) or an optionally quoted SQL identifier
//     Word(Word), 
//         /// If the word was not quoted and it matched one of the known keywords,
//         /// this will have one of the values from dialect::keywords, otherwise empty
//         pub keyword: Keyword,
//     dialect::keywords
// // tokenizer::ALL_KEYWORDS
// //      use crate::keywords::{Keyword, ALL_KEYWORDS, ALL_KEYWORDS_INDEX};