
"""
SELECT
    conname             AS constraint_name,
    conrelid::regclass  AS table_name,
    a.attname           AS column_name,
    confrelid::regclass AS foreign_table_name,
    af.attname AS foreign_column_name
FROM pg_constraint AS c
JOIN pg_attribute AS a ON a.attnum = ANY (c.conkey) AND a.attrelid = c.conrelid
JOIN pg_attribute AS af ON af.attnum = ANY (c.confkey) AND af.attrelid = c.confrelid
WHERE c.contype = 'f';



SELECT
    rel.relname  AS table_name,
    a.attname    AS column_name,
    frel.relname AS foreign_table_name,
    af.attname   AS foreign_column_name
FROM pg_constraint AS c
JOIN pg_class      AS rel ON rel.oid = c.conrelid
JOIN pg_attribute  AS a ON a.attnum = ANY (c.conkey) AND a.attrelid = c.conrelid
JOIN pg_class      AS frel ON frel.oid = c.confrelid
JOIN pg_attribute  AS af ON af.attnum = ANY (c.confkey) AND af.attrelid = c.confrelid
WHERE c.contype = 'f';
"""


