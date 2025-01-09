// from dataclasses import dataclass
// from anytree import Node
// from . import deployment
// from .dialect import Dialect
// from .pep249_database_api_spec_v2 import Cursor
// from sapi._internals.error import CompilerError, DataModelError
use bumpalo::collections::Vec as bVec;
use bumpalo::collections::String as bString;
use bumpalo::Bump;
use super::deployment;
use super::deployment::{Dialect, Cursor};
use std::cell::Cell;
use std::{any::Any, collections::HashMap};

#[derive(Debug, PartialEq, Clone, Copy)]
pub struct Node<'m> {name: &'m str, parent: Option<&'m Node<'m>>} // stub
// impl<'m> Node<'m> { fn new(name: &str, parent: &) -> Self {Node {parent: None}} } // str is temp // stub
impl Cursor { fn execute(&self, query: &str) -> &[&[&str]] {&[]} } // str is temp // stub


pub struct Table<'m> {
    name: &'m str,
    parent: Option<&'m str>,
    columns: bVec<'m, &'m str>,
    primary_key: &'m str,
    join_clause: Option<&'m str>, // None iff Parent is None
    // foreign_keys: str // a comma seperated list of foreign_keys
}
pub struct Tree<'m> { // evt. call it TableTree 
    tables: bVec<'m, Table<'m>>,
    name: &'m str,
    schema: &'m str,
    // insertable: bool = True
    // deletable: bool = True
}



pub struct DataModel<'m> {
    // _current: Option<DataModel>,
    _table_tree_names: bVec<'m, &'m str>,
    _trees_by_table: HashMap<&'m str, bVec<'m, &'m str>>, // HashMap uses global alloc
    _primary_key_by_tab: HashMap<&'m str, &'m str>,
    _tables_by_var: HashMap<&'m str, bVec<'m, &'m str>>,
    _tabs_by_var_and_tree: HashMap<(&'m str, &'m str), bVec<'m, &'m str>>,
    // _node_by_tab_and_tree: HashMap<(&'m str, &'m str), Node<'m>>,
    _join_clause_by_tab: HashMap<(&'m str, bool), Option<String>>,
    _all_tables: bVec<'m, &'m str>,
    _dialect: &'m Dialect // used due to get sqlglot_dialect and black_from_clause
}

impl<'m> DataModel<'m> {

    pub fn new(bump: &'m Bump, dialect: &'m Dialect, trees: &'m [Tree]) -> Self {
        // defaults
        let mut dm = DataModel {
            // _current: None,
            _table_tree_names: bVec::with_capacity_in(trees.len(), bump),
            _trees_by_table: HashMap::with_capacity(trees.len() * 6), // 6 = guess-tab-per-tree
            _primary_key_by_tab: HashMap::with_capacity(trees.len() * 6),
            _tables_by_var: HashMap::with_capacity(trees.len() * 6 * 4), // 4 = guess-col-per-tab
            _tabs_by_var_and_tree: HashMap::with_capacity(trees.len() * 6 * 4),
            // _node_by_tab_and_tree: HashMap::with_capacity(trees.len() * 6),
            _join_clause_by_tab: HashMap::with_capacity(trees.len() * 6),
            _all_tables: bVec::with_capacity_in(trees.len() * 6, bump),
            _dialect: dialect, // used due to get sqlglot_dialect and black_from_clause
        };
    

        for tree in trees {
            if dm._table_tree_names.contains(&tree.name) {
                // raise DataModelError(r"You cannot have two trees with the same name in the same instance "
                //                      r"of the DataModel class. name = {}", tree.name)
                }
            dm._table_tree_names.push(tree.name);
            for tab in &tree.tables {
                if !dm._all_tables.contains(&tab.name) {
                    dm._all_tables.push(tab.name);}
                
                let trs = dm._trees_by_table.entry(tab.name).or_insert(bVec::new_in(bump));
                if !trs.contains(&tree.name) {trs.push(tree.name);}

                dm._primary_key_by_tab.entry(tab.name).or_insert(tab.primary_key);

                if true { // dm._join_clause_by_tab.keys().contains(tab.name) // ??? why this check ? 
                    dm._join_clause_by_tab.insert((tab.name, true), tab.join_clause.map(|jc|jc.into())); // from child join parent
                    if let Some(parent) = tab.parent { match tab.join_clause {
                        None => { // raise CompilerError(
                        //     "Table should not have parent without having a rule for how to on join the parent")
                        }
                        Some(jc) => {
                            // let reverse_join: bString<'m> = bString::from_str_in(&jc.replacen(parent, tab.name, 1), bump); 
                            let reverse_join = jc.replacen(parent, tab.name, 1);
                            dm._join_clause_by_tab.insert((tab.name, false), Some(reverse_join)); // from parent join child
                        }
                    }};
                };

                // dm._node_by_tab_and_tree.insert((tab.name, tree.name), Node {name: tab.name, parent: None}); // parent is set later

                for col in &tab.columns {
                    let ts = dm._tables_by_var.entry(col).or_insert(bVec::new_in(bump));
                    if !ts.contains(&tab.name) {ts.push(tab.name);}

                    let ts = dm._tabs_by_var_and_tree.entry((col, tree.name)).or_insert(bVec::new_in(bump));
                    if !ts.contains(&tab.name) {ts.push(tab.name);}
                }
            }
        }
        // for tree in trees {
        //     for tab in &tree.tables {
        //         let node = dm._node_by_tab_and_tree.get(&(tab.name, tree.name));
        //         if let Some(parent) = tab.parent {
        //             let parent_node = dm._node_by_tab_and_tree.get(&(parent, tree.name)).clone();
        //             if node != None && parent_node != None {
        //                 let n = Node {name: node.expect("checked").name, parent: parent_node};
        //                 dm._node_by_tab_and_tree.insert((tab.name, tree.name), n);
        //             }
        //         }
        //     }
        // }
        return dm;
    }
    
