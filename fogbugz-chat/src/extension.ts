import * as vscode from 'vscode';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process';

let mcpProcess: ChildProcessWithoutNullStreams | null = null;
let panel: vscode.WebviewPanel | null = null;

export function activate(context: vscode.ExtensionContext) {
	console.log('FogBugz Chat extension activated');

	const disposable = vscode.commands.registerCommand(
		'fogbugz-chat.startChat',
		() => {
			startMcpClient(context);
			openChatUI(context);
		}
	);

	context.subscriptions.push(disposable);
}

function startMcpClient(context: vscode.ExtensionContext) {
	if (mcpProcess) {
		return;
	}

	// You can later move this to settings.json
	const pythonPath = 'D:\\IVP AI Boost\\.venv\\Scripts\\python.exe';
	const clientPath = context.asAbsolutePath('python/client.py');

	mcpProcess = spawn(pythonPath, [clientPath], {
		stdio: 'pipe',
	});

	mcpProcess.stdout.on('data', (data) => {
		const text = data.toString();
		console.log('[MCP STDOUT]', text);
		panel?.webview.postMessage({
			type: 'assistant',
			text,
		});
	});

	mcpProcess.stderr.on('data', (data) => {
		console.error('[MCP STDERR]', data.toString());
	});

	mcpProcess.on('exit', (code) => {
		console.log(`MCP client exited with code ${code}`);
		mcpProcess = null;
	});
}

function openChatUI(context: vscode.ExtensionContext) {
	if (panel) {
		panel.reveal();
		return;
	}

	panel = vscode.window.createWebviewPanel(
		'fogbugzChat',
		'FogBugz Chat',
		vscode.ViewColumn.One,
		{
			enableScripts: true,
		}
	);

	panel.webview.html = getWebviewHtml();

	panel.webview.onDidReceiveMessage((msg) => {
		if (msg.type === 'userMessage' && mcpProcess) {
			mcpProcess.stdin.write(msg.text + '\n');
		}
	});

	panel.onDidDispose(() => {
		panel = null;
	});
}

function getWebviewHtml(): string {
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
		}

		#chat {
			flex: 1;
			overflow-y: auto;
			padding: 16px;
			display: flex;
			flex-direction: column;
			gap: 12px;
		}

		.message {
			padding: 10px 12px;
			border-radius: 6px;
			max-width: 90%;
			white-space: pre-wrap;
			line-height: 1.5;
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
			gap: 8px;
			padding: 12px;
			border-top: 1px solid var(--border);
			background: var(--bg);
		}

		#input {
			flex: 1;
			background: var(--input-bg);
			color: var(--input-fg);
			border: 1px solid var(--border);
			border-radius: 4px;
			padding: 8px;
			font-family: inherit;
		}

		button {
			background: var(--button-bg);
			color: var(--button-fg);
			border: none;
			border-radius: 4px;
			padding: 0 16px;
			cursor: pointer;
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
			placeholder="Ask about FogBugz documentation…"
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


export function deactivate() {
	mcpProcess?.kill();
}
