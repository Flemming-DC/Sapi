import * as path from "path";
import { workspace, ExtensionContext, Uri, commands, CompletionList, CancellationToken, 
    DocumentSemanticTokensProvider, TextDocument, ProviderResult, SemanticTokens, DocumentHighlight, 
    Range,
    Position} from "vscode";
const vscode = require('vscode');

import {
    DocumentSemanticsTokensSignature,
    integer,
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient;


// ------------------ //

// const tokenTypes = ['class', 'interface', 'enum', 'function', 'variable'];
// const tokenModifiers = ['declaration', 'documentation'];
// const legend = new vscode.SemanticTokensLegend(tokenTypes, tokenModifiers);

// const provider: DocumentSemanticTokensProvider = {
//   provideDocumentSemanticTokens(document: TextDocument): ProviderResult<SemanticTokens> {
//     // analyze the document and return semantic tokens

//     const tokensBuilder = new vscode.SemanticTokensBuilder(legend);
//     // on line 1, characters 1-5 are a class declaration
//     tokensBuilder.push(
//       new vscode.Range(new vscode.Position(1, 1), new vscode.Position(1, 5)),
//       'class',
//       ['declaration']
//     );
//     return tokensBuilder.build();
//   }
// };

// const selector = { language: 'javap', scheme: 'file' }; // register for all Java documents from the local file system

//vscode.languages.registerDocumentSemanticTokensProvider(selector, provider, legend);




export function activate(context: ExtensionContext) {
    // const config = vscode.workspace.getConfiguration("sapi")

    // const terminal = vscode.window.createTerminal("My Terminal");
    // terminal.sendText("echo term: Hello, world!");
    // terminal.show();
    // context.subscriptions.push(
    // 	vscode.languages.registerDocumentSemanticTokensProvider(
    // 		selector, 
    // 		provider, 
    // 		legend
    // 	)
    // );

// ------------------ //
  
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

