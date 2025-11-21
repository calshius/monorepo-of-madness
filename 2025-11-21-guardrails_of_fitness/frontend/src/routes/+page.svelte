<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	interface Message {
		role: 'user' | 'assistant' | 'system';
		content: string;
		timestamp: Date;
	}

	function formatMessageContent(content: string): string {
		// Check if content contains mermaid code blocks
		const mermaidRegex = /```mermaid\s*([\s\S]*?)```/g;
		const hasMermaid = mermaidRegex.test(content);
		
		if (hasMermaid) {
			// Reset regex lastIndex
			mermaidRegex.lastIndex = 0;
			
			// Replace mermaid blocks with divs that will be rendered
			let formattedContent = content.replace(mermaidRegex, (match, mermaidCode) => {
				const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
				// Schedule mermaid rendering after DOM update
				setTimeout(() => {
					const mermaid = (window as any).mermaid;
					if (mermaid) {
						const element = document.getElementById(id);
						if (element) {
							mermaid.render(`mermaid-svg-${id}`, mermaidCode.trim()).then((result: any) => {
								element.innerHTML = result.svg;
							});
						}
					}
				}, 100);
				return `<div id="${id}" class="mermaid-diagram uk-margin"></div>`;
			});
			
			// Apply other formatting
			return formattedContent
				.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
				.replace(/\n/g, '<br>');
		}
		
		// Convert markdown-style bold to HTML
		return content
			.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
			.replace(/\n/g, '<br>');
	}

	let messages = $state<Message[]>([]);
	let currentMessage = $state('');
	let ws: WebSocket | null = null;
	let isConnected = $state(false);
	let isThinking = $state(false);
	let currentResponse = $state('');
	let toolActivity = $state('');

	const WS_URL = 'ws://localhost:8000/ws';

	const cannedQuestions = [
		'What are my ideal macros based on my data?',
		'How many calories am I burning in my workouts?',
		'What\'s my average protein intake?',
		'Find me healthy recipes'
	];

	function connectWebSocket() {
		ws = new WebSocket(WS_URL);

		ws.onopen = () => {
			isConnected = true;
			console.log('WebSocket connected');
		};

		ws.onmessage = (event) => {
			const data = JSON.parse(event.data);

			switch (data.type) {
				case 'start':
					isThinking = true;
					currentResponse = '';
					toolActivity = data.content;
					break;

				case 'token':
					currentResponse += data.content;
					break;

				case 'tool_start':
					toolActivity = data.content;
					break;

				case 'tool_end':
					toolActivity = '';
					break;

				case 'end':
					if (currentResponse) {
						messages = [
							...messages,
							{
								role: 'assistant',
								content: currentResponse,
								timestamp: new Date()
							}
						];
					}
					isThinking = false;
					currentResponse = '';
					toolActivity = '';
					break;

				case 'error':
					console.error('Error from server:', data.content);
					messages = [
						...messages,
						{
							role: 'system',
							content: `Error: ${data.content}`,
							timestamp: new Date()
						}
					];
					isThinking = false;
					currentResponse = '';
					toolActivity = '';
					break;
			}
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
			isConnected = false;
		};

		ws.onclose = () => {
			isConnected = false;
			console.log('WebSocket disconnected');
			// Attempt to reconnect after 3 seconds
			setTimeout(() => {
				if (!isConnected) {
					connectWebSocket();
				}
			}, 3000);
		};
	}

	function sendMessage() {
		if (!currentMessage.trim() || !ws || ws.readyState !== WebSocket.OPEN) {
			return;
		}

		const userMessage = currentMessage.trim();

		// Add user message to chat
		messages = [
			...messages,
			{
				role: 'user',
				content: userMessage,
				timestamp: new Date()
			}
		];

		// Send to backend
		ws.send(JSON.stringify({ message: userMessage }));

		// Clear input
		currentMessage = '';
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function askCannedQuestion(question: string) {
		currentMessage = question;
		sendMessage();
	}

	onMount(() => {
		connectWebSocket();
	});

	onDestroy(() => {
		if (ws) {
			ws.close();
		}
	});
</script>

<div class="uk-section uk-section-primary uk-section-small">
	<div class="uk-container">
		<h1 class="uk-heading-medium uk-margin-remove-bottom">Fitness Analysis Assistant</h1>
		<p class="uk-text-lead uk-margin-small-top">
			<span class="uk-label" class:uk-label-success={isConnected} class:uk-label-danger={!isConnected}>
				{isConnected ? 'Connected' : 'Disconnected'}
			</span>
		</p>
	</div>
</div>

<div class="uk-section" style="height: calc(100vh - 180px); display: flex; flex-direction: column;">
	<div class="uk-container" style="flex: 1; display: flex; flex-direction: column; max-width: 1200px;">
		<div class="uk-card uk-card-default uk-card-body" style="flex: 1; overflow-y: auto; margin-bottom: 1rem;">
			{#if messages.length === 0}
				<div>
					<h3 class="uk-h3">Welcome to your Fitness Analysis Assistant!</h3>
					<p>Ask me anything about your fitness data:</p>
					<div class="uk-margin" uk-margin>
						{#each cannedQuestions as question}
							<button 
								class="uk-button uk-button-primary" 
								onclick={() => askCannedQuestion(question)}
								disabled={!isConnected || isThinking}
							>
								{question}
							</button>
						{/each}
					</div>
				</div>
			{/if}

			{#each messages as message}
				<div class="uk-card uk-margin" class:uk-card-primary={message.role === 'user'} class:uk-card-secondary={message.role === 'assistant'} class:uk-card-default={message.role === 'system'}>
					<div class="uk-card-header">
						<h3 class="uk-card-title uk-margin-remove-bottom">{message.role === 'user' ? 'You' : message.role === 'assistant' ? 'Assistant' : 'System'}</h3>
						<p class="uk-text-meta uk-margin-remove-top">{message.timestamp.toLocaleTimeString()}</p>
					</div>
					<div class="uk-card-body">
						{@html formatMessageContent(message.content)}
					</div>
				</div>
			{/each}

			{#if isThinking}
				<div class="uk-card uk-card-secondary uk-margin">
					<div class="uk-card-header">
						<h3 class="uk-card-title uk-margin-remove-bottom">Assistant</h3>
						<p class="uk-text-meta uk-margin-remove-top">Thinking...</p>
					</div>
					<div class="uk-card-body">
						{#if toolActivity}
							<div class="uk-alert uk-alert-primary">
								<p class="uk-text-italic">{toolActivity}</p>
							</div>
						{/if}
						{#if currentResponse}
							<div>
								{@html formatMessageContent(currentResponse)}
							</div>
						{/if}
					</div>
				</div>
			{/if}
		</div>

		<div class="uk-grid-small" uk-grid>
			<div class="uk-width-expand">
				<textarea
					class="uk-textarea"
					bind:value={currentMessage}
					onkeydown={handleKeyDown}
					placeholder="Ask about your fitness data..."
					disabled={!isConnected || isThinking}
					rows="3"
				></textarea>
			</div>
			<div class="uk-width-auto">
				<button 
					class="uk-button uk-button-primary uk-button-large" 
					onclick={sendMessage} 
					disabled={!isConnected || isThinking || !currentMessage.trim()}
					style="height: 100%;"
				>
					Send
				</button>
			</div>
		</div>
	</div>
</div>