use bumpalo::Bump;
use bumpalo::collections::Vec as bVec;
use sqlparser::keywords::Keyword;
use sqlparser::tokenizer::Token;
use crate::internals::error::SapiError::QueryError; //, CompilerError
use crate::internals::db_contact::data_model::DataModel;
use crate::internals::token_tree::{tok_text, TokNode, TokenTree}; // , Token, TokenType
use super::analyzer_loop::AnalyzerLoop;
use super::tree_join::{TreeJoin, Resolvent};


pub fn find_tree_joins<'a>(bump: &'a Bump, model: &'a DataModel, mut lup: AnalyzerLoop<'a>) -> (bVec<'a, TreeJoin<'a>>, bVec<'a, Resolvent<'a>>) {
    // (bVec::new_in(&bump), bVec::new_in(&bump))
    let mut tabs_in_on_clauses: bVec<bVec<&str>> = bVec::new_in(bump); // on_clause_tables_across_joins
    let mut tree_joins: bVec<TreeJoin> = bVec::new_in(bump);
    let mut ref_tables: bVec<&str> = bVec::new_in(bump);
    let mut resolvents: bVec<Resolvent> = bVec::new_in(bump);

    while lup.next() {
        if let TokNode::Tree(_) = lup.tok() { 
            continue; }
        check_for_select_all(model, &lup);
        // analyze from clause
        
        let prior_j = bVec::from_iter_in(tree_joins.iter().map(|j| j.tree_tok.clone()), bump);
        let (tree_join, on_clause_tables_in_join, resolved_tabs_in_join) = make_tree_join(
            bump, model, &mut lup, prior_j);
        resolvents.extend(resolved_tabs_in_join.into_iter());
        if let Some(tree_join) = tree_join {
            if let Some(on_clause_tables_in_join) = on_clause_tables_in_join {
                tree_joins.push(tree_join);
                tabs_in_on_clauses.push(on_clause_tables_in_join.clone());
                continue }
            } else { panic!("INTERNAL COMPILER ERROR: Inkonsistent None case."); }
        
        // find referenced tables and resolve trees outside the from clause
        let (ref_tab, resolvent) = table_ref_and_resolvent(bump, model, &lup);
        if let Some(r) = resolvent { if resolvents.contains(&r) {
            resolvents.push(r); }}
        if let Some(r) = ref_tab { if ref_tables.contains(&r) {
            ref_tables.push(r); }}
    }
    tree_joins = plug_tables_into_tree_joins(bump, model, ref_tables, tree_joins, &tabs_in_on_clauses);
    // if any(j.referenced_tables == [] for j in tree_joins) {
    //     raise QueryError("Unused tree in from clause."); } // fix me
    return (tree_joins, resolvents)
}


