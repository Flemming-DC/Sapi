"""Sapi interface"""
# -------- User of libery -------- #
from sapi._internals.parser import parse
from sapi._internals.externals.database_py import dialect
from sapi._internals.externals.database_py.deployment import setup_sapi
from sapi._internals.externals.database_py.data_model import DataModel #, Tree, Table
# The (Tree, Table) approach to making a datamodel isnt very user friendly right now. 
# if it becomes user friendly, then expose it.

# -------- Editor -------- #
from sapi._internals import editor_tok as _editor_tok

# -------- AutoTests -------- #
from sapi import _test

