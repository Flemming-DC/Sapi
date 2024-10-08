--------- header ---------
drop schema if exists sapi_demo cascade;
set client_min_messages to warning;
drop table if exists 
	tab, tab0, tab1, tab2, tab00, tab01, tab10, tab20, tab21, tab_, tab0_, tab1_, sht3__
;
set client_min_messages to notice;
create schema if not exists sapi_demo;
set search_path to sapi_demo;


--------- tree ---------

create table sapi_demo.tab (
    tab_id bigint primary key, -- generated always as identity,
	col_1 text,
	col_2 text
);

create table sapi_demo.tab0 (
    tab0_id bigint primary key, -- generated always as identity,
	tab_id bigint references tab,
	tab1__id bigint,-- references tab1_, fk is declared at bottom of script
	col0_1 text,
	col0_2 text,
	shc text
);


create table sapi_demo.tab1 (
    tab1_id bigint primary key, -- generated always as identity,
	tab_id bigint references tab,
	tab0__id bigint,-- references tab0_, fk is declared at bottom of script
	col1_1 text,
	col1_2 text,
	shc text
);


create table sapi_demo.tab2 (
    tab2_id bigint primary key, -- generated always as identity,
	tab_id bigint references tab,
	col2_1 text,
	col2_2 text
);

create table sapi_demo.tab00 (
    tab00_id bigint primary key, -- generated always as identity,
	tab0_id bigint references tab0,
	col00_1 text,
	col00_2 text
);

create table sapi_demo.tab01 (
    tab01_id bigint primary key, -- generated always as identity,
	tab0_id bigint references tab0,
	col01_1 text,
	col01_2 text
);

create table sapi_demo.tab10 (
    tab10_id bigint primary key, -- generated always as identity,
	tab1_id bigint references tab1,
	col10_1 text,
	col10_2 text
);

create table sapi_demo.tab20 (
    tab20_id bigint primary key, -- generated always as identity,
	tab2_id bigint references tab2,
	col20_1 text,
	col20_2 text
);

create table sapi_demo.tab21 (
    tab21_id bigint primary key, -- generated always as identity,
	tab2_id bigint references tab2,
	col21_1 text,
	col21_2 text
);

--------- tree_ ---------

create table sapi_demo.tab_ (
    tab__id bigint primary key, -- generated always as identity,
	col_1_ text,
	col_2_ text
);

create table sapi_demo.tab0_ (
    tab0__id bigint primary key, -- generated always as identity,
	tab__id bigint references tab_,
	tab1_id bigint references tab1,
	col0_1_ text,
	col0_2_ text,
	shc_ text
);

create table sapi_demo.tab1_ (
    tab1__id bigint primary key, -- generated always as identity,
	tab__id bigint references tab_,
	tab0_id bigint references tab0,
	col1_1_ text,
	col1_2_ text,
	shc_ text
);

--------- OVERLAB ---------

create table sapi_demo.sht__ (
    sht___id bigint primary key, -- generated always as identity,
	tab_id bigint references tab,
	tab__id bigint references tab_, -- tab_id_ deviates from the usual naming
	col_1__ text,
	col_2__ text
);

alter table tab0 add foreign key (tab1__id) references tab1_;
alter table tab1 add foreign key (tab0__id) references tab0_;

