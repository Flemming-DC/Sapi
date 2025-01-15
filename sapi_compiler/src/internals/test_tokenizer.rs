// use bumpalo::collections::Vec as bVec;
// use bumpalo::Bump;
// use sqlparser::tokenizer::{Token, TokenWithSpan, Tokenizer, TokenizerError, Whitespace};
// use sqlparser::dialect::{dialect_from_str, PostgreSqlDialect};
// use sqlparser::keywords::Keyword;
// use super::token_tree::TokenTree;
// use super::token::*;
// use crate::{brk_if, dbg_assert, if_dbg, Piter, P};




// fn test_() {
        
//     "---"
//     new_tok(Keyword, 18, 24),      // "SELECT"
//     new_tok(Identifier, 25, 31),   // "col0_1"
//     new_tok(Comma, 31, 32),        // ","
//     new_tok(Identifier, 33, 39),   // "col0_2"
//     new_tok(Comma, 39, 40),        // ","
//     new_tok(Identifier, 41, 48),   // "col00_2"
//     new_tok(Keyword, 49, 53),      // "FROM"
//     new_tok(Identifier, 54, 58),   // "tree"
//     "---"
//     new_tok(Keyword, 104, 110),    // "SELECT"
//     new_tok(Keyword, 111, 116),    // "count"
//     new_tok(LParen, 116, 117),     // "("
//     new_tok(Identifier, 117, 124), // "col20_2"
//     new_tok(RParen, 124, 125),     // ")"
//     new_tok(Keyword, 126, 130),    // "FROM"
//     new_tok(Identifier, 131, 135), // "tree"
//     "---"
//     new_tok(Keyword, 0, 4),        // "WITH"
//     new_tok(Keyword, 9, 11),       // "AS"
//     new_tok(LParen, 12, 13),       // "("
//     // new_tok(Tree, 18, 24),         // "SELECT" # change text and idx
//     new_tok(RParen, 59, 60),       // ")"
//     new_tok(Keyword, 61, 67),      // "SELECT"
//     new_tok(Identifier, 73, 76),   // "cte"
//     new_tok(Period, 76, 77),       // "."
//     new_tok(Identifier, 77, 84),   // "col00_2"
//     new_tok(Comma, 84, 85),        // ","
//     new_tok(Identifier, 90, 97),   // "col10_2"
//     new_tok(Comma, 97, 98),        // ","
//     new_tok(LParen, 103, 104),     // "("
//     // new_tok(Tree, 104, 110),       // "SELECT" # change text and idx
//     new_tok(RParen, 135, 136),     // ")"
//     new_tok(Keyword, 188, 192),    // "FROM"
//     new_tok(Identifier, 193, 196), // "cte"
//     new_tok(Keyword, 198, 202),    // "join"
//     new_tok(Identifier, 203, 207), // "tree"
//     new_tok(Keyword, 208, 210),    // "ON"
//     new_tok(Identifier, 211, 215), // "tree"
//     new_tok(Period, 215, 216),     // "."
//     new_tok(Identifier, 216, 221), // "col_1"
//     new_tok(Eq, 222, 223),         // "="
//     new_tok(Identifier, 224, 227), // "cte"
//     new_tok(Period, 227, 228),     // "."
//     new_tok(Identifier, 228, 234), // "col0_1"
// }
    
