"""Sapi interface"""
from sapi._internals.parser import parse
from sapi._internals.execution import dependencies
from sapi._internals.db_contact import dialect
from sapi._internals.db_contact.deployment import setup_sapi
from sapi._internals.db_contact.data_model import DataModel #, Tree, Table
from sapi._internals.execution.to_be_named import Transaction, read, QueryResult, Database
# The (Tree, Table) approach to making a datamodel isnt very user friendly right now. 
# if it becomes user friendly, then expose it.

from sapi import _editor # only for use by Sapi Editor
from sapi import _test # only for use by Sapi AutoTests

