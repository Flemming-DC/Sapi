#![allow(dead_code, unused_imports, unused_variables, unused_parens)]
// use bumpalo::Bump;
use sapi_compiler::*;

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        let result = sapi_add(2, 2);
        assert_eq!(result, 4);
    }
}




fn main() {
    let join_clause = Some("JOIN __parent__ USING (__keys__)");
    let tree = Tree { name: "tree", schema: "sapi_demo", tables: vec![
        Table {name: "tab",   primary_key: "tab_id",   parent: None,         join_clause: join_clause, columns: vec!["col_1", "col_2", "tab_id"]}, 
        Table {name: "tab0",  primary_key: "tab0_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col0_1", "col0_2", "shc", "tab0_id", "tab1__id", "tab_id"]}, 
        Table {name: "tab00", primary_key: "tab00_id", parent: Some("tab0"), join_clause: join_clause, columns: vec!["col00_1", "col00_2", "tab00_id", "tab0_id"]}, 
        Table {name: "tab01", primary_key: "tab01_id", parent: Some("tab0"), join_clause: join_clause, columns: vec!["col01_1", "col01_2", "tab01_id", "tab0_id"]}, 
        Table {name: "tab1",  primary_key: "tab1_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col1_1", "col1_2", "shc", "tab0__id", "tab1_id", "tab_id"]}, 
        Table {name: "tab10", primary_key: "tab10_id", parent: Some("tab1"), join_clause: join_clause, columns: vec!["col10_1", "col10_2", "tab10_id", "tab1_id"]}, 
        Table {name: "tab2",  primary_key: "tab2_id",  parent: Some("tab"),  join_clause: join_clause, columns: vec!["col2_1", "col2_2", "tab2_id", "tab_id"]}, 
        Table {name: "tab20", primary_key: "tab20_id", parent: Some("tab2"), join_clause: join_clause, columns: vec!["col20_1", "col20_2", "tab20_id", "tab2_id"]}, 
        Table {name: "tab21", primary_key: "tab21_id", parent: Some("tab2"), join_clause: join_clause, columns: vec!["col21_1", "col21_2", "tab21_id", "tab2_id"]}, 
        Table {name: "sht__", primary_key: "sht___id", parent: Some("tab"),  join_clause: join_clause, columns: vec!["col_1__", "col_2__", "sht___id", "tab__id", "tab_id"]}, 
    ]};
    let model_id = DataModel::new("postgres", vec![tree]);

    let sapi_query = r"
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tree
        )
        SELECT 
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tree)
        -- here we have a select query. sapi parsed to sql
        FROM cte 
        join tree ON tree.col_1 = cte.col0_1
        ";
    let sql = compiler::compile(sapi_query.into(), model_id);
    // dbg!(&sql);
    
    let expected_sql = r"
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tab0
            JOIN tab00 USING (tab0_id))
        SELECT
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tab20)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte
        join tab ON tab.col_1 = cte.col0_1
        JOIN tab1 USING (tab_id)
        JOIN tab10 USING (tab1_id)
    ";
    // println!("----- expected -----");
    // println!("{:#}", &expected_sql);

    // println!("----- actual -----");
    // println!("{:#}", &sql);
    // println!();

    // assert!(&sql == expected_sql);

}
