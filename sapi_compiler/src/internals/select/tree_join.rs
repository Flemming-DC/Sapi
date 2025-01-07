use crate::internals::token_tree::TokenTree;
use sqlparser::tokenizer::Token;

#[derive(Debug)]
pub struct TreeJoin<'a> {
    pub tree_tok: &'a Token, // this is not a TokenTree, but an identifier for a table_tree
    pub tree_tok_index: usize,
    pub on_clause_end_index: usize,
    pub first_table: Option<&'a str>, // = None // the unique element of on_clause_tables except prior_tables
    pub referenced_tables: &'a [&'a str], // = [] // referenced tables. aka. those tables that must be autojoined.
}
//     fn __str__(_) {
//         return 'JoinData(' + ', '.join([
//         'tree_tok: ' + str(_.tree_tok.text), 
//         'tree_tok_index: ' + str(_.on_clause_end_index), 
//         'first_table: ' + str(_.first_table), 
//         'referenced_tables: ' + str(_.referenced_tables), 
//         ]) + ')'
// }

pub struct Resolvent<'a> { // info to resolve a tree into a table
    index: usize,
    tab_name: &'a str,
    // tree name isnt specified
}