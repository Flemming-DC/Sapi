

set search_path to sapi_sys;
truncate sapi_trees, sapi_tables;

insert into sapi_trees (tree_name, schema_name) values ('tree', 'sapi_demo');
insert into sapi_trees (tree_name, schema_name) values ('tree_', 'sapi_demo');


with tree as (
    select sapi_trees_id 
    from sapi_trees 
    where tree_name = 'tree' and schema_name = 'sapi_demo'
)
insert into sapi_tables (sapi_trees_id, table_name)
select sapi_trees_id, 'tab'   from tree union
select sapi_trees_id, 'tab0'  from tree union
select sapi_trees_id, 'tab1'  from tree union
select sapi_trees_id, 'tab2'  from tree union
select sapi_trees_id, 'tab00' from tree union
select sapi_trees_id, 'tab01' from tree union
select sapi_trees_id, 'tab10' from tree union
select sapi_trees_id, 'tab20' from tree union
select sapi_trees_id, 'tab21' from tree union
select sapi_trees_id, 'sht__'from tree
;

with tree as (
    select sapi_trees_id 
    from sapi_trees 
    where tree_name = 'tree_' and schema_name = 'sapi_demo'
)
insert into sapi_tables (sapi_trees_id, table_name)
select sapi_trees_id, 'tab_'  from tree union
select sapi_trees_id, 'tab0_' from tree union
select sapi_trees_id, 'tab1_' from tree union
select sapi_trees_id, 'sht__'from tree
;




