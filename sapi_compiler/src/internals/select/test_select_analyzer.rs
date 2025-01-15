use super::*;
use super::select_analyzer::*;
use bumpalo::Bump;
use bumpalo::collections::Vec as bVec;
use bumpalo::collections::String as bString;
use sqlparser::keywords::Keyword;
use sqlparser::tokenizer::Token;
use crate::brk_if;
use crate::dbg_assert;
use crate::internals::db_contact::data_model::DataModel;
use crate::internals::db_contact::data_model;
use crate::internals::token::Location;
use crate::internals::token::TokTy;
use crate::internals::token::{Tok, TokData, TokTy::*};
use crate::internals::token_tree::TokenTree;
use crate::zip::zip_longest;
use crate::Table;
use super::analyzer_loop::AnalyzerLoop;
use super::tree_join::{TreeJoin, Resolvent};
use crate::P; 

pub mod test { pub use super::test_get_expected_tree_joins; }
#[test] fn test_get_expected_tree_joins_() { test_get_expected_tree_joins(); }
pub fn test_get_expected_tree_joins() {
    let bump = Bump::new();
    let model = runtime_model(&bump);
    let sapi_stmt: &str = r"WITH cte AS (
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
    let new_kw_tok = |kw, start_idx, end_idx| { Tok {
        typ: Keyword,
        text: &sapi_stmt[start_idx..end_idx], 
        start: Location { idx: start_idx, line: ir, column: ir }, 
        end: Location { idx: end_idx, line: ir, column: ir }, 
        data: bump.alloc(TokData::Keyword(kw)),
    }};
    
    let tokens1 = bVec::from_iter_in([
        new_kw_tok(Keyword::SELECT, 18, 24),      // "SELECT"
        new_tok(Identifier, 25, 31),   // "col0_1"
        new_tok(Comma, 31, 32),        // ","
        new_tok(Identifier, 33, 39),   // "col0_2"
        new_tok(Comma, 39, 40),        // ","
        new_tok(Identifier, 41, 48),   // "col00_2"
        new_kw_tok(Keyword::FROM, 49, 53),      // "FROM"
        new_tok(Identifier, 54, 58),   // "tree"
    ], &bump);
    dbg_assert!(&tokens1[0].text == &"SELECT");

    
    // ------- tokens ---------
    let tokens2 = bVec::from_iter_in([
        new_kw_tok(Keyword::SELECT, 104, 110),    // "SELECT"
        new_kw_tok(Keyword::COUNT, 111, 116),    // "count"
        new_tok(LParen, 116, 117),     // "("
        new_tok(Identifier, 117, 124), // "col20_2"
        new_tok(RParen, 124, 125),     // ")"
        new_kw_tok(Keyword::FROM, 126, 130),    // "FROM"
        new_tok(Identifier, 131, 135), // "tree"
    ], &bump);
    dbg_assert!(&tokens2[0].text == &"SELECT");

    // ------- tokens ---------
    let sub_token_tree1 = TokenTree::new(
        tokens1, sapi_stmt.len(), Some(new_tok(RParen, 4, 63))
    );
    let sub_token_tree2 = TokenTree::new(
        tokens2, sapi_stmt.len(), Some(new_tok(RParen, 8, 144))
    );
    
    let tokens3 = bVec::from_iter_in([
        new_kw_tok(Keyword::WITH, 0, 4),        // "WITH"
        new_kw_tok(Keyword::AS, 9, 11),       // "AS"
        new_tok(LParen, 12, 13),       // "("
        new_tok(Tree, 18, 59-1),       // "SELECT col0_1, col0_2, col00_2 FROM tree"
        new_tok(RParen, 59, 60),       // ")"
        new_kw_tok(Keyword::SELECT, 61, 67),      // "SELECT"
        new_tok(Identifier, 73, 76),   // "cte"
        new_tok(Period, 76, 77),       // "."
        new_tok(Identifier, 77, 84),   // "col00_2"
        new_tok(Comma, 84, 85),        // ","
        new_tok(Identifier, 90, 97),   // "col10_2"
        new_tok(Comma, 97, 98),        // ","
        new_tok(LParen, 103, 104),     // "("
        new_tok(Tree, 104, 135-1),       // "SELECT count(col20_2) FROM tree"
        new_tok(RParen, 135, 136),     // ")"
        new_kw_tok(Keyword::FROM, 188, 192),    // "FROM"
        new_tok(Identifier, 193, 196), // "cte"
        new_kw_tok(Keyword::JOIN, 198, 202),    // "join"
        new_tok(Identifier, 203, 207), // "tree"
        new_kw_tok(Keyword::ON, 208, 210),    // "ON"
        new_tok(Identifier, 211, 215), // "tree"
        new_tok(Period, 215, 216),     // "."
        new_tok(Identifier, 216, 221), // "col_1"
        new_tok(Eq, 222, 223),         // "="
        new_tok(Identifier, 224, 227), // "cte"
        new_tok(Period, 227, 228),     // "."
        new_tok(Identifier, 228, 234), // "col0_1"
    ], &bump);
    dbg_assert!(&tokens3[0].text == &"WITH");
    let root_token_tree3 = TokenTree::new(
        tokens3, sapi_stmt.len(), None
    );

    let expected_1 = TreeJoin { 
        tree_tok: new_tok(Identifier, 54, 58),
        tree_tok_index: 7,
        on_clause_end_index: 7, 
        first_table: Some("tab0"), 
        referenced_tables: bVec::from_iter_in(["tab0", "tab00"], &bump),
    };
    let expected_2 = TreeJoin { 
        tree_tok: new_tok(Identifier, 131, 135),
        tree_tok_index: 6, 
        on_clause_end_index: 6, 
        first_table: Some("tab20"), 
        referenced_tables: bVec::from_iter_in(["tab20"], &bump),
    };
    let expected_3 = TreeJoin { 
        tree_tok: new_tok(Identifier, 211, 215), 
        tree_tok_index: 19, 
        on_clause_end_index: 27, 
        first_table: Some("tab"), 
        referenced_tables: bVec::from_iter_in(["tab10"], &bump),
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
            brk_if!(a != e);
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


fn runtime_model(bump: &Bump) -> &DataModel {
    let join_clause = Some("JOIN __parent__ USING (__keys__)");
    let tree = data_model::Tree { name: "tree", schema: "sapi_demo", tables: vec![
        Table {name: "tab",   primary_key: "tab_id",   parent: None,         join_clause: join_clause, columns: vec!["col_1", "col_2", "tab_id"]}, 
        Table {name: "tab0",  primary_key: "tab0_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col0_1", "col0_2", "shc", "tab0_id", "tab1__id", "tab_id"]}, 
        Table {name: "tab00", primary_key: "tab00_id", parent: Some("tab0"), join_clause: join_clause, columns: vec!["col00_1", "col00_2", "tab00_id", "tab0_id"]}, 
        Table {name: "tab01", primary_key: "tab01_id", parent: Some("tab0"), join_clause: join_clause, columns: vec!["col01_1", "col01_2", "tab01_id", "tab0_id"]}, 
        Table {name: "tab1",  primary_key: "tab1_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col1_1", "col1_2", "shc", "tab0__id", "tab1_id", "tab_id"]}, 
        Table {name: "tab10", primary_key: "tab10_id", parent: Some("tab1"), join_clause: join_clause, columns: vec!["col10_1", "col10_2", "tab10_id", "tab1_id"]}, 
        Table {name: "tab2",  primary_key: "tab2_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col2_1", "col2_2", "tab2_id", "tab_id"]}, 
        Table {name: "tab20", primary_key: "tab20_id", parent: Some("tab2"), join_clause: join_clause, columns: vec!["col20_1", "col20_2", "tab20_id", "tab2_id"]}, 
        Table {name: "tab21", primary_key: "tab21_id", parent: Some("tab2"), join_clause: join_clause, columns: vec!["col21_1", "col21_2", "tab21_id", "tab2_id"]}, 
        Table {name: "sht__", primary_key: "sht___id", parent: Some("tab"),  join_clause: join_clause, columns: vec!["col_1__", "col_2__", "sht___id", "tab__id", "tab_id"]}, 
    ]};
    let model_id = DataModel::new("postgres", vec![tree]);
    return DataModel::get_model_copy(bump, model_id);
}







