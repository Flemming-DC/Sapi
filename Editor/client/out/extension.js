"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const path = require("path");
const vscode = require('vscode');
const node_1 = require("vscode-languageclient/node");
let client;
function activate(context) {
    vscode.window.showInformationMessage('lang-client');
    const pythonInterpreter = context.asAbsolutePath(path.join("local_editor_env", "Scripts", "python.exe"));
    const serverModule = context.asAbsolutePath(path.join("server", "src", "py_serv.py"));
    const serverOptions = {
        run: { command: pythonInterpreter, args: [serverModule], transport: node_1.TransportKind.stdio },
        debug: { command: pythonInterpreter, args: [serverModule], transport: node_1.TransportKind.stdio }
    };
    const clientOptions = {
        // Register the server for all documents by default
        documentSelector: [{ scheme: "file", language: "*" }],
        // synchronize: {
        //   // Notify the server about file changes to '.clientrc files contained in the workspace
        //   fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
        // },
    };
    client = new node_1.LanguageClient("LanguageClient-id", "LanguageClient-name", serverOptions, clientOptions);
    client.start(); // Start the client. This will also launch the server
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map