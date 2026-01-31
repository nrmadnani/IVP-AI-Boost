import * as vscode from 'vscode';
import { MCPProcess } from './mcpProcess';

let mcpProcess: MCPProcess | null = null;
let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
	console.log('FogBugz Chat extension activated');

	// Create output channel for debugging
	outputChannel = vscode.window.createOutputChannel('FogBugz Chat');
	context.subscriptions.push(outputChannel);

	// Register the webview view provider
	const provider = new ChatViewProvider(context.extensionUri, context);
	
	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(
			'fogbugz-chat.chatView',
			provider
		)
	);

	// Optional: Keep the command to open the sidebar programmatically
	const disposable = vscode.commands.registerCommand(
		'fogbugz-chat.startChat',
		() => {
			vscode.commands.executeCommand('fogbugz-chat.chatView.focus');
		}
	);

	context.subscriptions.push(disposable);
}

class ChatViewProvider implements vscode.WebviewViewProvider {
	private _view?: vscode.WebviewView;
	private _context: vscode.ExtensionContext;

	constructor(
		private readonly _extensionUri: vscode.Uri,
		context: vscode.ExtensionContext
	) {
		this._context = context;
	}

	public resolveWebviewView(
		webviewView: vscode.WebviewView,
		context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken
	) {
		this._view = webviewView;

		webviewView.webview.options = {
			enableScripts: true,
			localResourceRoots: [this._extensionUri]
		};

		webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

		// Start MCP process when view is resolved
		this._startMcpClient();

		// Handle messages from the webview
		webviewView.webview.onDidReceiveMessage((msg) => {
			if (msg.type === 'userMessage' && mcpProcess) {
				mcpProcess.send(msg.text);
			}
		});


	}

	private _startMcpClient() {
		if (mcpProcess) {
			outputChannel.appendLine('MCP process already running');
			return;
		}

		outputChannel.appendLine('Starting MCP process...');

		// You can later move this to settings.json
		const pythonPath = 'D:\\IVP AI Boost\\.venv\\Scripts\\python.exe';
		const clientPath = this._context.asAbsolutePath('python/client.py');

		try {
			mcpProcess = new MCPProcess(pythonPath, clientPath, outputChannel);

			// Listen to the MCP process output and forward to webview
			// We need to modify MCPProcess class to support callbacks
			outputChannel.appendLine('MCP process started successfully');
			mcpProcess.onMessage((text: string) => {
				if (this._view) {
					this._view.webview.postMessage({ type: 'assistant', text });
				}
			});
		} catch (error) {
			outputChannel.appendLine(`Failed to start MCP process: ${error}`);
			vscode.window.showErrorMessage('Failed to start FogBugz Chat MCP process');
		}
	}

	private _getHtmlForWebview(webview: vscode.Webview) {
		return `
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<style>
		:root {
			--bg: var(--vscode-editor-background);
			--fg: var(--vscode-editor-foreground);
			--border: var(--vscode-editorWidget-border);
			--input-bg: var(--vscode-input-background);
			--input-fg: var(--vscode-input-foreground);
			--button-bg: var(--vscode-button-background);
			--button-fg: var(--vscode-button-foreground);
			--user-bg: var(--vscode-textBlockQuote-background);
			--assistant-bg: var(--vscode-editorWidget-background);
		}

		body {
			margin: 0;
			padding: 0;
			background: var(--bg);
			color: var(--fg);
			font-family: var(--vscode-font-family);
			font-size: var(--vscode-font-size);
			display: flex;
			flex-direction: column;
			height: 100vh;
			overflow: hidden;
		}

		#chat {
			flex: 1;
			overflow-y: auto;
			padding: 12px;
			display: flex;
			flex-direction: column;
			gap: 8px;
		}

		.message {
			padding: 8px 10px;
			border-radius: 6px;
			max-width: 100%;
			white-space: pre-wrap;
			line-height: 1.4;
			font-size: 13px;
		}

		.user {
			align-self: flex-end;
			background: var(--user-bg);
			border: 1px solid var(--border);
		}

		.assistant {
			align-self: flex-start;
			background: var(--assistant-bg);
			border: 1px solid var(--border);
			font-family: var(--vscode-editor-font-family);
		}

		#input-container {
			display: flex;
			gap: 6px;
			padding: 8px;
			border-top: 1px solid var(--border);
			background: var(--bg);
		}

		#input {
			flex: 1;
			background: var(--input-bg);
			color: var(--input-fg);
			border: 1px solid var(--border);
			border-radius: 4px;
			padding: 6px 8px;
			font-family: inherit;
			font-size: 13px;
		}

		button {
			background: var(--button-bg);
			color: var(--button-fg);
			border: none;
			border-radius: 4px;
			padding: 0 12px;
			cursor: pointer;
			font-size: 13px;
		}

		button:hover {
			opacity: 0.9;
		}
	</style>
</head>
<body>
	<div id="chat"></div>

	<div id="input-container">
		<input
			id="input"
			placeholder="Ask about FogBugz…"
			onkeydown="if(event.key==='Enter') send()"
		/>
		<button onclick="send()">Send</button>
	</div>

	<script>
		const vscode = acquireVsCodeApi();
		const chat = document.getElementById('chat');
		const input = document.getElementById('input');

		function addMessage(text, cls) {
			const div = document.createElement('div');
			div.className = 'message ' + cls;
			div.textContent = text;
			chat.appendChild(div);
			chat.scrollTop = chat.scrollHeight;
		}

		function send() {
			const text = input.value.trim();
			if (!text) return;

			addMessage(text, 'user');
			vscode.postMessage({ type: 'userMessage', text });
			input.value = '';
		}

		window.addEventListener('message', event => {
			const msg = event.data;
			if (msg.type === 'assistant') {
				addMessage(msg.text, 'assistant');
			}
		});
	</script>
</body>
</html>
		`;
	}
}

export function deactivate() {
	mcpProcess?.dispose();
	outputChannel?.dispose();
}