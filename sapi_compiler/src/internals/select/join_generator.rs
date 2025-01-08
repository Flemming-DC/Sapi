// from sapi._internals.db_contact import data_model
// from sapi._internals.error import QueryError
// from .path_finder import pathType, Node
use crate::internals::db_contact::data_model::Node;
use super::path_finder::PathType;
use crate::internals::token_tree::TokenTree; // , Token, TokenType
use super::tree_join::{TreeJoin, Resolvent};

pub fn make_join_clauses(token_tree: &TokenTree, tree_join: &TreeJoin, path: PathType, eldest: Option<Node>) { 
//     i = tree_join.tree_tok_index
//     if not tree_join.first_table:
//         raise QueryError("Unused tree in from clause.")

//     // replace table_tree with first table in join_path
//     token_tree.make_replacement(i, i + 1, tree_join.first_table, False)

//     // autogenerate the remaining joins in join_path
//     i = tree_join.on_clause_end_index + 1
//     going_up_the_tree = True
//     for tab, next_tab in path:
//         if tab == eldest: // eldest is only None if there are no referenced tables, and that doesn't happen here.
//             going_up_the_tree = False
//         referenced_table = next_tab if going_up_the_tree else tab

//         // check for alternative join clauses in the tree
//         // this code assumes that foreign key and primary keys follow your naming convention.
//         // in the general case, then you need next_tab, referenced_table and a join rule to make join_clause_tokens
//         // join_clause = f"JOIN {next_tab.name} USING ({referenced_table.name}_id)"    

//         child_table = next_tab if not going_up_the_tree else tab
//         join_clause = data_model.join_clause_by_tab(child_table.name, going_up_the_tree)
//         token_tree.make_replacement(i, i, join_clause, True) // equivalent to insert
}
    

pub fn resolve_trees_to_tabs(token_tree: &TokenTree, resolvents: &[Resolvent]) {
//     for r in resolvents: // ie.e tables resolved from trees 
//         token_tree.make_replacement(r.index, r.index + 1, r.tab_name, False)
}

