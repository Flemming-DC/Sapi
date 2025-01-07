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
    // sqlparser::tokenizer
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
    parser::parse(sapi_query.into(), &parser::DataModel);
}
