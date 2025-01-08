



pub struct DataModel; // stub
pub struct Dialect; // stub
pub struct Node; // stub

pub fn is_var(tok_text: &str)                                   -> bool { false }
pub fn is_tree(tok_text: &str)                                  -> bool { false }
pub fn is_table(tok_text: &str)                                 -> bool { false }
pub fn tables_by_var(var: &str)                                 -> &[&str] { &[] }
pub fn trees_by_table(table_name: &str)                         -> &[&str] { &[] }
pub fn tables_by_var_and_tree<'a>(var: &'a str, tree: &'a str)  -> &'a [&'a str] { &[] }
pub fn primary_key_by_tab(table_name: &str)                     -> &str { "" }
pub fn join_clause_by_tab(table_name: &str, going_up: bool)     -> &str { "" }
pub fn node_by_tab_and_tree(tab: &str, tree: &str)              -> Node { Node{} }
pub fn dialect()                                                -> Dialect { Dialect{} }




