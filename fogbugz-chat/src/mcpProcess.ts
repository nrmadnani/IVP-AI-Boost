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
		this.outputChannel.appendLine(`➡️ MCP SEND: ${message}`);
		this.process.stdin.write(message + '\n');
	}

	onMessage(callback: (message: string) => void) {
		this.onMessageCallback = callback;
	}
	dispose() {
		this.process.kill();
	}
}