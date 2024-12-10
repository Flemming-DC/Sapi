

truncate sapi_sys.sapi_trees, sapi_sys.sapi_tables;

insert into sapi_sys.sapi_trees (tree_name, schema_name) values ('tree', 'sapi_demo');
insert into sapi_sys.sapi_trees (tree_name, schema_name) values ('tree_', 'sapi_demo');
insert into sapi_sys.sapi_trees (tree_name, schema_name) values ('tree_manual', 'sapi_demo');
insert into sapi_sys.sapi_trees (tree_name, schema_name) values ('dual_key', 'sapi_demo');
insert into sapi_sys.sapi_trees (tree_name, schema_name) values ('historic', 'sapi_demo');



with tree as (select sapi_trees_id from sapi_sys.sapi_trees 
    where tree_name = 'tree' and schema_name = 'sapi_demo')
insert into sapi_sys.sapi_tables (sapi_trees_id, table_name)
select sapi_trees_id, 'tab'   from tree union
select sapi_trees_id, 'tab0'  from tree union
select sapi_trees_id, 'tab1'  from tree union
select sapi_trees_id, 'tab2'  from tree union
select sapi_trees_id, 'tab00' from tree union
select sapi_trees_id, 'tab01' from tree union
select sapi_trees_id, 'tab10' from tree union
select sapi_trees_id, 'tab20' from tree union
select sapi_trees_id, 'tab21' from tree union
select sapi_trees_id, 'sht__' from tree 
;

with tree as (select sapi_trees_id from sapi_sys.sapi_trees 
    where tree_name = 'tree_' and schema_name = 'sapi_demo')
insert into sapi_sys.sapi_tables (sapi_trees_id, table_name)
select sapi_trees_id, 'tab_'  from tree union
select sapi_trees_id, 'tab0_' from tree union
select sapi_trees_id, 'tab1_' from tree union
select sapi_trees_id, 'sht__'from tree
;

with tree as (select sapi_trees_id from sapi_sys.sapi_trees 
    where tree_name = 'tree_manual' and schema_name = 'sapi_demo')
insert into sapi_sys.sapi_tables (sapi_trees_id, table_name)
select sapi_trees_id, 'tab_manual' from tree union
select sapi_trees_id, 'tab0_manual'from tree
;

with tree as (select sapi_trees_id from sapi_sys.sapi_trees 
    where tree_name = 'dual_key' and schema_name = 'sapi_demo')
insert into sapi_sys.sapi_tables (sapi_trees_id, table_name)
select sapi_trees_id, 'dual_pk' from tree union
select sapi_trees_id, 'dual_fk' from tree
;

with tree as (select sapi_trees_id from sapi_sys.sapi_trees 
    where tree_name = 'historic' and schema_name = 'sapi_demo')
insert into sapi_sys.sapi_tables (sapi_trees_id, table_name, join_clause)
select sapi_trees_id, 'historic1', 'JOIN __parent__ USING (__keys__)' from tree union
select sapi_trees_id, 'historic2', 
    'JOIN __parent__ ON persistent2_id = persistent1_id and from_date2 < to_date2 and from_date1 < to_date1' from tree
;
