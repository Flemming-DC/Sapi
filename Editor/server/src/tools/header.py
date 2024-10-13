from enum import IntFlag, auto
from lsprotocol import types as t
from tools.server import server, serverType
from sapi import _editor_tok
from dataclasses import dataclass
from tools.settings import Settings
from tools import data_model


def semantic_tokens_full(_: serverType, params: t.SemanticTokensParams) -> t.SemanticTokens | None:
    """Return the semantic tokens for the entire document"""
    # repeated code
    document_uri = params.text_document.uri
    if not document_uri.endswith('.sapi'):
        return None
    document = server.workspace.get_text_document(document_uri)

    # repeated code
    fal_settings = Settings.try_load()
    if fal_settings.is_err():
        server.show_message(fal_settings.err, t.MessageType.Error)
        return None
    database_name = fal_settings.ok.current_database
    database = fal_settings.ok.databases[database_name]
    dialect = database.dialect


def code_actions(params: t.CodeActionParams) -> list[t.CodeAction]:
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(uri)
    
    # dataModel = runtime_model.make_datamodel() # hardcoded datamodel
    fal_dataModel = data_model.make_datamodel()
    if fal_dataModel.is_err():
        server.show_message(fal_dataModel.err, t.MessageType.Error)
        return []

