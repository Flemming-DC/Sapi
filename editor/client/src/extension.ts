import { workspace, EventEmitter, ExtensionContext, window, TextDocumentChangeEvent } from "vscode";
import { Disposable, Executable, LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient/node";
import * as path from "path";
import * as fs from "fs";

let client: LanguageClient;

export async function activate(_: ExtensionContext) {
  const traceOutputChannel = window.createOutputChannel("Nrs Language Server trace");
  let lang_server = path.join(__dirname, "..", "..", "target", "debug", "nrs-language-server.exe");
  // let lang_server = path.join(__dirname, "..", "..", "..", "target", "debug", "nrs-language-server.exe");
  // let lang_server = path.join(__dirname, "..", "debug", "nrs-language-server.exe");
  traceOutputChannel.appendLine(`debug lang_server: ${lang_server}`);
  if (fs.existsSync(lang_server)) {
    traceOutputChannel.appendLine(`Found debug server`);
  }

  if (!fs.existsSync(lang_server)) {
    // lang_server = path.join(__dirname, "..", "release", "nrs-language-server.exe");
    lang_server = path.join(__dirname, "nrs-language-server.exe");
  } else if (!fs.existsSync(lang_server)) {
    traceOutputChannel.appendLine(`Failed to find language server ${lang_server}`);
  }
  traceOutputChannel.appendLine(`lang_server: ${lang_server}`);
  traceOutputChannel.appendLine(`__dirname : ${__dirname}`);
  
  const run: Executable = {
    command: lang_server,
    options: {
      env: {
        ...process.env,
        RUST_LOG: "debug",
      },
    },
  };
  const serverOptions: ServerOptions = {
    run, // used if running without debugging/breakpoints
    debug: run, // If the extension is launched in debug mode then the debug server options are used
  };
  
  let clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "nrs" }],
    // Notify the server about file changes to '.clientrc files contained in the workspace
    synchronize: { fileEvents: workspace.createFileSystemWatcher("**/.clientrc") },
    traceOutputChannel,
  };
  // Create the language client and start the client.
  client = new LanguageClient("nrs-language-server", "nrs language server", serverOptions, clientOptions);
  client.start();
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}

