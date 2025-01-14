use super::*;
use super::select_analyzer::*;

use bumpalo::Bump;
use bumpalo::collections::Vec as bVec;
use bumpalo::collections::String as bString;
use sqlparser::keywords::Keyword;
use sqlparser::tokenizer::Token;
use crate::internals::error::SapiError::QueryError; //, CompilerError
use crate::internals::db_contact::data_model::DataModel;
use crate::internals::token::Location;
use crate::internals::token::TokTy;
use crate::internals::token::{Tok, TokData, TokTy::*};
use crate::internals::token_tree::TokenTree;
use crate::zip::zip_longest;
use crate::P; 
use super::analyzer_loop::AnalyzerLoop;
use super::tree_join::{TreeJoin, Resolvent};


fn test_get_expected_tree_joins(model: &DataModel) {
    let bump = Bump::new();
    let sapi_stmt: &str = r"
WITH cte AS (
    SELECT col0_1, col0_2, col00_2 FROM tree
)
SELECT 
    cte.col00_2,
    col10_2,
    (SELECT count(col20_2) FROM tree)
-- here we have a select query. sapi parsed to sql
FROM cte 
join tree ON tree.col_1 = cte.col0_1
    ";
    
    // ------- tokens ---------
    let ir = 0; // ir = irrelevant
    let ir_td = TokData::new(Token::EOF);
    let new_tok = |typ, start_idx, end_idx| { Tok {
        typ: typ,
        text: &sapi_stmt[start_idx..end_idx], 
        start: Location { idx: start_idx, line: ir, column: ir }, 
        end: Location { idx: end_idx, line: ir, column: ir }, 
        data: bump.alloc(ir_td.clone()),
    }};
    
    let tokens1 = bVec::from_iter_in([
        new_tok(Keyword, 3, 27),
        new_tok(Identifier,  3, 34),
        new_tok(Period,  3, 34),
        new_tok(Identifier,  3, 34),
        new_tok(Comma,3, 38),
        new_tok(Identifier,  3, 40),
        new_tok(Period,  3, 40),
        new_tok(Identifier,  3, 40),
        new_tok(Comma,3, 44),
        new_tok(Identifier,  3, 46),
        new_tok(Period,  3, 46),
        new_tok(Identifier,  3, 46),
        new_tok(Keyword, 3, 52),
        new_tok(Identifier,  3, 57),
    ], &bump);
    
    // ------- tokens ---------
    let tokens2 = bVec::from_iter_in([
        new_tok(Keyword, 8, 120),
        new_tok(Identifier, 8, 127),
        new_tok(LParen, 8, 130),
        new_tok(Identifier, 8, 131),
        new_tok(RParen, 8, 136),
        new_tok(Keyword, 8, 138),
        new_tok(Identifier, 8, 143),
    ], &bump);
    // ------- tokens ---------
    let sub_token_tree1 = TokenTree::new(
        tokens1, sapi_stmt.len(), Some(new_tok(RParen, 4, 63))
    );
    let sub_token_tree2 = TokenTree::new(
        tokens2, sapi_stmt.len(), Some(new_tok(RParen, 8, 144))
    );
    
    let tokens3 = bVec::from_iter_in([
        new_tok(Keyword,  2, 5),
        new_tok(Identifier, 2, 10),
        new_tok(Keyword, 2, 14),
        new_tok(LParen, 2, 17),
        new_tok(Tree, 4, 63), // sub_token_tree1
        new_tok(RParen, 4, 63),
        new_tok(Keyword, 5, 69),
        new_tok(Identifier, 6, 85),
        new_tok(Period, 6, 88),
        new_tok(Identifier, 6, 89),
        new_tok(Comma, 6, 94),
        new_tok(Identifier,7, 104),
        new_tok(Comma,7, 109),
        new_tok(LParen,8, 119),
        new_tok(Tree, 8, 144), // sub_token_tree2
        new_tok(RParen, 8,  144),
        new_tok(Keyword, 11, 198),
        new_tok(Identifier, 11, 203),
        new_tok(Keyword, 12, 212),
        new_tok(Identifier, 12, 217),
        new_tok(Keyword, 12, 219),
        new_tok(Identifier, 12, 222),
        new_tok(Period, 12, 223),
        new_tok(Identifier, 12, 224),
        new_tok(Keyword, 12, 228),
        new_tok(Identifier, 12, 230),
        new_tok(Period, 12, 233),
        new_tok(Identifier, 12, 234),
    ], &bump);
    let root_token_tree3 = TokenTree::new(
        tokens3, sapi_stmt.len(), None
    );

    let expected_1 = TreeJoin { 
        tree_tok: new_tok(Identifier, 3, 57), 
        tree_tok_index: 13,
        on_clause_end_index: 13, 
        first_table: Some("a0"), 
        referenced_tables: bVec::from_iter_in(["a0", "a0", "a00"], &bump),
    };
    let expected_2 = TreeJoin { 
        tree_tok: new_tok(Identifier, 8, 143),
        tree_tok_index: 8, 
        on_clause_end_index: 8, 
        first_table: Some("a20"), 
        referenced_tables: bVec::from_iter_in(["a20"], &bump),
    };
    let expected_3 = TreeJoin { 
        tree_tok: new_tok(Identifier, 12, 217), 
        tree_tok_index: 21, 
        on_clause_end_index: 29, 
        first_table: Some("a"), 
        referenced_tables: bVec::from_iter_in(["a10", "a"], &bump),
    };
    let expected_1 = [expected_1];
    let expected_2 = [expected_2];
    let expected_3 = [expected_3];

    let cases = [
        (expected_1, sub_token_tree1),
        (expected_2, sub_token_tree2),
        (expected_3, root_token_tree3),
    ];

    for (expected, tok_tree) in cases {
        let lup = AnalyzerLoop::new(&tok_tree);
        let (actual, _) = select_analyzer::find_tree_joins(&bump, model, &lup);
        for (a, e) in zip_longest(actual.iter(), expected.iter()) { // zip_longest
            // assert!(equal_join_data(a, e));
            assert_eq!(a, e);
        }
    }

}

// fn equal_join_data<'a>(j1: Option<&TreeJoin<'a>>, j2: Option<&TreeJoin<'a>>) -> bool {
    
//     let new_tok = |typ, start_idx, end_idx| { Tok {
//         typ: typ,
//         text: &sapi_stmt[start_idx..end_idx], 
//         start: Location { idx: start_idx, line: ir, column: ir }, 
//         end: Location { idx: end_idx, line: ir, column: ir }, 
//         data: bump.alloc(ir_td),
//     }};

//     match (j1, j2) {
//         (None, None) => return true,
//         (Some(_), None) => return false,
//         (None, Some(_)) => return false,
//         (Some(j1), Some(j2)) => {
//             let jo1 = j1.tree_tok;
//             let jot1 = (jo1.typ, jo1.text, jo1.line, jo1.start);
//             let j1_comparable = (jot1, j1.on_clause_end_index, j1.first_table, j1.referenced_tables);
        
//             let jo2 = j2.tree_tok;
//             let jot2 = (jo2.typ, jo2.text, jo2.line, jo2.start);
//             let j2_comparable = (jot2, j2.on_clause_end_index, j2.first_table, j2.referenced_tables);
        
//             return j1_comparable == j2_comparable;
//         }
//     };
// }










