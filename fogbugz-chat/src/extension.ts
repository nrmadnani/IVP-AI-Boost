import * as vscode from 'vscode';
import { MCPProcess } from './mcpProcess';
import * as fs from 'fs';
import * as path from 'path';

let mcpProcess: MCPProcess | null = null;
let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
	console.log('FogBugz Chat extension activated');
	// Create output channel for debugging
	outputChannel = vscode.window.createOutputChannel('FogBugz Chat');
	context.subscriptions.push(outputChannel);

	// Register the webview view provider
	const provider = new ChatViewProvider(context.extensionUri, context);
	provider.clearHistory(); // Clear history on activation to start fresh
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
        // Check if user typed "/clear" command - handle locally only
        if (msg.text.trim().toLowerCase() === '/clear') {
            this.clearHistory("Chat History cleared");
            return;
        }
        
        // For /new command, send to Python server AND clear local history
        if (msg.text.trim().toLowerCase() === '/new') {
            if (mcpProcess) {
                mcpProcess.send(msg.text);
                // Save user message to history
                this._addToHistory({ type: 'user', text: msg.text });
            }
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
				this._view?.webview.postMessage({
					type: 'assistant',
					text: message
				});
				
				// If it's the "new conversation" message, clear local history
				if (message.trim().includes('🧹 New conversation started')) {
					this.clearHistory('🧹 New conversation started. (long-term memory preserved).'); 
				}
				
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

	public clearHistory(message: string | null = null) {
		this._context.globalState.update(ChatViewProvider.CHAT_HISTORY_KEY, []);
		this._view?.webview.postMessage({
			type: 'clearHistory',
			message: message
		});
		if (message) {
			outputChannel.appendLine(message);
		} 
	}

	private _getHtmlForWebview(webview: vscode.Webview): string {
		// Try to load from external HTML file
		const htmlPath = path.join(this._context.extensionPath, 'src', 'chatview.html');
		
		try {
			if (fs.existsSync(htmlPath)) {
				return fs.readFileSync(htmlPath, 'utf8');
			}
		} catch (error) {
			outputChannel.appendLine(`Failed to load HTML file: ${error}`);
		}

		// Fallback to inline HTML if file doesn't exist
		return `Sorry, the chat view HTML file is missing.`;
	}

	
	}


export function deactivate() {
	mcpProcess?.dispose();
	outputChannel?.dispose();
}