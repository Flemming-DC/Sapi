from sapi import dialect, DataModel
from sapi._test import Tree, Table
from test.demo_pg_model import demo_schema

def make_datamodel():
    join_clause = 'JOIN __parent__ USING (__keys__)'
    tree = Tree(
        tables=[
            Table(name='tab',   primary_key='tab_id',   parent=None,   columns=['col_1', 'col_2', 'tab_id'],  join_clause=join_clause), 
            Table(name='tab0',  primary_key='tab0_id',  parent='tab',  columns=['col0_1', 'col0_2', 'shc', 'tab0_id', 'tab1__id', 'tab_id'], join_clause=join_clause), 
            Table(name='tab00', primary_key='tab00_id', parent='tab0', columns=['col00_1', 'col00_2', 'tab00_id', 'tab0_id'], join_clause=join_clause), 
            Table(name='tab01', primary_key='tab01_id', parent='tab0', columns=['col01_1', 'col01_2', 'tab01_id', 'tab0_id'], join_clause=join_clause), 
            Table(name='tab1',  primary_key='tab1_id',  parent='tab',  columns=['col1_1', 'col1_2', 'shc', 'tab0__id', 'tab1_id', 'tab_id'], join_clause=join_clause), 
            Table(name='tab10', primary_key='tab10_id', parent='tab1', columns=['col10_1', 'col10_2', 'tab10_id', 'tab1_id'], join_clause=join_clause), 
            Table(name='tab2',  primary_key='tab2_id',  parent='tab',  columns=['col2_1', 'col2_2', 'tab2_id', 'tab_id'], join_clause=join_clause), 
            Table(name='tab20', primary_key='tab20_id', parent='tab2', columns=['col20_1', 'col20_2', 'tab20_id', 'tab2_id'], join_clause=join_clause), 
            Table(name='tab21', primary_key='tab21_id', parent='tab2', columns=['col21_1', 'col21_2', 'tab21_id', 'tab2_id'], join_clause=join_clause), 
            Table(name='sht__', primary_key='sht___id', parent='tab',  columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id'], join_clause=join_clause), 
            ], 
        name='tree', schema=demo_schema())

    tree_ = Tree(
        tables=[
            Table(name='tab_',  primary_key='tab__id',  parent=None,   columns=['col_1_', 'col_2_', 'tab__id'], join_clause=join_clause), 
            Table(name='tab0_', primary_key='tab0__id', parent='tab_', columns=['col0_1_', 'col0_2_', 'shc_', 'tab0__id', 'tab1_id', 'tab__id'], join_clause=join_clause), 
            Table(name='tab1_', primary_key='tab1__id', parent='tab_', columns=['col1_1_', 'col1_2_', 'shc_', 'tab0_id', 'tab1__id', 'tab__id'], join_clause=join_clause), 
            Table(name='sht__', primary_key='sht___id', parent='tab_', columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id'], join_clause=join_clause), 
            ], 
        name='tree_', schema=demo_schema())

    tree_manual = Tree(
        tables=[
            Table(name='tab_manual',  primary_key='tab_manual_id',  parent=None,   
                  columns=['tab_manual_id', 'col_manual_1', 'col_manual_2'], join_clause=join_clause), 
            Table(name='tab0_manual', primary_key='tab0_manual_id', parent='tab_manual_id', 
                  columns=['tab0_manual_id', 'tab_manual_id', 'col0_manual_1', 'col0_manual_2'], join_clause=join_clause), 
            ], 
        name='tree_manual', schema=demo_schema())
     
    dual_key = Tree(
        tables=[
            Table(name='dual_pk', primary_key='dual_pk_id1, dual_pk_id2', parent=None,      
                  columns=['dual_pk_id1', 'dual_pk_id2', 'dual_pk_col'], 
                  join_clause=join_clause), 
            Table(name='dual_fk', primary_key='dual_fk_id1, dual_fk_id2', parent='dual_pk', 
                  columns=['dual_fk_id1', 'dual_pk_id1', 'dual_pk_id2', 'dual_fk_col'], 
                  join_clause='JOIN __parent__ USING (dual_pk_id1, dual_pk_id2)'), 
            ], 
        name='dual_key', schema=demo_schema())

    historic = Tree(
        tables=[
            Table(name='historic1', primary_key='historic1_id', parent=None, join_clause=join_clause, columns=[
                'historic1_id', 'persistent1_id', 'from_date1', 'to_date1', 'historic_col1']), 
            Table(name='historic2', primary_key='historic2_id', parent='historic1',  
                join_clause='JOIN __parent__ ON persistent2_id = persistent1_id and from_date2 < to_date2 and from_date1 < to_date1', 
                columns=['historic2_id', 'historic1_id', 'persistent2_id', 'from_date2', 'to_date2', 'historic_col2']), 
            ], 
        name='historic', schema=demo_schema())


    trees = [tree, tree_, tree_manual, dual_key, historic]

    for tr in trees:
        for tab in tr.tables:
            if tab.parent:
                tab.join_clause = (tab.join_clause
                    ).replace('__parent__', tab.parent
                    ).replace('__keys__', f'{tab.parent}_id')
            
    return DataModel(dialect.postgres(), trees)