    pub fn from_database(bumb: &'m Bump, dialect: &'m Dialect, cur: &Cursor, sys_schema: &str) -> Self {
        cur.execute("savepoint DataModel_from_database");
        if !deployment::is_deployed(cur, dialect, sys_schema) {
            // raise DataModelError("You must call deployment.setup, before calling this function.")
        }
        cur.execute(r"set search_path to {sys_schema}");
        let trees = Self::make_trees(dialect, cur, sys_schema);
        cur.execute("rollback to savepoint DataModel_from_database");
        
        return DataModel::new(bumb, dialect, trees);
    }

    fn make_trees(dialect: &Dialect, cur: &Cursor, sys_schema: &str) -> &'m [Tree<'m>] {
    &[]
//     cur.execute(r"""
//         WITH columns as ({dialect.columns_query})
//         SELECT 
//             tree.schema_name,
//             tree.tree_name,
//             sapi_tables.table_name,
//             col.column_name,
//             sapi_tables.sapi_tables_id
//         FROM {sys_schema}.sapi_trees AS tree 
//         JOIN {sys_schema}.sapi_tables ON sapi_tables.sapi_trees_id = tree.sapi_trees_id
//         LEFT JOIN columns AS col ON col.table_name = sapi_tables.table_name and col.schema_name = tree.schema_name
//         ORDER BY tree.schema_name, tree.tree_name, sapi_tables.table_name, col.column_name
//         """)
//     columns_data = cur.fetchall()
    
//     cur.execute(r"""
//         WITH foreign_keys as ({dialect.foreign_keys_query})
//         select 
//             tab.sapi_tables_id,
//             ref_tab.table_name as parent,
//             fk.primary_key_col,
//             fk.foreign_key_col,
//             tab.join_clause 
//         from {sys_schema}.sapi_tables as tab
//         join {sys_schema}.sapi_tables as ref_tab using (sapi_trees_id)
//         join {sys_schema}.sapi_trees as trees using (sapi_trees_id)
//         join foreign_keys as fk
//             on  trees.schema_name = fk.schema
//             and trees.schema_name = fk.referenced_schema
//             and tab.table_name = fk.table
//             and ref_tab.table_name = fk.referenced_table
//         """)
//     join_info = cur.fetchall()
//     join_info_by_table_id = {
//         j[0]: {'parent': j[1], 'primary_key_col': j[2], 'foreign_key_col': j[3], 'join_clause': j[4]} 
//         for j in join_info}
//     }

//     cur.execute(r"""
//         WITH primary_keys as ({dialect.primary_keys_query})
//         select 
//             tab.table_name,
//             pk.primary_key_col
//         from {sys_schema}.sapi_tables as tab
//         join {sys_schema}.sapi_trees as trees using (sapi_trees_id)
//         join primary_keys as pk
//             on  trees.schema_name = pk.schema
//             and tab.table_name = pk.table
//         """);
//     primary_keys = cur.fetchall();
//     primary_key_by_tab_ = {pk[0]: pk[1] for pk in primary_keys};

//     cur.execute(r"""
//         select distinct schema_name, table_name
//         from {sys_schema}.sapi_tables
//         join {sys_schema}.sapi_trees using (sapi_trees_id)
//         """); 
//     remaining_expected_tables = [schema + '.' + tab for schema, tab in cur.fetchall()]; // used for error checking 

//     let trees: list[Tree] = [];
//     let current_tree: Tree|None = None;
//     let current_table: Table|None = None;
//     for col_row in columns_data {
//         col_row = {
//             'schema_name': col_row[0],
//             'tree_name': col_row[1],
//             'table_name': col_row[2],
//             'column_name': col_row[3],
//             'sapi_tables_id': col_row[4];}
//         if !current_tree || col_row['tree_name'] != current_tree.name {
//             current_tree = Tree(tables=[], name=col_row['tree_name'], schema=col_row['schema_name']);
//             trees.push(current_tree);}

//         // now current_tree must exist
//         if !current_table || col_row['table_name'] != current_table.name {
//             current_table = Table(
//                 name=col_row['table_name'], primary_key=primary_key_by_tab_[col_row['table_name']], 
//                 parent=None, columns=[], join_clause=None);
//             if current_table.name in [t.name for t in current_tree.tables] {
//                 // raise DataModelError("Table name should be unique inside tree.")
//             };
//             current_tree.tables.push(current_table);
//             // set parent and any necessary join info
//             join_info = join_info_by_table_id.get(col_row['sapi_tables_id'], None);
//             if join_info { // join_info is None for the root table
//                 current_table.parent = join_info['parent'];
//                 current_table.join_clause = str(join_info['join_clause']
//                     ).replace('__parent__', join_info['parent']
//                     ).replace('__keys__', join_info['foreign_key_col']);
//             }

//             qualified_table = current_tree.schema + '.' + current_table.name;
//             if remaining_expected_tables.contains(qualified_table) {
//                 remaining_expected_tables.remove(qualified_table); }
//         }
//         // now current_table must exist
//         if col_row['column_name'] != None {
//             full_name = r"{col_row['schema_name']}.{col_row['tree_name']}.{col_row['table_name']}";
//             // raise DataModelError(r"Failed to find any table '{full_name}' containing any columns.")
//         }
//         // now col_row['column_name'] must exist
//         current_table.columns.push(col_row['column_name']);
//     }
//     if remaining_expected_tables {
//         // raise DataModelError(r"Failed to find the following table even though they are listed in "
//         //                     r"{sys_schema}.sapi_tables.\n{remaining_expected_tables}")
//     }

//     return trees;
    }
}


// pub fn set_current(dataModel: DataModel) { DataModel._current = dataModel; } 





pub fn is_var(tok_text: &str)                                   -> bool { false }
pub fn is_tree(tok_text: &str)                                  -> bool { false }
pub fn is_table(tok_text: &str)                                 -> bool { false }
pub fn tables_by_var(var: &str)                                 -> &[&str] { &[] }
pub fn trees_by_table(table_name: &str)                         -> &[&str] { &[] }
pub fn tables_by_var_and_tree<'a>(var: &'a str, tree: &'a str)  -> &'a [&'a str] { &[] }
pub fn primary_key_by_tab(table_name: &str)                     -> &str { "" }
pub fn join_clause_by_tab(table_name: &str, going_up: bool)     -> &str { "" }
pub fn dialect()                                                -> Dialect { Dialect{} }
// pub fn node_by_tab_and_tree<'a>(tab: &str, tree: &str)          -> Node<'a> { Node{parent: None} }




