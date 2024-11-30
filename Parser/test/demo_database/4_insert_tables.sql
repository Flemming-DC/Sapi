

set search_path to sapi_demo;

truncate tab, tab0, tab1, tab2, tab00, tab01, tab10, tab20, tab21, tab_, tab0_, tab1_, sht__;

insert into tab   (col_1,   col_2)                    values (   'col_1',   'col_2');
insert into tab0  (tab_id,  col0_1, col0_2, shc)      values (1, 'col0_1',  'col0_2', 'shc');
insert into tab1  (tab_id,  col1_1, col1_2, shc)      values (1, 'col1_1',  'col1_2', 'shc');
insert into tab2  (tab_id,  col2_1, col2_2)           values (1, 'col2_1',  'col2_2');
insert into tab00 (tab0_id, col00_1, col00_2)         values (1, 'col00_1', 'col00_2');
insert into tab01 (tab0_id, col01_1, col01_2)         values (1, 'col01_1', 'col01_2');
insert into tab10 (tab1_id, col10_1, col10_2)         values (1, 'col10_1', 'col10_2');
insert into tab20 (tab2_id, col20_1, col20_2)         values (1, 'col20_1', 'col20_2');
insert into tab21 (tab2_id, col21_1, col21_2)         values (1, 'col21_1', 'col21_2');
insert into tab_  (col_1_,  col_2_)                   values (   'col_1_',  'col_2_');
insert into tab0_ (tab__id, col0_1_, col0_2_, shc_)   values (1, 'col0_1_', 'col0_2_', 'shc_');
insert into tab1_ (tab__id, col1_1_, col1_2_, shc_)   values (1, 'col1_1_', 'col1_2_', 'shc_');
insert into sht__ (tab_id,  tab__id, col_1__, col_2__)values (1, 1, 'col_1__', 'col_2__');
/*
insert into tab   (tab_id,   col_1,   col_2)                    values (1,    'col_1',   'col_2');
insert into tab0  (tab0_id,  tab_id,  col0_1, col0_2, shc)      values (1, 1, 'col0_1',  'col0_2', 'shc');
insert into tab1  (tab1_id,  tab_id,  col1_1, col1_2, shc)      values (1, 1, 'col1_1',  'col1_2', 'shc');
insert into tab2  (tab2_id,  tab_id,  col2_1, col2_2)           values (1, 1, 'col2_1',  'col2_2');
insert into tab00 (tab00_id, tab0_id, col00_1, col00_2)         values (1, 1, 'col00_1', 'col00_2');
insert into tab01 (tab01_id, tab0_id, col01_1, col01_2)         values (1, 1, 'col01_1', 'col01_2');
insert into tab10 (tab10_id, tab1_id, col10_1, col10_2)         values (1, 1, 'col10_1', 'col10_2');
insert into tab20 (tab20_id, tab2_id, col20_1, col20_2)         values (1, 1, 'col20_1', 'col20_2');
insert into tab21 (tab21_id, tab2_id, col21_1, col21_2)         values (1, 1, 'col21_1', 'col21_2');
insert into tab_  (tab__id,  col_1_,  col_2_)                   values (1,    'col_1_',  'col_2_');
insert into tab0_ (tab0__id, tab__id, col0_1_, col0_2_, shc_)   values (1, 1, 'col0_1_', 'col0_2_', 'shc_');
insert into tab1_ (tab1__id, tab__id, col1_1_, col1_2_, shc_)   values (1, 1, 'col1_1_', 'col1_2_', 'shc_');
insert into sht__ (sht___id, tab_id,  tab__id, col_1__, col_2__)values (1,1,1,'col_1__', 'col_2__');
*/





