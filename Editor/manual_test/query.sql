
WITH cte AS (
    SELECT col0_1, col00_2 FROM tree
)
SELECT /* hegr */
    'vervre',
    $$ multi
    line $$,
    123,
    cte.col00_2,
    col10_2,
    (SELECT count(col20_2) FROM tree)
--FROM tree
--join cte ON tree.col_1 = cte.col0_1 
FROM cte 
join tree ON tree.col_1 = cte.col0_1
;


