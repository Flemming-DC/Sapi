use std::cell::RefCell;

// from . import select_analyzer, path_finder, join_generator
// from sapi._internals.token_tree import TokenTree, StrReplacement
// from sapi._internals.select_.analyzer_loop import AnalyzerLoop
use bumpalo::Bump;
use bumpalo::collections::{Vec as bVec, String as bString};
use crate::internals::token_tree::{TokenTree, StrReplacement};
use crate::{DataModel, P};
use super::tree_join::{TreeJoin, Resolvent};
use super::analyzer_loop::AnalyzerLoop;
use super::*;

pub fn compile_select<'a>(bump: &'a Bump, model: &DataModel, token_tree: &'a TokenTree<'a>, sapi_stmt: &'a str) 
    -> bVec<'a, StrReplacement<'a>> {
    let lup = AnalyzerLoop::new(token_tree);
    let (tree_joins, resolvents) = select_analyzer::find_tree_joins(
        bump, model, &lup);

    // P!(&tree_joins);
    join_generator::resolve_trees_to_tabs(token_tree, &resolvents);
    for tree_join in tree_joins {
        let (path, eldest) = path_finder::join_path(
            &tree_join.referenced_tables, tree_join.first_table, &tree_join.tree_tok.text);
        join_generator::make_join_clauses(token_tree, &tree_join, path, eldest);
    }

    let replacements = token_tree.recursive_str_replacements(bump);
    return replacements
}


