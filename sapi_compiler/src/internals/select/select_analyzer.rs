use bumpalo::Bump;
use bumpalo::collections::Vec as bVec;
// from sapi._internals.error import QueryError, CompilerError
// from sapi._internals.db_contact import data_model
use crate::internals::token_tree::TokenTree; // , Token, TokenType
use super::analyzer_loop::AnalyzerLoop;
use super::tree_join::{TreeJoin, Resolvent};


pub fn find_tree_joins<'a>(bump: &'a Bump, lup: AnalyzerLoop) -> (bVec<'a, TreeJoin<'a>>, bVec<'a, Resolvent<'a>>) {
    (bVec::new_in(&bump), bVec::new_in(&bump))
//     tree_joins: list[TreeJoin] = []
//     tabs_in_on_clauses: list[list[str]] = [] // on_clause_tables_across_joins
//     ref_tables: list[str] = []
//     resolvents: list[Resolvent] = []

//     while lup.next():
//         if isinstance(lup.tok(), TokenTree):
//             continue
//         _check_for_select_all(lup)
//         // analyze from clause
//         tree_join, on_clause_tables_in_join, resolved_tabs_in_join = _make_tree_join(lup, [j.tree_tok for j in tree_joins])
//         resolvents += resolved_tabs_in_join
//         if tree_join:
//             tree_joins.append(tree_join)
//             tabs_in_on_clauses.append(on_clause_tables_in_join)
//             continue
        
//         // find referenced tables and resolve trees outside the from clause
//         ref_tab, resolvent = _table_ref_and_resolvent(lup)
//         if resolvent and resolvent not in resolvents:
//             resolvents.append(resolvent)
//         if ref_tab and ref_tab not in ref_tables:
//             ref_tables.append(ref_tab) 

//     _plug_tables_into_tree_joins(ref_tables, tree_joins, tabs_in_on_clauses)
//     if any(j.referenced_tables == [] for j in tree_joins):
//         raise QueryError("Unused tree in from clause.")
//     return tree_joins, resolvents
}


// fn make_tree_join(lup: AnalyzerLoop, prior_join_objs: list[Token]
//         ) -> tuple[TreeJoin, list[str], list[Resolvent]] | tuple[None, None, list[Resolvent]]:
//     if not lup.found([TokenType.FROM, TokenType.JOIN], 0):
//         return None, None, []
//     lup.next()
//     if not lup.found([TokenType.VAR, TokenType.IDENTIFIER], 0):
//         raise QueryError("expected identifier or variable after from / join.")
    
//     // pass through join_obj prefix
//     while lup.found(TokenType.DOT, 1):
//         lup.next()
//         lup.next()

//     if lup.at_end():
//         raise QueryError("Encountered end of query while parsing prefix (such as schem.tree.table). "
//                          "Expected an object to join with instead.")

//     join_obj = lup.tok() // join_obj at end of join_obj prefixes
//     join_obj_index = lup.index()
//     if join_obj in prior_join_objs:
//         return None, None, [] // don't dublicate join_data (is that actually correct behaviour??)
//     is_tree = data_model.is_tree(join_obj.text)

//     fn on_clause_done(): 
//         return lup.at_end(1) or lup.found([ // join or clause-after-from
//             TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.OUTER, 
//             TokenType.FULL, TokenType.SEMI, TokenType.ANTI, TokenType.LATERAL, TokenType.CROSS, 
//             TokenType.CROSS, TokenType.NATURAL,
//             TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.WINDOW, TokenType.UNION, 
//             TokenType.ORDER_BY, TokenType.LIMIT, TokenType.OFFSET, TokenType.FETCH, TokenType.FOR], after_steps=1)

//     // resolve tree prefixes and record table prefixes in on clause
//     on_clause_tables: list[str] = []
//     resolvents = []
//     while not _on_clause_done():
//         lup.next()
//         resolved_tab = None
//         // resolve tree prefixes
//         if data_model.is_tree(lup.tok().text):
//             if not lup.found([TokenType.VAR, TokenType.IDENTIFIER], 2): // peek(2) should be column
//                 raise QueryError("Expected column after tree, as in tree.column") // why not table?
            
//             var = lup.peek(2).text
//             tree = lup.tok().text
//             resolved_tab = _get_table_from_var_and_tree(var, tree)
//             resolvents.append(Resolvent(index=lup.index(), tab_name=resolved_tab))
//         // record table prefixes
//         if resolved_tab or data_model.is_table(lup.tok().text):
//             on_clause_tables.append(resolved_tab if resolved_tab else lup.tok().text) // register table in on clause
    
