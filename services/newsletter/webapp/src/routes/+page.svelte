<script lang="ts">
	import { onMount } from 'svelte';
	import { marked } from 'marked';
	import { 
		chatMessages, 
		newsletterState, 
		chatHistoryForAPI,
		addMessage, 
		setNewsletterMarkdown, 
		updateNewsletterMarkdown, 
		resetToChat 
	} from '$lib/stores.js';
	import { generateNewsletterFromChat, sendMessageAndGetResponse } from '$lib/utils.js';

	let messageInput = '';
	let isGenerating = false;
	let isSending = false;

	// Handle sending a message
	async function handleSendMessage() {
		if (!messageInput.trim() || isSending) return;
		
		const messageToSend = messageInput.trim();
		messageInput = ''; // Clear input immediately for better UX
		
		isSending = true;
		const chatHistory = $chatHistoryForAPI;
		await sendMessageAndGetResponse(messageToSend, chatHistory);
		isSending = false;
	}

	// Handle generating newsletter
	async function handleGenerateNewsletter() {
		if (isGenerating) return;
		
		isGenerating = true;
		const chatHistory = $chatHistoryForAPI;
		const markdown = await generateNewsletterFromChat(chatHistory);
		setNewsletterMarkdown(markdown);
		isGenerating = false;
	}

	// Handle keyboard events
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSendMessage();
		}
	}

	// Initialize with a welcome message
	onMount(() => {
		addMessage("Hello! I'm your AI recipe assistant. I can help you find recipes, cooking tips, and even generate newsletters from our conversations. What would you like to cook today?", false);
	});
</script>

<svelte:head>
	<title>AI Recipe Assistant + Newsletter Editor</title>
</svelte:head>

<main class="min-h-screen bg-gray-50">
	<!-- Generate Newsletter Button (Fixed Position) -->
	<div class="fixed top-4 right-4 z-50">
		<button
			on:click={handleGenerateNewsletter}
			disabled={isGenerating}
			class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium shadow-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
		>
			{#if isGenerating}
				Generating...
			{:else}
				Generate Newsletter
			{/if}
		</button>
	</div>

	<!-- Main Content -->
	<div class="container mx-auto px-4 py-8 max-w-6xl">
		{#if $newsletterState.isEditing}
			<!-- Newsletter Editor View -->
			<div class="bg-white rounded-lg shadow-lg overflow-hidden">
				<!-- Header -->
				<div class="bg-gray-800 text-white px-6 py-4 flex justify-between items-center">
					<h1 class="text-xl font-semibold">Recipe Newsletter Editor</h1>
					<button
						on:click={resetToChat}
						class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
					>
						Back to Chat
					</button>
				</div>

				<!-- Editor Layout -->
				<div class="flex h-[calc(100vh-200px)]">
					<!-- Markdown Editor -->
					<div class="w-1/2 border-r border-gray-200">
						<div class="p-4 h-full">
							<label for="markdown-editor" class="block text-sm font-medium text-gray-700 mb-2">
								Edit Markdown
							</label>
							<textarea
								id="markdown-editor"
								bind:value={$newsletterState.markdown}
								on:input={(e) => updateNewsletterMarkdown(e.currentTarget.value)}
								class="w-full h-full p-4 border border-gray-300 rounded-md font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="Edit your newsletter markdown here..."
							></textarea>
						</div>
					</div>

					<!-- Preview -->
					<div class="w-1/2">
						<div class="p-4 h-full overflow-y-auto">
							<h3 class="text-sm font-medium text-gray-700 mb-2">Preview</h3>
							<div class="prose prose-sm max-w-none">
								{@html marked($newsletterState.markdown)}
							</div>
						</div>
					</div>
				</div>
			</div>
		{:else}
			<!-- Chat Interface -->
			<div class="bg-white rounded-lg shadow-lg overflow-hidden h-[calc(100vh-200px)] flex flex-col">
				<!-- Chat Header -->
				<div class="bg-gray-800 text-white px-6 py-4">
					<h1 class="text-xl font-semibold">AI Recipe Assistant</h1>
					<p class="text-sm text-gray-300 mt-1">Ask me about recipes, cooking tips, and more!</p>
				</div>

				<!-- Messages Area -->
				<div class="flex-1 overflow-y-auto p-4 space-y-4">
					{#each $chatMessages as message (message.id)}
						<div class="flex {message.isUser ? 'justify-end' : 'justify-start'}">
							<div class="max-w-[70%]">
								<div class="px-4 py-2 rounded-lg {message.isUser ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}">
									<p class="text-sm whitespace-pre-wrap">{message.content}</p>
									<p class="text-xs mt-1 opacity-70">
										{message.timestamp.toLocaleTimeString()}
									</p>
								</div>
							</div>
						</div>
					{/each}

					{#if isSending}
						<div class="flex justify-start">
							<div class="max-w-[70%]">
								<div class="px-4 py-2 rounded-lg bg-gray-200 text-gray-800">
									<div class="flex items-center space-x-2">
										<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
										<span class="text-sm">AI is typing...</span>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>

				<!-- Message Input -->
				<div class="border-t border-gray-200 p-4">
					<div class="flex space-x-2">
						<textarea
							bind:value={messageInput}
							on:keydown={handleKeydown}
							placeholder="Ask about recipes, cooking tips, or anything food-related..."
							disabled={isSending}
							class="flex-1 p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
							rows="2"
						></textarea>
						<button
							on:click={handleSendMessage}
							disabled={!messageInput.trim() || isSending}
							class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-md font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 self-end"
						>
							Send
						</button>
					</div>
				</div>
			</div>
		{/if}
	</div>
</main>

<style>
	/* Custom scrollbar for better UX */
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

	/* Prose styles for markdown preview */
	:global(.prose) {
		color: #374151;
	}

	:global(.prose h1) {
		font-size: 1.875rem;
		font-weight: 700;
		margin-top: 0;
		margin-bottom: 1rem;
	}

	:global(.prose h2) {
		font-size: 1.5rem;
		font-weight: 600;
		margin-top: 2rem;
		margin-bottom: 1rem;
	}

	:global(.prose h3) {
		font-size: 1.25rem;
		font-weight: 600;
		margin-top: 1.5rem;
		margin-bottom: 0.5rem;
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
	}

	:global(.prose em) {
		font-style: italic;
	}

	:global(.prose hr) {
		border: none;
		border-top: 1px solid #d1d5db;
		margin: 2rem 0;
	}
</style>
