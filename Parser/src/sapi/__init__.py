"""Sapi interface"""
from sapi._internals.parser import parse
from sapi._internals.externals.database_py import dialect
from sapi._internals.externals.database_py.deployment import setup_sapi
from sapi._internals.externals.database_py.data_model import DataModel #, Tree, Table
# The (Tree, Table) approach to making a datamodel isnt very user friendly right now. 
# if it becomes user friendly, then expose it.

from sapi import _editor # only for use by Sapi Editor
from sapi import _test # only for use by Sapi AutoTests

