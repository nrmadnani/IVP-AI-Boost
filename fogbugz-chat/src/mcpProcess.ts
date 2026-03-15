import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import * as vscode from 'vscode';

export class MCPProcess {
	private process: ChildProcessWithoutNullStreams;
	private outputChannel: vscode.OutputChannel;
	private onMessageCallback?: (message: string) => void;
	constructor(
		pythonPath: string,
		clientScriptPath: string,
		outputChannel: vscode.OutputChannel
	) {
		this.outputChannel = outputChannel;

		this.process = spawn(pythonPath, [clientScriptPath], {
			stdio: 'pipe',
		});

		this.process.stdout.on('data', (data) => {
			this.outputChannel.appendLine(`🧠 MCP: ${data.toString()}`);
			if (this.onMessageCallback) {
				this.onMessageCallback(data.toString());
			}
		});

		this.process.stderr.on('data', (data) => {
			this.outputChannel.appendLine(`❌ MCP ERROR: ${data.toString()}`);
		});

		this.process.on('exit', (code) => {
			this.outputChannel.appendLine(`⚠️ MCP process exited with code ${code}`);
		});
	}

	send(message: string) {
        // 1. Escape the actual newlines into literal text characters "\\n"
        // This ensures the entire prompt stays on ONE line when passing through stdin
        const safeMessage = message.replace(/\r?\n/g, '\\n');

        this.outputChannel.appendLine(`➡️ MCP SEND: ${safeMessage}`);
        
        // 2. Add the SINGLE newline at the very end to tell Python "execute now"
        this.process.stdin.write(safeMessage + '\n');
    }

	onMessage(callback: (message: string) => void) {
		this.onMessageCallback = callback;
	}
	dispose() {
		this.process.kill();
	}
}