import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process';

let pyProcess: ChildProcessWithoutNullStreams | null = null;

/*

export function activate(context: vscode.ExtensionContext) {
    startPythonBackend();

    const disposable = vscode.commands.registerCommand('autocomment.processText', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("Nessun file aperto!");
            return;
        }

        const selection = editor.selection;
        let text = editor.document.getText(selection);
        if (!text) text = editor.document.getText();

        try {
            await waitForBackend();

            let accumulated = "";
            await callPythonBackendStream(text, async (chunk) => {
                accumulated += chunk;

                // Aggiorna l'editor progressivamente
                await editor.edit(editBuilder => {
                    if (selection && !selection.isEmpty) {
                        editBuilder.replace(selection, accumulated);
                    } else {
                        const firstLine = editor.document.lineAt(0);
                        const lastLine = editor.document.lineAt(editor.document.lineCount - 1);
                        const fullRange = new vscode.Range(firstLine.range.start, lastLine.range.end);
                        editBuilder.replace(fullRange, accumulated);
                    }
                }, { undoStopBefore: false, undoStopAfter: false });
            });

            vscode.window.showInformationMessage("Testo aggiornato dal backend Python!");
        } catch (err: any) {
            vscode.window.showErrorMessage(`Errore backend: ${err.message}`);
        }
    });

    context.subscriptions.push(disposable);
}

*/
export function activate(context: vscode.ExtensionContext) {
    startPythonBackend();

    const disposable = vscode.commands.registerCommand('autocomment.processText', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("Nessun file aperto!");
            return;
        }

        const selection = editor.selection;
        let text = editor.document.getText(selection);
        if (!text) text = editor.document.getText();

        try {
            await waitForBackend();
            const result = await callPythonBackend(text);

            await editor.edit(editBuilder => {
                if (selection && !selection.isEmpty) {
                    editBuilder.replace(selection, result);
                } else {
                    const firstLine = editor.document.lineAt(0);
                    const lastLine = editor.document.lineAt(editor.document.lineCount - 1);
                    const fullRange = new vscode.Range(firstLine.range.start, lastLine.range.end);
                    editBuilder.replace(fullRange, result);
                }
            });

            vscode.window.showInformationMessage("Testo aggiornato dal backend Python!");
        } catch (err: any) {
            vscode.window.showErrorMessage(`Errore backend: ${err.message}`);
        }
    });

    context.subscriptions.push(disposable);
}


function startPythonBackend() {
    if (pyProcess) return;

    const backendPath = path.join(__dirname, "../backend");
    const pythonExecutable = process.platform === "win32"
        ? `"C:\\Users\\jciotola\\OneDrive - NTT DATA EMEAL\\Desktop\\jordan_github\\VsCodeCommentsExtension\\autocomment\\backend\\venv\\Scripts\\python.exe"`
        : path.join(backendPath, ".venv/bin/python");

    const command = `${pythonExecutable} -m uvicorn app:app --host 127.0.0.1 --port 8000`;

    pyProcess = spawn(command, {
        cwd: backendPath,
        shell: true
    });

    pyProcess.stdout.on('data', data => console.log(`[PYTHON] ${data.toString()}`));
    pyProcess.stderr.on('data', data => console.error(`[PYTHON ERROR] ${data.toString()}`));
    pyProcess.on('close', code => {
        console.log(`Backend Python terminato con codice ${code}`);
        pyProcess = null;
    });
}

// Controlla che il backend risponda
async function waitForBackend() {
    const maxRetries = 20;
    const delay = 200;

    for (let i = 0; i < maxRetries; i++) {
        try {
            const res = await globalThis.fetch("http://127.0.0.1:8000/health");
            if (res.ok) return;
        } catch {
            // ignora errori di connessione
        }
        await new Promise(r => setTimeout(r, delay));
    }

    throw new Error("Backend Python non pronto dopo vari tentativi");
}

/*
async function callPythonBackendStream(
    text: string,
    onData: (chunk: string) => void
): Promise<void> {
    const res = await globalThis.fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const reader = res.body?.getReader();
    if (!reader) throw new Error("Stream non disponibile dal backend");

    const decoder = new TextDecoder();
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        onData(chunk);
    }
}


// Chiama il backend Python
*/
async function callPythonBackend(text: string): Promise<string> {
    const res = await globalThis.fetch("http://127.0.0.1:8000/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    return data.result; // backend deve rispondere {"text": "..."}
}

export function deactivate() {
    if (pyProcess) {
        pyProcess.kill();
        pyProcess = null;
    }
}


