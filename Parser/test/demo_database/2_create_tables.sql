--------- header ---------
-- drop schema if exists sapi_demo cascade;
set search_path to sapi_demo;
drop table if exists 
	tab, tab0, tab1, tab2, tab00, tab01, tab10, tab20, tab21, 
	tab_, tab0_, tab1_, sht__, 
	tab_manual, tab0_manual,
	dual_pk, dual_fk, historic1, historic2
;
-- create schema if not exists sapi_demo;


--------- tree ---------

create table tab (
    tab_id bigint primary key generated always as identity,
	col_1 text,
	col_2 text
);

create table tab0 (
    tab0_id bigint primary key generated always as identity,
	tab_id bigint references tab,
	tab1__id bigint,-- references tab1_, fk is declared at bottom of script
	col0_1 text,
	col0_2 text,
	shc text
);


create table tab1 (
    tab1_id bigint primary key generated always as identity,
	tab_id bigint references tab,
	tab0__id bigint,-- references tab0_, fk is declared at bottom of script
	col1_1 text,
	col1_2 text,
	shc text
);


create table tab2 (
    tab2_id bigint primary key generated always as identity,
	tab_id bigint references tab,
	col2_1 text,
	col2_2 text
);

create table tab00 (
    tab00_id bigint primary key generated always as identity,
	tab0_id bigint references tab0,
	col00_1 text,
	col00_2 text
);

create table tab01 (
    tab01_id bigint primary key generated always as identity,
	tab0_id bigint references tab0,
	col01_1 text,
	col01_2 text
);

create table tab10 (
    tab10_id bigint primary key generated always as identity,
	tab1_id bigint references tab1,
	col10_1 text,
	col10_2 text
);

create table tab20 (
    tab20_id bigint primary key generated always as identity,
	tab2_id bigint references tab2,
	col20_1 text,
	col20_2 text
);

create table tab21 (
    tab21_id bigint primary key generated always as identity,
	tab2_id bigint references tab2,
	col21_1 text,
	col21_2 text
);

--------- tree_ ---------

create table tab_ (
    tab__id bigint primary key generated always as identity,
	col_1_ text,
	col_2_ text
);

create table tab0_ (
    tab0__id bigint primary key generated always as identity,
	tab__id bigint references tab_,
	tab1_id bigint references tab1,
	col0_1_ text,
	col0_2_ text,
	shc_ text
);

create table tab1_ (
    tab1__id bigint primary key generated always as identity,
	tab__id bigint references tab_,
	tab0_id bigint references tab0,
	col1_1_ text,
	col1_2_ text,
	shc_ text
);

--------- OVERLAB ---------

create table sht__ (
    sht___id bigint primary key generated always as identity,
	tab_id bigint references tab,
	tab__id bigint references tab_, -- tab_id_ deviates from the usual naming
	col_1__ text,
	col_2__ text
);

alter table tab0 add foreign key (tab1__id) references tab1_;
alter table tab1 add foreign key (tab0__id) references tab0_;


--------- MANUAL PRIMARY KEY ---------

create table tab_manual (
    tab_manual_id bigint primary key,
	col_manual_1 text,
	col_manual_2 text
);

create table tab0_manual (
    tab0_manual_id bigint primary key,
	tab_manual_id bigint references tab_manual,
	col0_manual_1 text,
	col0_manual_2 text
);

--------- JOIN RULES ---------

create table dual_pk (
    dual_pk_id1 bigint,
    dual_pk_id2 bigint,
    dual_pk_col text,
    primary key (dual_pk_id1, dual_pk_id2)
);

create table dual_fk (
    dual_fk_id1 bigint primary key generated always as identity,
    dual_pk_id1 bigint not null,
    dual_pk_id2 bigint not null,
    dual_fk_col text,
    FOREIGN KEY (dual_pk_id1, dual_pk_id2) REFERENCES dual_pk (dual_pk_id1, dual_pk_id2)
);

create table historic1 (
    historic1_id bigint primary key generated always as identity,
	persistent1_id bigint,
	from_date1 date,
	to_date1 date,
    historic_col1 text,
	unique (persistent1_id, from_date1, to_date1)
);

create table historic2 (
    historic2_id bigint primary key generated always as identity,
	historic1_id bigint not null references historic1,
	persistent2_id bigint,
	from_date2 date,
	to_date2 date,
    historic_col2 text,
	unique (persistent2_id, from_date2, to_date2)
);

