import * as path from "path";
import { ExtensionContext} from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from "vscode-languageclient/node";

const vscode = require('vscode');
let client: LanguageClient;




export function activate(context: ExtensionContext) {
  
    const pythonInterpreter = context.asAbsolutePath(path.join("local_editor_env", "Scripts", "python.exe"));
    const serverModule = context.asAbsolutePath(path.join("server", "main.py"));

    const serverOptions: ServerOptions = {
        run: { command: pythonInterpreter, args: [serverModule], transport: TransportKind.stdio },
        debug: { command: pythonInterpreter, args: [serverModule], transport: TransportKind.stdio }
    };

    
    const clientOptions: LanguageClientOptions = {
        // Register the server for all documents by default
        documentSelector: [{ scheme: "file", language: "*" }],
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







