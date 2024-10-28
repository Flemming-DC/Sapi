--------- header ---------

-- drop schema if exists sapi_sys cascade;
drop table if exists sapi_tables;
drop table if exists sapi_trees;
-- create schema if not exists sapi_sys;

--------- sys tables ---------

create table sapi_sys.sapi_trees (
    sapi_trees_id bigint primary key generated always as identity,
	tree_name text not null, -- check valid name
	schema_name text not null, -- check valid name
	-- evt. catalog name not null,
	-- insertable bool not null default true,
	-- deletable bool not null default true,

	unique (tree_name, schema_name) -- evt. add catalog name
);

create table sapi_sys.sapi_tables (
    sapi_tables_id bigint primary key generated always as identity,
	sapi_trees_id bigint not null references sapi_trees,
	table_name text not null, -- check valid name and check that table exists
	table_acronym text check (table_acronym is null or length(table_acronym) < length(table_name)),
	-- unchecked_references (evt. separate into another table)

	unique (table_name, sapi_trees_id),
	unique (table_acronym, sapi_trees_id)
);



