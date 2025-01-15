use bumpalo::collections::Vec as bVec;
use bumpalo::Bump;
use sqlparser::tokenizer::{Token, TokenWithSpan, Tokenizer, TokenizerError, Whitespace};
use sqlparser::dialect::{dialect_from_str, PostgreSqlDialect};
use sqlparser::keywords::Keyword;
use super::token_tree::TokenTree;
use super::token::*;
use crate::{brk_if, dbg_assert, if_dbg, Piter, P};

// Result<Vec<TokenWithSpan>, TokenizerError>
pub fn tokenize<'a>(bump: &'a Bump, dialect_name: &'a str, sapi_stmt: &'a str) -> Option<&'a TokenTree<'a>> {
    // glot_tokens: list[glotToken] = data_model.dialect().sqlglot_dialect().tokenize(sapi_stmt) 
    let dialect = dialect_from_str(dialect_name).unwrap(); // fixme
    // evt use tokenize_with_location_into_buf or tokenize_with_location
    let tokens_raw: Vec<TokenWithSpan> = Tokenizer::new(&*dialect, sapi_stmt).tokenize_with_location().unwrap(); // fix unwrap
    let tokens: bVec<'a, Tok<'a>> = format_tokens(bump, tokens_raw, sapi_stmt);

    // cut_leading_junk(&bump, &tokens);
    if tokens.is_empty() { return None; }
    let (tree, _) = make_nested_tok_tree(bump, &tokens, 0, sapi_stmt);
    return Some(tree);
}

fn make_nested_tok_tree<'a>(bump: &'a Bump, all_tokens: &[Tok<'a>], mut i: usize, sapi_str: &'a str) -> (&'a TokenTree<'a>, usize) {
    // if all_tokens[i] == Token::LParen {
    //     raise (if i == 0 {QueryError}  else {CompilerError})("TokenTree should not start with ("); // fix me
    // }
    let mut depth: usize = 0; // parenthesis nesting depth
    let token_count = all_tokens.len();
    let mut tokens_at_this_level: bVec<Tok> = bVec::with_capacity_in(10, &bump); // number is a guess

    let continue_ = |i: usize, depth: usize|  {
        if i >= token_count { return false; } 
        let depth_goes_negative = (all_tokens[i].typ == TokTy::RParen && depth <= 0);
        return (all_tokens[i].typ != TokTy::SemiColon) && !depth_goes_negative;
    };

    while continue_(i, depth) {
        let mut tok: Tok<'a> = all_tokens[i].clone();
        match &all_tokens[i].typ {
            TokTy::LParen => { depth += 1; } // evt. check if next token if a sub query start
            TokTy::RParen => { depth -= 1; }
            TokTy::Keyword => {
                let Some(kw) = &all_tokens[i].keyword() else { unreachable!() };
                if depth > 0 && matches!(kw, Keyword::SELECT | Keyword::INSERT | Keyword::UPDATE | Keyword::DELETE) {
                    // we don't want to recursively parse the outermost select, ergo depth > 0 check
                    let (sub_tree, j) = make_nested_tok_tree(bump, all_tokens, i, sapi_str);
                    i = j;
                    tok.typ = TokTy::Tree;
                    tok.data = bump.alloc(TokData::Tree(sub_tree));
                }
            }
            _ => {}
        }
        tokens_at_this_level.push(tok); // token can be overridden by a sub_tree
        i += 1;
    }
    if i < token_count && all_tokens[i].typ == TokTy::RParen {
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


fn format_tokens<'a>(bump: &'a Bump, tokens: Vec<TokenWithSpan>, sapi_stmt: &'a str) -> bVec<'a, Tok<'a>> {
    let mut out_tokens = bVec::with_capacity_in(tokens.len(), bump);
    let lines: bVec<&str> = bVec::from_iter_in(sapi_stmt.lines(), bump);
    let mut line_start_idx: usize = 0;
    let mut last_tok_line_nr: usize = 1; // starts at one
    let mut index_from_line_and_col = |line_nr: usize, col_nr: usize| -> usize { 
        let line = lines[line_nr - 1];
        while line_nr > last_tok_line_nr {
            let last_line = lines[last_tok_line_nr - 1];
            line_start_idx += last_line.len() + 1; // +1 for \n (what about \r\n?) 
            last_tok_line_nr += 1;
        } 
        // The end can be lines.len() even if 0 indexed (i.e. outside the boundary)
        // Thus if 1 indexed it go one step above
        dbg_assert!(line_nr > 0 && line_nr - 1 <= lines.len()); 
        dbg_assert!(col_nr - 1 <= line.len(), [col_nr, line.len()]);
        dbg_assert!(line_nr == last_tok_line_nr, "last_tok_line_nr has been updated");
        dbg_assert!(!line.contains('\r'), "\r\n probably forces some +1 to become +2, so that the code must be edited.");
        if_dbg!( // this check may be a little overkill as it is O(n^2)
            let preceding_chars: usize = lines[..line_nr - 1].iter().map(|line| line.len() + 1).sum();  // + 1 for \n
            dbg_assert!(preceding_chars == line_start_idx, [preceding_chars, line_start_idx]);
        );
        return line_start_idx + col_nr - 1;
    };

    let mut has_passed_leading_junk = false;
    for tok in tokens {
        if let Token::Whitespace(_) = tok.token { continue; }

        let start_idx = index_from_line_and_col(
            tok.span.start.line as usize, tok.span.start.column as usize); 
        let end_idx = index_from_line_and_col(
            tok.span.end.line as usize, tok.span.end.column as usize); 
        dbg_assert!(sapi_stmt.len() >= end_idx && end_idx >= start_idx);

        let typ = TokTy::new(tok.token.clone());

        if !has_passed_leading_junk && typ != TokTy::Keyword { // evt. make this optional.
            has_passed_leading_junk = true;
            continue; 
        } 

        let out_tok = Tok {
            typ: typ,
            text: &sapi_stmt[start_idx..end_idx], 
            start: Location {
                idx: start_idx, 
                line: tok.span.start.line, 
                column: tok.span.start.column,
            }, 
            end: Location {
                idx: end_idx, 
                line: tok.span.end.line, 
                column: tok.span.end.column,
            }, 
            data: bump.alloc(TokData::new(tok.token)),
        };
        dbg_assert!(match out_tok.data {
            TokData::Tree(..)                 => {out_tok.typ == TokTy::Tree},
            TokData::Keyword(..)              => {out_tok.typ == TokTy::Keyword},
            TokData::Text(..)                 => {true}, // too many options to check
            TokData::Placeholder(..)          => {out_tok.typ == TokTy::Placeholder},
            TokData::CustomBinaryOperator(..) => {out_tok.typ == TokTy::CustomBinaryOperator},
            TokData::MultiLineComment(..)     => {out_tok.typ == TokTy::MultiLineComment},
            TokData::Char(..)                 => {out_tok.typ == TokTy::Char},
            TokData::Number(..)               => {out_tok.typ == TokTy::Number},
            TokData::Identifier {..}          => {out_tok.typ == TokTy::Identifier},
            TokData::DollarQuotedString {..}  => {out_tok.typ == TokTy::DollarQuotedString},
            TokData::SingleLineComment {..}   => {out_tok.typ == TokTy::SingleLineComment},
            TokData::None                     => {true}, // too many options to check
        });
        dbg_assert!(out_tok.end.idx > out_tok.start.idx);
        out_tokens.push(out_tok);
    }
    return out_tokens;
}





// tokenizer::ALL_KEYWORDS
//      use crate::keywords::{Keyword, ALL_KEYWORDS, ALL_KEYWORDS_INDEX};


