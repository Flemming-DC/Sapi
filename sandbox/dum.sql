
select tree_name from sapi_trees -- table_tree_names
;

select -- trees_by_table
    table_name, 
    array_agg(tree_name) as tree_names 
from sapi_trees
join sapi_tables using (sapi_trees_id)	
group by table_name
;

SELECT -- columns_by_table
    table_name as table,
    array_agg(column_name::text) as columns
FROM information_schema.columns
where table_schema = 'sapi_demo'
group by table_name
;

SELECT
    tab.relname             AS table, 
    array_agg(ftab.relname) AS referenced_tables, 
    -- array_agg(col.attname)    AS primary_key,
    -- array_agg(fcol.attname)   AS foreign_key,
    null
FROM pg_constraint AS con
JOIN pg_class      AS tab  ON tab.oid = con.conrelid
JOIN pg_attribute  AS col  ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
JOIN pg_class      AS ftab ON ftab.oid = con.confrelid
JOIN pg_attribute  AS fcol ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
WHERE con.contype = 'f'
group by tab.relname
;


SELECT 
    tab.relname as table_name,
    col.attname as column_name
FROM pg_class      AS tab ON tab.relname = sapi_tables.table_name
JOIN pg_attribute  AS col ON col.attrelid = tab.oid
WHERE col.attnum > 0 -- exclude system columns
    and not col.attisdropped 
;


WITH columns as (
    SELECT -- copy of the columns query below
        schema.nspname as schema_name,
        tab.relname as table_name,
        col.attname as column_name
    FROM pg_namespace  AS schema
    JOIN pg_class      AS tab ON tab.relnamespace = schema.oid
    JOIN pg_attribute  AS col ON col.attrelid = tab.oid    
    WHERE col.attnum > 0 -- exclude system columns
        and not col.attisdropped   
        and schema.nspname not in ('pg_catalog', 'pg_toast', 'information_schema')
)
SELECT 
    tree.schema_name,
    tree.tree_name,
    sapi_tables.table_name,
    col.column_name -- if column_name is null, then there is no table_name, schema_name match in the tree, which is an error
FROM sapi_sys.sapi_trees AS tree 
JOIN sapi_sys.sapi_tables ON sapi_tables.sapi_trees_id = tree.sapi_trees_id
LEFT JOIN columns AS col ON col.table_name = sapi_tables.table_name and col.schema_name = tree.schema_name
ORDER BY tree.schema_name, tree.tree_name, sapi_tables.table_name, col.column_name -- evt. drop order by
;

-- per dialect
-- columns
SELECT 
    schema.nspname as schema_name,
    tab.relname as table_name,
    col.attname as column_name
FROM pg_namespace  AS schema
JOIN pg_class      AS tab ON tab.relnamespace = schema.oid
JOIN pg_attribute  AS col ON col.attrelid = tab.oid    
WHERE col.attnum > 0 -- exclude system columns
    and not col.attisdropped   
    and schema.nspname not in ('pg_catalog', 'pg_toast', 'information_schema')

-- per dialect
-- foreign keys
SELECT
    schema.nspname          as schema,
    fschema.nspname         as referenced_schema,
    tab.relname             AS table,
    ftab.relname            AS referenced_table,
    array_agg(col.attname)  AS primary_key_columns,
    array_agg(fcol.attname) AS foreign_key_columns
FROM pg_constraint AS con
JOIN pg_class      AS tab     ON tab.oid = con.conrelid
JOIN pg_namespace  AS schema  ON schema.oid = tab.relnamespace
JOIN pg_attribute  AS col     ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
JOIN pg_class      AS ftab    ON ftab.oid = con.confrelid
JOIN pg_namespace  AS fschema ON fschema.oid = ftab.relnamespace
JOIN pg_attribute  AS fcol    ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
WHERE con.contype = 'f'
    and col.attnum > 0 -- exclude system columns
    and fcol.attnum > 0 -- exclude system columns
    and not col.attisdropped 
    and not fcol.attisdropped 
group by schema.nspname, fschema.nspname, tab.oid, ftab.oid
-- evt add order by
;

-- evt. no agg 
SELECT
    schema.nspname  as schema,
    fschema.nspname as referenced_schema,
    tab.relname     AS table,
    ftab.relname    AS referenced_table,
    col.attname     AS primary_key_col, -- note that a pk can contain multiple columns
    fcol.attname    AS foreign_key_col -- note that a fk can contain multiple columns
