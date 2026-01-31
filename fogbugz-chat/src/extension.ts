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
			provider,
			{
				webviewOptions: {
					retainContextWhenHidden: true  // Keep webview alive when hidden
				}
			}
		)
	);

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
	private static readonly CHAT_HISTORY_KEY = 'fogbugz.chatHistory';

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
			if (msg.type === 'userMessage') {
				// Check if user typed "clear" command
				if (msg.text.trim().toLowerCase() === 'clear') {
					this._clearHistory();
					return;
				}
				
				if (mcpProcess) {
					mcpProcess.send(msg.text);
					// Save user message to history
					this._addToHistory({ type: 'user', text: msg.text });
				}
			} else if (msg.type === 'requestHistory') {
				// Send chat history to webview when it requests it
				this._sendHistoryToWebview();
			}
		});

		// Send history when webview is first loaded
		this._sendHistoryToWebview();
	}

	private _startMcpClient() {
		if (mcpProcess) {
			outputChannel.appendLine('MCP process already running');
			return;
		}

		outputChannel.appendLine('Starting MCP process...');

		const pythonPath = 'D:\\IVP AI Boost\\.venv\\Scripts\\python.exe';
		const clientPath = this._context.asAbsolutePath('python/client.py');

		try {
			mcpProcess = new MCPProcess(pythonPath, clientPath, outputChannel);

			mcpProcess.onMessage((message) => {
				// Forward to webview
				this._view?.webview.postMessage({
					type: 'assistant',
					text: message
				});
				// Save assistant message to history
				this._addToHistory({ type: 'assistant', text: message });
			});

			outputChannel.appendLine('MCP process started successfully');
		} catch (error) {
			outputChannel.appendLine(`Failed to start MCP process: ${error}`);
			vscode.window.showErrorMessage('Failed to start FogBugz Chat MCP process');
		}
	}

	private _addToHistory(message: { type: string; text: string }) {
		const history = this._getHistory();
		history.push(message);
		// Keep only last 100 messages to avoid storage limits
		if (history.length > 100) {
			history.shift();
		}
		this._context.globalState.update(ChatViewProvider.CHAT_HISTORY_KEY, history);
	}

	private _getHistory(): Array<{ type: string; text: string }> {
		return this._context.globalState.get(ChatViewProvider.CHAT_HISTORY_KEY, []);
	}

	private _sendHistoryToWebview() {
		const history = this._getHistory();
		this._view?.webview.postMessage({
			type: 'loadHistory',
			history: history
		});
	}

	private _clearHistory() {
		this._context.globalState.update(ChatViewProvider.CHAT_HISTORY_KEY, []);
		this._view?.webview.postMessage({
			type: 'clearHistory'
		});
		outputChannel.appendLine('Chat history cleared');
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

		.system {
			align-self: center;
			background: transparent;
			border: none;
			font-size: 12px;
			opacity: 0.6;
			font-style: italic;
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
			placeholder="Ask about FogBugz… (type 'clear' to clear history)"
			onkeydown="if(event.key==='Enter') send()"
		/>
		<button onclick="send()">Send</button>
	</div>

	<script>
		const vscode = acquireVsCodeApi();
		const chat = document.getElementById('chat');
		const input = document.getElementById('input');

		// Request chat history when webview loads
		vscode.postMessage({ type: 'requestHistory' });

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

			// Check if user typed "clear"
			if (text.toLowerCase() === 'clear') {
				vscode.postMessage({ type: 'userMessage', text });
				input.value = '';
				return;
			}

			addMessage(text, 'user');
			vscode.postMessage({ type: 'userMessage', text });
			input.value = '';
		}

		window.addEventListener('message', event => {
			const msg = event.data;
			
			if (msg.type === 'assistant') {
				addMessage(msg.text, 'assistant');
			} else if (msg.type === 'loadHistory') {
				// Load chat history
				chat.innerHTML = '';
				msg.history.forEach(item => {
					addMessage(item.text, item.type);
				});
			} else if (msg.type === 'clearHistory') {
				chat.innerHTML = '';
				addMessage('Chat history cleared', 'system');
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