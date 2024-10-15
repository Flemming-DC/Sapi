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
  // const config = vscode.workspace.getConfiguration("sapi")

  // const outputChannel = vscode.window.createOutputChannel("My Extension");
  // // outputChannel.appendLine("out: Hello, world!");
  // // outputChannel.show();

  // const terminal = vscode.window.createTerminal("My Terminal");
  // terminal.sendText("echo term: Hello, world!");
  // terminal.show();


  const pythonInterpreter = context.asAbsolutePath(path.join("local_editor_env", "Scripts", "python.exe"));
  const serverModule = context.asAbsolutePath(path.join("server", "main.py"));

  const serverOptions: ServerOptions = {
    run: { command: pythonInterpreter, args: [serverModule], transport: TransportKind.stdio },
    debug: { command: pythonInterpreter, args: [serverModule], transport: TransportKind.stdio }
  };

  const clientOptions: LanguageClientOptions = {
    // Register the server for all documents by default
    documentSelector: [{ scheme: "file", language: "*" }],
    // outputChannel,
    // synchronize: {
    //   // Notify the server about file changes to '.clientrc files contained in the workspace
    //   fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    // },
  };


  client = new LanguageClient(
    "LanguageClient-id",
    "LanguageClient-name",
    serverOptions,
    clientOptions,
  );

  const outputChannel = vscode.window.createOutputChannel("Sapi");
  client.onNotification('output', (data) => {
    outputChannel.appendLine("---- QUERY RESULT ----");
    outputChannel.appendLine(data);
    outputChannel.show(true); // true means preserve focus
  });

  client.start(); // Start the client. This will also launch the server
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}