FROM pg_constraint AS con
JOIN pg_class      AS tab     ON tab.oid = con.conrelid
JOIN pg_namespace  AS schema  ON schema.oid = tab.relnamespace
JOIN pg_attribute  AS col     ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
JOIN pg_class      AS ftab    ON ftab.oid = con.confrelid
JOIN pg_namespace  AS fschema ON fschema.oid = ftab.relnamespace
JOIN pg_attribute  AS fcol    ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
WHERE con.contype = 'f'
    and col.attnum > 0 -- exclude system columns
    and fcol.attnum > 0 -- exclude system columns
    and not col.attisdropped 
    and not fcol.attisdropped 
;


WITH foreign_keys as (
    SELECT
        schema.nspname  as schema,
        fschema.nspname as referenced_schema,
        tab.relname     AS table,
        ftab.relname    AS referenced_table,
        col.attname     AS primary_key_col, -- note that a pk can contain multiple columns
        fcol.attname    AS foreign_key_col -- note that a fk can contain multiple columns
    FROM pg_constraint AS con
    JOIN pg_class      AS tab     ON tab.oid = con.conrelid
    JOIN pg_namespace  AS schema  ON schema.oid = tab.relnamespace
    JOIN pg_attribute  AS col     ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
    JOIN pg_class      AS ftab    ON ftab.oid = con.confrelid
    JOIN pg_namespace  AS fschema ON fschema.oid = ftab.relnamespace
    JOIN pg_attribute  AS fcol    ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
    WHERE con.contype = 'f'
        and col.attnum > 0 -- exclude system columns
        and fcol.attnum > 0 -- exclude system columns
        and not col.attisdropped 
        and not fcol.attisdropped 
    )
SELECT 
    tree.schema_name,
    tree.tree_name,
    sapi_tables.table_name,
    col.column_name -- if column_name is null, then there is no table_name, schema_name match in the tree, which is an error
FROM sapi_sys.sapi_trees AS tree 
JOIN sapi_sys.sapi_tables ON sapi_tables.sapi_trees_id = tree.sapi_trees_id
LEFT JOIN columns AS col ON col.table_name = sapi_tables.table_name and col.schema_name = tree.schema_name
ORDER BY tree.schema_name, tree.tree_name, sapi_tables.table_name, col.column_name -- evt. drop order by
;





-- join_info
WITH foreign_keys as (
    SELECT
        schema.nspname  as schema,
        fschema.nspname as referenced_schema,
        tab.relname     AS table,
        ftab.relname    AS referenced_table,
        col.attname     AS primary_key_col, -- note that a pk can contain multiple columns
        fcol.attname    AS foreign_key_col -- note that a fk can contain multiple columns
    FROM pg_constraint AS con
    JOIN pg_class      AS tab     ON tab.oid = con.conrelid
    JOIN pg_namespace  AS schema  ON schema.oid = tab.relnamespace
    JOIN pg_attribute  AS col     ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
    JOIN pg_class      AS ftab    ON ftab.oid = con.confrelid
    JOIN pg_namespace  AS fschema ON fschema.oid = ftab.relnamespace
    JOIN pg_attribute  AS fcol    ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
    WHERE con.contype = 'f'
        and col.attnum > 0 -- exclude system columns
        and fcol.attnum > 0 -- exclude system columns
        and not col.attisdropped 
        and not fcol.attisdropped 
)
select 
    tab.table_name as tab_name,
    ref_tab.table_name as parent,
    fk.primary_key_col,
    fk.foreign_key_col 
from sapi_sys.sapi_tables as tab
join sapi_sys.sapi_tables as ref_tab using (sapi_trees_id)
join sapi_sys.sapi_trees as trees using (sapi_trees_id)
join foreign_keys as fk
    on trees.schema_name = fk.schema
    and trees.schema_name = fk.referenced_schema
    and tab.table_name = fk.table
    and ref_tab.table_name = fk.referenced_table


    -- tab.relname   AS table, 
    -- ftab.relname  AS referenced_table, 
    -- col.attname   AS primary_key,
    -- fcol.attname  AS foreign_key,


--------------
-- table_tree_names, trees_by_table, _table_data
-- table_tree_names, trees_by_table, tables_by_var, tables_by_var_and_tree, node_by_table, all_tables


-- per table: pk, fk, overwriting join_rule (join-type, evt. acronym and on clause)

------
-- [per tree], [per table], [per column] 
-- tree_name,  table_name,  column_name, refers_to, 

-- tree, table, column

-- column: follow_reference(), 
-- table: parent
-- 

-- inner join by setting every fk equal to the corresponding pk