fn make_tree_join<'a>(bump: &'a Bump, model: &'a DataModel, lup: &mut AnalyzerLoop, prior_join_objs: bVec<'a, Token>) 
    -> (Option<TreeJoin<'a>>, Option<bVec<'a, &'a str>>, bVec<'a, Resolvent<'a>>) {
    // (None, None, bVec::new_in(bump))
    if !lup.found_kw(&[Keyword::FROM, Keyword::JOIN], 0) {
        return (None, None, bVec::new_in(bump)); }
    lup.next();
    // if not lup.found([Token::VAR, Token::IDENTIFIER], 0) {
    //     raise QueryError("expected identifier or variable after from / join."); }
    
    // pass through join_obj prefix
    while lup.found(&[Token::Period], 1) {
        lup.next();
        lup.next();
    }
    // if lup.at_end() {
    //     raise QueryError("Encountered end of query while parsing prefix (such as schem.tree.table). "
    //                      "Expected an object to join with instead."); }

    let join_obj = lup.tok().clone(); // join_obj at end of join_obj prefixes
    // if let TokNode::Tree(_) = join_obj_ { return QueryError; }} // temp make an error instead
    let TokNode::Leaf(join_obj) = join_obj else { unreachable!("temp uncommented check") };
    let join_obj_index = lup.index();
    if prior_join_objs.contains(&&join_obj) {
        return (None, None, bVec::new_in(bump)); } // don't dublicate join_data (is that actually correct behaviour??)
    let is_tree = model.is_tree(tok_text(&join_obj));

    fn on_clause_done(lup: &AnalyzerLoop) -> bool { 
        return lup.next_at_end() || lup.found_kw(&[ // join or clause-after-from
            Keyword::JOIN, Keyword::INNER, Keyword::LEFT, Keyword::RIGHT, Keyword::OUTER, 
            Keyword::FULL, Keyword::SEMI, Keyword::ANTI, Keyword::LATERAL, Keyword::CROSS, 
            Keyword::CROSS, Keyword::NATURAL,
            Keyword::WHERE, Keyword::GROUP, Keyword::HAVING, Keyword::WINDOW, Keyword::UNION, 
            Keyword::ORDER, Keyword::LIMIT, Keyword::OFFSET, Keyword::FETCH, Keyword::FOR], 1)
    }
    // resolve tree prefixes and record table prefixes in on clause
    let mut on_clause_tables: bVec<&str> = bVec::with_capacity_in(1, bump);
    let mut resolvents: bVec<Resolvent> = bVec::with_capacity_in(1, bump);
    loop {
        if on_clause_done(&lup) { break; }
        lup.next();
        let resolved_tab = None;
        // resolve tree prefixes
        if model.is_tree(lup.tok().text()) {
            // if not lup.found([Token::VAR, Token::IDENTIFIER], 2) { // peek(2) should be column
            //     raise QueryError("Expected column after tree, as in tree.column"); } // why not table?
            let var = lup.peek(2).expect("temp uncommented check").text();
            let tree = lup.tok().text();
            let resolved_tab = get_table_from_var_and_tree(model, var, tree);
            resolvents.push(Resolvent {index: lup.index() as usize, tab_name: resolved_tab});
        }
        // record table prefixes
        if resolved_tab != None || model.is_table(lup.tok().text()) {
            on_clause_tables.push(if resolved_tab != None {resolved_tab.expect("checked")} else {lup.tok().text()}); } // register table in on clause
    }
    if !is_tree {
        return (None, None, resolvents); }
    let tree_join = TreeJoin {tree_tok: join_obj, tree_tok_index: join_obj_index as usize, 
        on_clause_end_index: lup.index() as usize, first_table: None, referenced_tables: bVec::with_capacity_in(3, bump)};
    
    return (Some(tree_join), Some(on_clause_tables), resolvents);
}

fn table_ref_and_resolvent<'a>(bump: &'a Bump, model: &'a DataModel, lup: &AnalyzerLoop) -> (Option<&'a str>, Option<Resolvent<'a>>) {
    // Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    // Each call to _table_from_prefix will update the prefix and 
    // If tree.var is encountered, then the tree is resolved into a variable, if table is unique.
    
    if !lup.tok().is_identifier() {
        return (None, None); }

    if lup.found(&[Token::Period], -1) {
        // get ref_tab, resolvent from a prefix (e.g. tree.tab, tree.col or tab.col)
        let prefix: &str = lup.peek(-2).expect("impossible").text(); // This includes views and cte's as tables. Is that okay?
        if model.is_tree(&prefix) {
            let (var, tree) = (lup.tok().text(), lup.peek(-2).expect("impossible").text());
            let ref_tab = get_table_from_var_and_tree(model, var, tree);
            return (Some(ref_tab), Some(Resolvent {index: lup.index() as usize - 2, tab_name: ref_tab})); }
        else if model.is_table(&prefix) {
            return (Some(prefix), None); }
        else {
            return (None, None); } 
        }
    else if model.is_var(lup.tok().text()) {
        return (table_containing_variable(model, lup.tok().text()).into(), None); }
    else {
        return (None, None); }
}
        
       

