#![allow(dead_code, unused_imports, unused_variables, unused_parens)]
mod internals;
pub use internals::*;
// use sqlparser::tokenizer::{Tokenizer, Token, Whitespace};
// use sqlparser::dialect::PostgreSqlDialect;

#[no_mangle]
pub extern "C" fn sapi_add(left: u64, right: u64) -> u64 {
    add(left, right)
}
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

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

