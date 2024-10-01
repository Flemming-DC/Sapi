import * as path from "path";
import { workspace, ExtensionContext } from "vscode";
const vscode = require('vscode');

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient;

export function activate(context: ExtensionContext) {
  vscode.window.showInformationMessage('lang-client');
  const pythonInterpreter = context.asAbsolutePath(path.join("local_editor_env", "Scripts", "python.exe"));
  const serverModule = context.asAbsolutePath(path.join("server", "src", "py_serv.py"));

  const serverOptions: ServerOptions = {
    run: { command: pythonInterpreter, args: [serverModule], transport: TransportKind.stdio },
    debug: { command: pythonInterpreter, args: [serverModule], transport: TransportKind.stdio }
  };

  const clientOptions: LanguageClientOptions = {
    // Register the server for all documents by default
    documentSelector: [{ scheme: "file", language: "*" }],
    // synchronize: {
    //   // Notify the server about file changes to '.clientrc files contained in the workspace
    //   fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    // },
  };

  client = new LanguageClient(
    "LanguageClient-id",
    "LanguageClient-name",
    serverOptions,
    clientOptions
  );
  client.start(); // Start the client. This will also launch the server
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}