//     if not is_tree:
//         return None, None, resolvents
//     tree_join = TreeJoin(tree_tok=join_obj, tree_tok_index=join_obj_index, on_clause_end_index=lup.index())
    
//     return tree_join, on_clause_tables, resolvents
    

// fn table_ref_and_resolvent(lup: AnalyzerLoop) -> tuple[str|None, Resolvent|None]:
//     """
//     Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
//     Each call to _table_from_prefix will update the prefix and 
//     If tree.var is encountered, then the tree is resolved into a variable, if table is unique.
//     """
//     if not lup.found([TokenType.IDENTIFIER, TokenType.VAR], 0):
//         return None, None

//     if lup.found(TokenType.DOT, -1):
//         // get ref_tab, resolvent from a prefix (e.g. tree.tab, tree.col or tab.col)
//         prefix: str = lup.peek(-2).text // This includes views and cte's as tables. Is that okay?
//         if data_model.is_tree(prefix):
//             var, tree = lup.tok().text, lup.peek(-2).text
//             ref_tab = _get_table_from_var_and_tree(var, tree)
//             return ref_tab, Resolvent(index=lup.index() - 2, tab_name=ref_tab)
//         elif data_model.is_table(prefix):
//             return prefix, None
//         else:
//             return None, None
//     elif data_model.is_var(lup.tok().text):
//         return _table_containing_variable(lup.tok().text), None
//     else:
//         return None, None

        
       

// fn table_containing_variable(var: str) -> str|None:
//     "Get a referenced table from a variable, by asking which table the variable comes from."
//     tabs_of_var = data_model.tables_by_var(var)
//     if len(tabs_of_var) > 1:
//         raise QueryError(f"There are multiple tables {tabs_of_var} with column {var}.")
//     elif len(tabs_of_var) == 0:
//         raise QueryError(f"The is no table with column {var}.")
//     else:
//         return tabs_of_var[0]


// fn get_table_from_var_and_tree(var: str, tree: str) -> str:
//     tabs = data_model.tables_by_var_and_tree(var, tree)
//     if len(tabs) > 1:
//         raise QueryError(f"The tree {tree} contains multiple tables {tabs} with column {var}.")
//     elif len(tabs) == 0:
//         raise QueryError(f"The tree {tree} does not contain any table with column {var}.")
//     return tabs[0]



// fn plug_tables_into_tree_joins(ref_tables: list[str], tree_joins: list[TreeJoin], tabs_in_on_clauses: list[str]):
//     for tab_name in ref_tables:
//         if data_model.is_table(tab_name): // this filters for cte's and probably views.
//             _plug_ref_table_into_tree_join(tab_name, tree_joins)
    
//     prior_tables = []
//     for j, tabs_in_on_clause in zip(tree_joins, tabs_in_on_clauses):
        
//         new_tables = [t for t in tabs_in_on_clause if t not in prior_tables]
//         if len(new_tables) >= 2:
//             raise SyntaxError(dedent(f"""
//                 Each tree-on-clause may reference at most one new table. 
//                 The on-clause of {j.tree_tok} references {new_tables}.
//                 """))
//         // j.first_table can be None in a query like "select 1 from A"
//         // min(j.referenced_tables) is the alphabetic minimum
//         j.first_table = new_tables[0] if new_tables else min(j.referenced_tables) if j.referenced_tables else None

//         prior_tables += j.referenced_tables


// fn plug_ref_table_into_tree_join(table_name: str, tree_joins: list[TreeJoin]):
//     trees_of_tab = data_model.trees_by_table(table_name)
//     already_found = False
//     for j in tree_joins:
//         if j.tree_tok.text not in trees_of_tab:
//             continue
//         if already_found:
//             raise QueryError(
//                 "You cannot have multiple trees in the same query, while using columns from a table that belongs to both. "
//                 f"table {table_name} belongs to {trees_of_tab}.")
//         already_found = True
    
//         j.referenced_tables.append(table_name)
//         if len(trees_of_tab) == 1:
//             break // this break is an optimization


// fn check_for_select_all(lup: AnalyzerLoop):
//     if lup.tok().type != TokenType.STAR: return
//     if lup.peek(-1).type == TokenType.DOT and not data_model.is_tree(lup.peek(-2).text): return
    
//     if lup.peek().type in [TokenType.COMMA, TokenType.FROM]:
//         raise QueryError("The wildcard '*' cannot be used, when selecting from a tree, "
//                          "unless you restrict the wildcard by an expression on the form 'object.*', "
//                          "where 'object' is not a tree.")


