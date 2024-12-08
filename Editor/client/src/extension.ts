import * as fs from "fs";
import * as path from "path";
import { ExtensionContext} from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from "vscode-languageclient/node";

const vscode = require('vscode');
let client: LanguageClient;




export function activate(context: ExtensionContext) {
    
    const pythonInterpreter = context.asAbsolutePath(path.join("local_editor_env", "Scripts", "python.exe"));
    const serverModule = context.asAbsolutePath(path.join("server", "main.py"));
    
    const outputChannel = vscode.window.createOutputChannel("Sapi");
    let message = fs.existsSync(pythonInterpreter) ? `The file '${pythonInterpreter}' exists.` : `The file '${pythonInterpreter}' does not exist.`;
    outputChannel.appendLine(message);
    message = fs.existsSync(serverModule) ? `The file '${serverModule}' exists.` : `The file '${serverModule}' does not exist.`;
    outputChannel.appendLine(message);

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

    client.onNotification('output', (data) => {
        outputChannel.appendLine("---- QUERY RESULT ----");
        outputChannel.appendLine(data);
        outputChannel.show(true); // true means preserve focus
    });


    // Start the client. This will also launch the server
    client.start().catch((error) => {
        outputChannel.appendLine(`Client Failed to start LSP server:\n ${error}`);
    }); 
}


export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}







