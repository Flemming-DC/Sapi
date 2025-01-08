// from . import select_analyzer, path_finder, join_generator
// from sapi._internals.token_tree import TokenTree, StrReplacement
// from sapi._internals.select_.analyzer_loop import AnalyzerLoop
use bumpalo::Bump;
use bumpalo::collections::{Vec as bVec, String as bString};
use crate::internals::token_tree::{TokenTree, StrReplacement, tok_text};
use super::tree_join::{TreeJoin, Resolvent};
use super::analyzer_loop::AnalyzerLoop;
use super::*;

pub fn parse_select<'a>(bump: &'a Bump, token_tree: &'a TokenTree<'a>) -> bVec<'a, StrReplacement<'a>> {
    let (tree_joins, resolvents) = select_analyzer::find_tree_joins(bump, AnalyzerLoop::new(token_tree));

    join_generator::resolve_trees_to_tabs(token_tree, &resolvents);
    for tree_join in tree_joins {
        let (path, eldest) = path_finder::join_path(
            &tree_join.referenced_tables, tree_join.first_table, tok_text(&tree_join.tree_tok));
        join_generator::make_join_clauses(token_tree, &tree_join, path, eldest);
    }

    let replacements = token_tree.recursive_str_replacements(bump);
    return replacements
}


