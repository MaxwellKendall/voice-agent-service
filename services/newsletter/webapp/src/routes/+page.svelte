<script lang="ts">
	import { onMount } from 'svelte';
	import { marked } from 'marked';
	import { 
		chatState, 
		newsletterState, 
		chatHistoryForAPI,
		promptState,
		addMessage, 
		setNewsletterMarkdown, 
		updateNewsletterMarkdown, 
		resetToChat,
		updatePrompt
	} from '$lib/stores.js';
	import { generateNewsletterFromChat, sendMessageAndGetResponse } from '$lib/utils.js';
	import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
	import { faPaperPlane, faEnvelope, faSpinner, faArrowUp } from '@fortawesome/free-solid-svg-icons';

	let messageInput = '';
	let isGenerating = false;
	let isSending = false;
	let activeView = 'chat'; // 'chat' | 'newsletter' | 'prompt'
	let messagesEnd: HTMLElement;

	// Handle sending a message
	async function handleSendMessage() {
		if (!messageInput.trim() || isSending) return;
		
		const messageToSend = messageInput.trim();
		messageInput = ''; // Clear input immediately for better UX
		
		isSending = true;
		await sendMessageAndGetResponse(messageToSend);
		isSending = false;
	}

	// Handle generating newsletter
	async function handleGenerateNewsletter() {
		if (isGenerating) return;
		isGenerating = true;
		const markdown = await generateNewsletterFromChat($promptState.prompt);
		setNewsletterMarkdown(markdown);
		activeView = 'newsletter';
		isGenerating = false;
	}

	// Handle keyboard events
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSendMessage();
		}
	}

	// Scroll to bottom of messages
	function scrollToBottom() {
		setTimeout(() => {
			messagesEnd?.scrollIntoView({ behavior: 'smooth' });
		}, 100);
	}

	// Watch for new messages and scroll
	$: if ($chatState.messages.length > 0) {
		scrollToBottom();
	}

	// Initialize with a welcome message
	onMount(() => {
		addMessage("Hello! I'm your AI recipe assistant. I can help you find recipes, cooking tips, and even generate newsletters from our conversations. What would you like to cook today?", false);
	});
</script>

<svelte:head>
	<title>AI Recipe Assistant + Newsletter Editor</title>
</svelte:head>

