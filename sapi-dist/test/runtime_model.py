from sapi import dialect, DataModel
from sapi._test import Tree, Table

def make_datamodel():
    _tree = Tree(
        tables=[
            Table(name='sht__', parent='tab',  columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id']), 
            Table(name='tab',   parent=None,   columns=['col_1', 'col_2', 'tab_id']), 
            Table(name='tab0',  parent='tab',  columns=['col0_1', 'col0_2', 'shc', 'tab0_id', 'tab1__id', 'tab_id']), 
            Table(name='tab00', parent='tab0', columns=['col00_1', 'col00_2', 'tab00_id', 'tab0_id']), 
            Table(name='tab01', parent='tab0', columns=['col01_1', 'col01_2', 'tab01_id', 'tab0_id']), 
            Table(name='tab1',  parent='tab',  columns=['col1_1', 'col1_2', 'shc', 'tab0__id', 'tab1_id', 'tab_id']), 
            Table(name='tab10', parent='tab1', columns=['col10_1', 'col10_2', 'tab10_id', 'tab1_id']), 
            Table(name='tab2',  parent='tab',  columns=['col2_1', 'col2_2', 'tab2_id', 'tab_id']), 
            Table(name='tab20', parent='tab2', columns=['col20_1', 'col20_2', 'tab20_id', 'tab2_id']), 
            Table(name='tab21', parent='tab2', columns=['col21_1', 'col21_2', 'tab21_id', 'tab2_id']),
            ], 
        name='tree', schema='sapi_demo')

    _tree_ = Tree(
        tables=[
            Table(name='sht__', parent='tab_', columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id']), 
            Table(name='tab_',  parent=None,   columns=['col_1_', 'col_2_', 'tab__id']), 
            Table(name='tab0_', parent='tab_', columns=['col0_1_', 'col0_2_', 'shc_', 'tab0__id', 'tab1_id', 'tab__id']), 
            Table(name='tab1_', parent='tab_', columns=['col1_1_', 'col1_2_', 'shc_', 'tab0_id', 'tab1__id', 'tab__id']),
            ], 
        name='tree_', schema='sapi_demo')

    return DataModel(dialect.postgres(), [_tree, _tree_])