fn table_containing_variable<'a>(model: &'a DataModel, var: &'a str) -> &'a str {
    // Get a referenced table from a variable, by asking which table the variable comes from.
    let tabs_of_var = model.tables_by_var(var);
    if tabs_of_var.len() > 1 { "fix me" }
        // raise QueryError(f"There are multiple tables {tabs_of_var} with column {var}."); 
    else if tabs_of_var.len() == 0 { "fix me" }
        // raise QueryError(f"The is no table with column {var}."); }
    else {
        return tabs_of_var[0]; }
}

fn get_table_from_var_and_tree<'a>(model: &'a DataModel, var: &'a str, tree: &'a str) -> &'a str {
    let tabs = model.tables_by_var_and_tree(var, tree);
    if tabs.len() > 1 { return "fix me" }
        // raise QueryError(f"The tree {tree} contains multiple tables {tabs} with column {var}."); }
    else if tabs.len() == 0 { return "fix me" }
        // raise QueryError(f"The tree {tree} does not contain any table with column {var}."); }
    return tabs[0];
}


fn plug_tables_into_tree_joins<'a>(bump: &Bump, model: &'a DataModel, ref_tables: bVec<'a, &'a str>, 
                                   mut tree_joins: bVec<'a, TreeJoin<'a>>, tabs_in_on_clauses: &[bVec<&'a str>]
                                ) -> bVec<'a, TreeJoin<'a>> {
    for tab_name in ref_tables {
        if model.is_table(tab_name) { // this filters for cte's and probably views.
            plug_ref_table_into_tree_join(model, tab_name, &mut tree_joins); }}
    
    let mut prior_tables: bVec<&str> = bVec::with_capacity_in(5, bump);
    for (j, tabs_in_on_clause) in tree_joins.iter_mut().zip(tabs_in_on_clauses.iter()) {
        
        let new_tables = bVec::from_iter_in(
            tabs_in_on_clause.iter().filter(|&t| !prior_tables.contains(t)), bump);
        if new_tables.len() >= 2 {
            // raise QueryError(dedent(f"""
            //     Each tree-on-clause may reference at most one new table. 
            //     The on-clause of {j.tree_tok} references {new_tables}.
            //     """)); 
        }
        // j.first_table can be None in a query like "select 1 from A"
        let alpha_min = j.referenced_tables.iter().min(); // why are we taking the alpha min ???
        j.first_table = if !new_tables.is_empty()   { Some(*new_tables[0]) } 
            else if let Some(&rt) = alpha_min { Some(rt) }
            else                                    { None };

        prior_tables.extend(&j.referenced_tables);
    }
    return tree_joins;
}

fn plug_ref_table_into_tree_join<'a>(model: &'a DataModel, table_name: &'a str, tree_joins: &mut [TreeJoin<'a>]) {
    let trees_of_tab = model.trees_by_table(table_name);
    let already_found = false;
    for j in tree_joins {
        if !trees_of_tab.contains(&tok_text(&j.tree_tok)) {
            continue; }
        if already_found { }
            // raise QueryError(
            //     "You cannot have multiple trees in the same query, while using columns from a table that belongs to both. "
            //     f"table {table_name} belongs to {trees_of_tab}.")
        let already_found = true;
    
        j.referenced_tables.push(table_name);
        if trees_of_tab.len() == 1 {
            break; } // this break is an optimization
    }
}

fn check_for_select_all<'a>(model: &'a DataModel, lup: &AnalyzerLoop) {
    if !matches!(lup.tok(), TokNode::Leaf(Token::Mul)) { return }
    if matches!(lup.peek(-1), Some(TokNode::Leaf(Token::Period))) 
        && !model.is_tree(lup.peek(-2).expect("impossible").text()) 
        {return}
    
    if let Some(next) = lup.peek(1) {
        if matches!(next, TokNode::Leaf(Token::Comma)) || next.is_kw(Keyword::FROM) {} 
            // raise QueryError("The wildcard '*' cannot be used, when selecting from a tree, "
            //                  "unless you restrict the wildcard by an expression on the form 'object.*', "
            //                  "where 'object' is not a tree.")
    }
}

