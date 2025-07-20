<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { marked } from 'marked';

	// Override link renderer to add target="_blank" and rel="noopener noreferrer"
	const renderer = {
		link({ href, title, text }: { href: string; title?: string | null; text: string }) {
			return `<a href="${href}" target="_blank" rel="noopener noreferrer" title="${title || ''}">${text}</a>`;
		}
	};

	marked.use({ renderer });
	import { 
		chatsState, 
		messagesState,
		currentChatIdState,
		currentPromptState,
		currentNewsletterState,
		promptIsEditingState,
		newsletterIsSavingState,
		chatHistoryForAPI,
		addMessage, 
		setMessages,
		clearMessages,
		setChats,
		setCurrentChatId,
		setCurrentPrompt,
		setCurrentNewsletter,
		setPromptIsEditing,
		setNewsletterIsSaving,
		type ChatInfo
	} from '$lib/stores.js';
	import { generateNewsletterFromChat, sendMessageAndGetResponse, loadChatHistory, loadChat, updateChatPrompt, updateChatNewsletter, updatePromptWithDebounce, updateNewsletterWithDebounce } from '$lib/utils.js';
	
	const API_BASE_URL = 'http://localhost:8000';
	import { FontAwesomeIcon } from '@fortawesome/svelte-fontawesome';
	import { faPaperPlane, faEnvelope, faSpinner, faArrowUp } from '@fortawesome/free-solid-svg-icons';

	let messageInput = '';
	let isGenerating = false;
	let isSending = false;
	let activeView = 'chat'; // 'chat' | 'newsletter' | 'prompt'
	let messagesEnd: HTMLElement;
	let chatHistory: ChatInfo[] = [];
	let isLoadingChats = false;

	// Handle sending a message
	async function handleSendMessage() {
		if (!messageInput.trim() || isSending) return;
		
		const messageToSend = messageInput.trim();
		messageInput = ''; // Clear input immediately for better UX
		
		isSending = true;
		await sendMessageAndGetResponse(messageToSend);
		isSending = false;
		
		// Refresh chat history to show the updated chat
		loadChatHistoryData();
	}

	// Handle generating newsletter
	async function handleGenerateNewsletter() {
		if (isGenerating) return;
		isGenerating = true;
		
		try {
			const markdown = await generateNewsletterFromChat($currentPromptState);
			setCurrentNewsletter(markdown);
			activeView = 'newsletter';
			
			// Save newsletter to current chat immediately after generation
			if ($currentChatIdState) {
				await updateChatNewsletter($currentChatIdState, markdown);
			}
		} catch (error) {
			console.error('Error generating newsletter:', error);
		} finally {
			isGenerating = false;
		}
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
	$: if ($messagesState.length > 0) {
		scrollToBottom();
	}

	// Load chat history
	async function loadChatHistoryData() {
		isLoadingChats = true;
		try {
			const chats = await loadChatHistory();
			setChats(chats);
			chatHistory = chats;
			
			// If we have a selected chat, ensure its prompt is loaded
			const currentChatId = get(currentChatIdState);
			if (currentChatId) {
				loadPromptForChat(currentChatId);
			}
		} catch (error) {
			console.error('Error loading chat history:', error);
		} finally {
			isLoadingChats = false;
		}
	}

	// Helper function to load prompt and newsletter for a chat
	function loadPromptForChat(chatId: string) {
		const chats = get(chatsState);
		const selectedChat = chats.find((chat: ChatInfo) => chat.id === chatId);
		if (selectedChat) {
			if (selectedChat.prompt) {
				setCurrentPrompt(selectedChat.prompt);
			}
			if (selectedChat.newsletter) {
				setCurrentNewsletter(selectedChat.newsletter);
			}
		}
	}

	// Load a specific chat
	async function loadChatData(chatId: string) {
		try {
			const chatData = await loadChat(chatId);
			if (chatData) {
				// Clear current messages
				clearMessages();
				
				// Load messages from the selected chat
				if (chatData.messages) {				
					chatData.messages.forEach((msg: any) => {
						addMessage(msg.content, msg.role === 'user');
					});
				}
				
				// Update chat ID
				setCurrentChatId(chatId);
				
				// Set prompt and newsletter from chat if available, otherwise try chat history
				if (chatData.prompt || chatData.newsletter) {
					if (chatData.prompt) {
						setCurrentPrompt(chatData.prompt);
					}
					if (chatData.newsletter) {
						setCurrentNewsletter(chatData.newsletter);
					}
				} else {
					loadPromptForChat(chatId);
				}
			}
		} catch (error) {
			console.error('Error loading chat:', error);
		}
	}

	// Handle prompt changes with debouncing
	function handlePromptChange(event: Event) {
		const target = event.target as HTMLTextAreaElement;
		const newPrompt = target.value;
		setCurrentPrompt(newPrompt);
		setPromptIsEditing(true);

		updatePromptWithDebounce(newPrompt);
	}

	// Handle newsletter changes with debouncing
	function handleNewsletterChange(event: Event) {
		const target = event.target as HTMLTextAreaElement;
		const newNewsletter = target.value;
		setCurrentNewsletter(newNewsletter);
		setNewsletterIsSaving(true);

		updateNewsletterWithDebounce(newNewsletter);
	}

	// Initialize with a welcome message and load chat history
	onMount(() => {
		addMessage("Hello! I'm your AI recipe assistant. I can help you find recipes, cooking tips, and even generate newsletters from our conversations. What would you like to cook today?", false);
		loadChatHistoryData();
	});
</script>

<svelte:head>
	<title>AI Recipe Assistant + Newsletter Editor</title>
</svelte:head>

<div class="h-screen bg-gray-50 flex">
	<!-- Sidebar -->
	<div class="w-64 bg-white border-r border-gray-200 flex flex-col fixed left-0 top-0 h-full overflow-y-auto">
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

			<!-- Chat History -->
			<div class="mt-4 h-full">
				<div class="flex items-center justify-between mb-3">
					<h3 class="text-sm font-medium text-gray-700">Chat History</h3>
					<button
						on:click={loadChatHistoryData}
						disabled={isLoadingChats}
						class="text-gray-400 hover:text-gray-600 transition-colors duration-200"
						title="Refresh chat history"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
						</svg>
					</button>
				</div>
				
				{#if isLoadingChats}
					<div class="flex justify-center py-4">
						<FontAwesomeIcon icon={faSpinner} class="animate-spin h-4 w-4 text-gray-400" />
					</div>
				{:else if chatHistory.length === 0}
					<p class="text-xs text-gray-500 text-center py-4">No previous chats</p>
				{:else}
					<div class="space-y-2 overflow-y-auto">
						{#each chatHistory as chat (chat.id)}
							<button
								on:click={() => loadChatData(chat.id)}
								class="w-full text-left p-2 rounded-lg hover:bg-gray-50 transition-colors duration-200 cursor-pointer {chat.id === $currentChatIdState ? 'bg-blue-50 border border-blue-200' : ''}"
							>
								<div class="text-sm font-medium text-gray-900 truncate">{chat.title}</div>
								<div class="text-xs text-gray-500 mt-1">
									{new Date(chat.updated_at).toLocaleDateString()} • {chat.message_count} messages
								</div>
							</button>
						{/each}
					</div>
				{/if}
			</div>
		</nav>


	</div>

	<!-- Main Content Area -->
	<div class="flex-1 flex flex-col ml-64">
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
							{$messagesState.length} messages
						</div>
					</div>
				</div>

				<!-- Messages Area -->
				<div class="flex-1 overflow-y-auto p-6 space-y-6">
					{#each $messagesState as message (message.id)}
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
									disabled={isGenerating || get(messagesState).length === 0}
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
							{#if $newsletterIsSavingState}
								<div class="flex items-center text-sm text-blue-600 mt-1">
									<FontAwesomeIcon icon={faSpinner} class="animate-spin h-4 w-4 mr-2" />
									Saving...
								</div>
							{/if}
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
								bind:value={$currentNewsletterState}
								on:input={handleNewsletterChange}
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
								{@html marked($currentNewsletterState)}
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
							bind:value={$currentPromptState}
							on:input={handlePromptChange}
							class="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							placeholder="Enter your newsletter generation prompt..."
							style="min-height: 24rem; max-height: 60rem;"
						></textarea>
						<div class="mt-2 flex items-center justify-between">
							<p class="text-sm text-gray-600">
								This prompt will be used to generate newsletters from your chat conversations.
							</p>
							{#if $promptIsEditingState}
								<div class="flex items-center text-sm text-blue-600">
									<FontAwesomeIcon icon={faSpinner} class="animate-spin h-4 w-4 mr-2" />
									Saving...
								</div>
							{/if}
						</div>
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
