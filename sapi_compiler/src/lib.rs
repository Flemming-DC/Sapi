#![allow(dead_code, unused_imports, unused_variables, unused_parens)]
mod internals;
pub use internals::*;
// use sqlparser::tokenizer::{Tokenizer, Token, Whitespace};
// use sqlparser::dialect::PostgreSqlDialect;

use std::os::raw::{c_char, c_uchar, c_uint};

#[repr(C)] #[allow(non_camel_case_types)] pub struct c_str {ptr: *const c_char, len: u32}

#[no_mangle]
pub extern "C" fn sapi_add(left: u64, right: u64) -> u64 {
    
    add(left, right)
}
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[no_mangle]
pub extern "C" fn ib_sl(x: c_str) -> c_str {
    // dbg!(&x);
    x
}
#[no_mangle]
pub extern "C" fn ib_nt(x: *const c_char) -> *const c_char {
    dbg!(&x);
    x
}

// #[cfg(test)]
// mod tests {
//     use super::*;

//     #[test]
//     fn test_no_chrash() {
//         let join_clause = Some("JOIN __parent__ USING (__keys__)");
//         let tree = Tree { name: "tree", schema: "sapi_demo", tables: vec![
//             Table {name: "tab",   primary_key: "tab_id",   parent: None,         join_clause: join_clause, columns: vec!["col_1", "col_2", "tab_id"]}, 
//             Table {name: "tab0",  primary_key: "tab0_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col0_1", "col0_2", "shc", "tab0_id", "tab1__id", "tab_id"]}, 
//             Table {name: "tab00", primary_key: "tab00_id", parent: Some("tab0"), join_clause: join_clause, columns: vec!["col00_1", "col00_2", "tab00_id", "tab0_id"]}, 
//             Table {name: "tab01", primary_key: "tab01_id", parent: Some("tab0"), join_clause: join_clause, columns: vec!["col01_1", "col01_2", "tab01_id", "tab0_id"]}, 
//             Table {name: "tab1",  primary_key: "tab1_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col1_1", "col1_2", "shc", "tab0__id", "tab1_id", "tab_id"]}, 
//             Table {name: "tab10", primary_key: "tab10_id", parent: Some("tab1"), join_clause: join_clause, columns: vec!["col10_1", "col10_2", "tab10_id", "tab1_id"]}, 
//             Table {name: "tab2",  primary_key: "tab2_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col2_1", "col2_2", "tab2_id", "tab_id"]}, 
//             Table {name: "tab20", primary_key: "tab20_id", parent: Some("tab2"), join_clause: join_clause, columns: vec!["col20_1", "col20_2", "tab20_id", "tab2_id"]}, 
//             Table {name: "tab21", primary_key: "tab21_id", parent: Some("tab2"), join_clause: join_clause, columns: vec!["col21_1", "col21_2", "tab21_id", "tab2_id"]}, 
//             Table {name: "sht__", primary_key: "sht___id", parent: Some("tab"),  join_clause: join_clause, columns: vec!["col_1__", "col_2__", "sht___id", "tab__id", "tab_id"]}, 
//         ]};
//         let model_id = DataModel::new("postgres", vec![tree]);
    
//         let sapi_query = r"
//             WITH cte AS (
//                 SELECT col0_1, col0_2, col00_2 FROM tree
//             )
//             SELECT 
//                 cte.col00_2,
//                 col10_2,
//                 (SELECT count(col20_2) FROM tree)
//             -- here we have a select query. sapi parsed to sql
//             FROM cte 
//             join tree ON tree.col_1 = cte.col0_1
//             ";
//         let sql = compiler::compile(sapi_query.into(), model_id);
//     }
// }


// pub fn sandbox() {
//     let sapi_query = r"
//         WITH cte AS (
//             SELECT col0_1, col0_2, col00_2 FROM tree
//         )
//         SELECT 
//             cte.col00_2,
//             col10_2,
//             (SELECT count(col20_2) FROM tree)
//         -- here we have a select query. sapi parsed to sql
//         FROM cte 
//         join tree ON tree.col_1 = cte.col0_1
//         ";
//     // sqlparser::tokenizer
//     parser::parse(sapi_query.into(), &parser::DataModel);
// }