<div class="h-screen bg-gray-50 flex">
	<!-- Sidebar -->
	<div class="w-64 bg-white border-r border-gray-200 flex flex-col">
		<!-- Header -->
		<div class="p-6 border-b border-gray-200">
			<h1 class="text-xl font-bold text-gray-900">Recipe Assistant</h1>
			<p class="text-sm text-gray-600 mt-1">AI-powered cooking companion</p>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 p-4 space-y-2">
			<button
				on:click={() => activeView = 'chat'}
				class="w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors duration-200 {activeView === 'chat' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-gray-700 hover:bg-gray-50'}"
			>
				<FontAwesomeIcon icon={faPaperPlane} class="w-5 h-5 mr-3" />
				Chat
			</button>

			<button
				on:click={() => activeView = 'newsletter'}
				class="w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors duration-200 {activeView === 'newsletter' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-gray-700 hover:bg-gray-50'}"
			>
				<FontAwesomeIcon icon={faEnvelope} class="w-5 h-5 mr-3" />
				Newsletter Editor
			</button>

			<button
				on:click={() => activeView = 'prompt'}
				class="w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors duration-200 {activeView === 'prompt' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-gray-700 hover:bg-gray-50'}"
			>
				<svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
				</svg>
				Prompt Settings
			</button>
		</nav>


	</div>

	<!-- Main Content Area -->
	<div class="flex-1 flex flex-col">
		{#if activeView === 'chat'}
			<!-- Chat Interface -->
			<div class="flex-1 flex flex-col bg-white">
				<!-- Chat Header -->
				<div class="border-b border-gray-200 px-6 py-4">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-lg font-semibold text-gray-900">Recipe Chat</h2>
							<p class="text-sm text-gray-600">Ask me about recipes, cooking tips, and more!</p>
						</div>
						<div class="text-sm text-gray-500">
							{$chatState.messages.length} messages
						</div>
					</div>
				</div>

				<!-- Messages Area -->
				<div class="flex-1 overflow-y-auto p-6 space-y-6">
					{#each $chatState.messages as message (message.id)}
						<div class="flex {message.isUser ? 'justify-end' : 'justify-start'}">
							<div class="max-w-2xl {message.isUser ? 'order-2' : 'order-1'}">
								<div class="flex items-start space-x-3">
									{#if !message.isUser}
										<div class="flex-shrink-0">
											<div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
												<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
												</svg>
											</div>
										</div>
									{/if}
									
									<div class="flex-1">
										<div class="bg-gray-50 rounded-2xl px-4 py-3 shadow-sm">
											<div class="prose prose-sm max-w-none">
												{@html marked(message.content)}
											</div>
										</div>
										<div class="mt-2 text-xs text-gray-500">
											{message.timestamp.toLocaleTimeString()}
										</div>
									</div>

									{#if message.isUser}
										<div class="flex-shrink-0">
											<div class="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center">
												<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
												</svg>
											</div>
										</div>
									{/if}
								</div>
							</div>
						</div>
					{/each}

					{#if isSending}
						<div class="flex justify-start">
							<div class="max-w-2xl">
								<div class="flex items-start space-x-3">
									<div class="flex-shrink-0">
										<div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
											<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
											</svg>
										</div>
									</div>
									<div class="flex-1">
										<div class="bg-gray-50 rounded-2xl px-4 py-3 shadow-sm">
											<div class="flex items-center space-x-2">
												<div class="flex space-x-1">
													<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
													<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
													<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
												</div>
												<span class="text-sm text-gray-600">AI is thinking...</span>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					{/if}
					
					<div bind:this={messagesEnd}></div>
				</div>

				<!-- Message Input -->
				<div class="p-6">
					<div class="max-w-4xl mx-auto">
						<div class="relative">
							<textarea
								bind:value={messageInput}
								on:keydown={handleKeydown}
								placeholder="Ask about recipes, cooking tips, or anything food-related..."
								disabled={isSending}
								class="w-full p-4 pr-24 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 shadow-sm"
								rows="2"
							></textarea>
							
							<!-- Action Buttons -->
							<div class="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-3">
								<!-- Generate Newsletter Button -->
								<button
									on:click={handleGenerateNewsletter}
									disabled={isGenerating || $chatState.messages.length === 0}
									class="p-2 text-gray-500 hover:text-blue-600 disabled:text-gray-300 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg cursor-pointer"
									title="Generate Newsletter"
								>
									{#if isGenerating}
										<FontAwesomeIcon icon={faSpinner} class="animate-spin h-6 w-6" />
									{:else}
										<FontAwesomeIcon icon={faEnvelope} class="w-6 h-6" />
									{/if}
								</button>
								
								<!-- Send Message Button -->
								<button
									on:click={handleSendMessage}
									disabled={!messageInput.trim() || isSending}
									class="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer"
									title="Send Message"
								>
									<FontAwesomeIcon icon={faArrowUp} class="w-6 h-6" />
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>

		{:else if activeView === 'newsletter'}
			<!-- Newsletter Editor -->
			<div class="flex-1 flex flex-col bg-white">
				<!-- Newsletter Header -->
				<div class="border-b border-gray-200 px-6 py-4">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-lg font-semibold text-gray-900">Newsletter Editor</h2>
							<p class="text-sm text-gray-600">Edit and preview your generated newsletter</p>
						</div>
						<button
							on:click={() => activeView = 'chat'}
							class="text-gray-600 hover:text-gray-900 transition-colors duration-200"
						>
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
							</svg>
						</button>
					</div>
				</div>

				<!-- Editor Layout -->
				<div class="flex-1 flex">
					<!-- Markdown Editor -->
					<div class="w-1/2 border-r border-gray-200">
						<div class="p-6 h-full">
							<label for="markdown-editor" class="block text-sm font-medium text-gray-700 mb-3">
								Edit Markdown
							</label>
							<textarea
								id="markdown-editor"
								bind:value={$newsletterState.markdown}
								on:input={(e) => updateNewsletterMarkdown(e.currentTarget.value)}
								class="w-full h-full p-4 border border-gray-300 rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="Edit your newsletter markdown here..."
							></textarea>
						</div>
					</div>

					<!-- Preview -->
					<div class="w-1/2">
						<div class="p-6 h-full overflow-y-auto">
							<h3 class="text-sm font-medium text-gray-700 mb-3">Preview</h3>
							<div class="prose prose-sm max-w-none bg-white p-6 rounded-lg border border-gray-200">
								{@html marked($newsletterState.markdown)}
							</div>
						</div>
					</div>
				</div>
			</div>

		{:else if activeView === 'prompt'}
			<!-- Prompt Settings -->
			<div class="flex-1 flex flex-col bg-white">
				<!-- Prompt Header -->
				<div class="border-b border-gray-200 px-6 py-4">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-lg font-semibold text-gray-900">Prompt Settings</h2>
							<p class="text-sm text-gray-600">Customize how newsletters are generated</p>
						</div>
						<button
							on:click={() => activeView = 'chat'}
							class="text-gray-600 hover:text-gray-900 transition-colors duration-200"
						>
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
							</svg>
						</button>
					</div>
				</div>

				<!-- Prompt Editor -->
				<div class="flex-1 p-6">
					<div class="max-w-4xl mx-auto">
						<label for="prompt-editor" class="block text-sm font-medium text-gray-700 mb-3">
							Newsletter Generation Prompt
						</label>
						<textarea
							id="prompt-editor"
							bind:value={$promptState.prompt}
							on:input={(e) => updatePrompt(e.currentTarget.value)}
							class="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="Enter your newsletter generation prompt..."
							style="min-height: 24rem; max-height: 60rem;"
						></textarea>
						<p class="mt-2 text-sm text-gray-600">
							This prompt will be used to generate newsletters from your chat conversations.
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	/* Custom scrollbar */
	::-webkit-scrollbar {
		width: 6px;
	}

	::-webkit-scrollbar-track {
		background: #f1f1f1;
	}

	::-webkit-scrollbar-thumb {
		background: #c1c1c1;
		border-radius: 3px;
	}

	::-webkit-scrollbar-thumb:hover {
		background: #a8a8a8;
	}

	/* Prose styles for markdown */
	:global(.prose) {
		color: #374151;
	}

	:global(.prose h1) {
		font-size: 1.875rem;
		font-weight: 700;
		margin-top: 0;
		margin-bottom: 1rem;
		color: #111827;
	}

	:global(.prose h2) {
		font-size: 1.5rem;
		font-weight: 600;
		margin-top: 2rem;
		margin-bottom: 1rem;
		color: #111827;
	}

	:global(.prose h3) {
		font-size: 1.25rem;
		font-weight: 600;
		margin-top: 1.5rem;
		margin-bottom: 0.5rem;
		color: #111827;
	}

	:global(.prose p) {
		margin-bottom: 1rem;
		line-height: 1.6;
	}

	:global(.prose ul) {
		margin-bottom: 1rem;
		padding-left: 1.5rem;
	}

	:global(.prose li) {
		margin-bottom: 0.25rem;
	}

	:global(.prose table) {
		width: 100%;
		border-collapse: collapse;
		margin-bottom: 1rem;
	}

	:global(.prose th),
	:global(.prose td) {
		border: 1px solid #d1d5db;
		padding: 0.5rem;
		text-align: left;
	}

	:global(.prose th) {
		background-color: #f9fafb;
		font-weight: 600;
	}

	:global(.prose strong) {
		font-weight: 600;
		color: #111827;
	}

	:global(.prose em) {
		font-style: italic;
	}

	:global(.prose hr) {
		border: none;
		border-top: 1px solid #d1d5db;
		margin: 2rem 0;
	}

	:global(.prose a) {
		color: #2563eb;
		text-decoration: underline;
	}

	:global(.prose a:hover) {
		color: #1d4ed8;
	}

	:global(.prose code) {
		background-color: #f3f4f6;
		padding: 0.125rem 0.25rem;
		border-radius: 0.25rem;
		font-size: 0.875em;
	}

	:global(.prose pre) {
		background-color: #1f2937;
		color: #f9fafb;
		padding: 1rem;
		border-radius: 0.5rem;
		overflow-x: auto;
	}

	:global(.prose pre code) {
		background-color: transparent;
		padding: 0;
		color: inherit;
	}
</style>
