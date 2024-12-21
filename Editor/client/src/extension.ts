import * as fs from "fs";
import * as path from "path";
import { ExtensionContext} from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from "vscode-languageclient/node";
import log from "./log";
import * as yaml from 'yaml';

const vscode = require('vscode') as typeof import('vscode');
let client: LanguageClient;



export function activate(context: ExtensionContext) {
    const sapi_settings_path = path.join(__dirname, '..', '..', ".vscode", "sapi_settings.yml");

    // const pythonInterpreter = __dirname + "/local_editor_env/Scripts/python.exe";
    // const serverModule = __dirname + "/server/main.py";

    let pythonInterpreter = path.join(__dirname, '..', '..', "local_editor_env", "Scripts", "python.exe");
    // const serverModule = path.join(__dirname, "server", "main.py");
    
    // const pythonInterpreter = context.asAbsolutePath(path.join("local_editor_env", "Scripts", "python.exe"));
    let serverModule = context.asAbsolutePath(path.join("server", "main.py"));
    log.write(pythonInterpreter);
    log.write(serverModule);
    log.write(path.join(__dirname, '..', '..', "local_editor_env", "Scripts", "python.exe"));
    log.write(path.join('..', '..', "local_editor_env", "Scripts", "python.exe"));
    log.write(sapi_settings_path);
    
    const outputChannel = vscode.window.createOutputChannel("Sapi");
    let message = fs.existsSync(pythonInterpreter) ? `The file '${pythonInterpreter}' exists.` : `The file '${pythonInterpreter}' does not exist.`;
    outputChannel.appendLine(message);
    message = fs.existsSync(serverModule) ? `The file '${serverModule}' exists.` : `The file '${serverModule}' does not exist.`;
    outputChannel.appendLine(message);

    outputChannel.appendLine("");
    outputChannel.appendLine(pythonInterpreter);
    outputChannel.appendLine(serverModule);
    outputChannel.appendLine(path.join(__dirname, '..', '..', "local_editor_env", "Scripts", "python.exe"));
    outputChannel.appendLine(path.join('..', '..', "local_editor_env", "Scripts", "python.exe"));
    outputChannel.appendLine(sapi_settings_path);

    try {
        const sapi_settings_content: string = fs.readFileSync(sapi_settings_path, "utf-8");
        log.write(sapi_settings_content);
        outputChannel.appendLine(sapi_settings_content);
    } catch (err) {
        log.write(err);
        outputChannel.appendLine(err);
    }
    
    
    const workspaceFolders = vscode.workspace.workspaceFolders;

    if (workspaceFolders && workspaceFolders.length > 0) {
        const userProjectPath = workspaceFolders[0].uri.fsPath;
        log.write(`User's Project Path: ${userProjectPath}`);
        outputChannel.appendLine(`User's Project Path: ${userProjectPath}`);

        let sapi_set = path.join(userProjectPath, "sapi_settings.yml");
        if (!fs.existsSync(sapi_set)) {
            sapi_set = path.join(userProjectPath, ".vscode", "sapi_settings.yml");
        } else if (!fs.existsSync(sapi_set)) { 
            sapi_set = path.join(userProjectPath, "sapi_settings.yaml");
        } else if (!fs.existsSync(sapi_set)) { 
            sapi_set = path.join(userProjectPath, ".vscode", "sapi_settings.yaml");
        } else if (!fs.existsSync(sapi_set)) { 
            sapi_set = path.join(userProjectPath, "sapi_settings.json");
        } else if (!fs.existsSync(sapi_set)) { 
            sapi_set = path.join(userProjectPath, ".vscode", "sapi_settings.json");
        } else {
            outputChannel.appendLine("Failed to find sapi_settings");
        }   
        
        try {
            const content = fs.readFileSync(sapi_set, 'utf-8'); // Read the file
            const data = sapi_set.endsWith("json") ? JSON.parse(content) : yaml.parse(content); 
            outputChannel.appendLine(`yml/json Data: ${data}`);
            // data['start_server']
        } catch (err) {
            outputChannel.appendLine(`Error parsing yml/json file: ${err}`);
        }



        pythonInterpreter = path.join(userProjectPath, "local_editor_env", "Scripts", "python.exe");
        // serverModule = path.join(userProjectPath, "server", "main.py");
        
        outputChannel.appendLine(pythonInterpreter);
        // outputChannel.appendLine(serverModule);
    

    } else {
        log.write("No workspace folder is open.");
        outputChannel.appendLine("No workspace folder is open.");
    }
    

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







