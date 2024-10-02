"""Sapi interface"""
from sapi._internals.parser import parse
from sapi._internals.externals.database_py import dialect
from sapi._internals.externals.database_py.deployment import setup_sapi
from sapi._internals.externals.database_py.data_model import DataModel #, Tree, Table
# The (Tree, Table) approach to making a datamodel isnt very user friendly right now. 
# if it becomes user friendly, then expose it.

# the auto-tests are allowed to violate the interface, if needed. But editor and demo may not.

