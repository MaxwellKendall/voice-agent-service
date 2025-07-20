import { addMessage, currentChatIdState, currentPromptState, currentNewsletterState, messagesState, setPromptIsEditing, setNewsletterIsSaving, updateChat } from './stores.js';
import { get } from 'svelte/store';
import debounce from 'lodash.debounce';

const API_BASE_URL = 'http://localhost:8000';
const DEBOUNCE_INTERVAL = 1500;

// Real API call to chat endpoint
export async function sendChatMessage(message: string, prompt?: string): Promise<{response: string, chat_id: string, recipes?: any[], tool_calls?: any[]}> {
	try {
		const chatId = get(currentChatIdState);
		const requestBody: any = {
			message,
			chat_id: chatId
		};
		
		// Include prompt if provided (for first message) or if no chatId (new chat)
		if (prompt || !chatId) {
			requestBody.prompt = prompt || get(currentPromptState);
		}
		
		const response = await fetch(`${API_BASE_URL}/chat`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(requestBody)
		});

		if (!response.ok) {
			throw new Error(`API request failed: ${response.status} ${response.statusText}`);
		}

		const data = await response.json();
		return data;
	} catch (error) {
		console.error('Error calling chat API:', error);
		// Fallback to mock response if API is unavailable
		return {
			response: "I'm having trouble connecting to my services right now. Please try again later.",
			recipes: [],
			tool_calls: [],
			chat_id: '',
		};
	}
}

// Update chat prompt
export async function updateChatPrompt(chatId: string, prompt: string): Promise<boolean> {
	try {
		const response = await fetch(`${API_BASE_URL}/chats/${chatId}/prompt`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ prompt })
		});

		if (!response.ok) {
			throw new Error(`API request failed: ${response.status} ${response.statusText}`);
		}

		return true;
	} catch (error) {
		console.error('Error updating chat prompt:', error);
		return false;
	} finally {
		setPromptIsEditing(false);
	}
}

// Update chat newsletter
export async function updateChatNewsletter(chatId: string, newsletter: string): Promise<boolean> {
	try {
		const response = await fetch(`${API_BASE_URL}/chats/${chatId}/newsletter`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ newsletter })
		});

		if (!response.ok) {
			throw new Error(`API request failed: ${response.status} ${response.statusText}`);
		}

		return true;
	} catch (error) {
		console.error('Error updating chat newsletter:', error);
		return false;
	} finally {
		setNewsletterIsSaving(false);
	}
}

// Debounced network calls only
const debouncedSavePrompt = debounce(async (chatId: string, prompt: string) => {
	await updateChatPrompt(chatId, prompt);
}, DEBOUNCE_INTERVAL);

const debouncedSaveNewsletter = debounce(async (chatId: string, newsletter: string) => {
	await updateChatNewsletter(chatId, newsletter);
}, DEBOUNCE_INTERVAL);

// Simple functions to update local state and trigger debounced save
export function updatePromptWithDebounce(prompt: string) {
	const chatId = get(currentChatIdState);
	if (chatId) {
		debouncedSavePrompt(chatId, prompt);
	}
}

export function updateNewsletterWithDebounce(newsletter: string) {
	const chatId = get(currentChatIdState);
	if (chatId) {
		debouncedSaveNewsletter(chatId, newsletter);
	}
}

// Load chat history
export async function loadChatHistory(): Promise<any[]> {
	try {
		const response = await fetch(`${API_BASE_URL}/chats`);
		
		if (!response.ok) {
			throw new Error(`API request failed: ${response.status} ${response.statusText}`);
		}
		
		const data = await response.json();
		return data.chats || [];
	} catch (error) {
		console.error('Error loading chat history:', error);
		return [];
	}
}

// Load specific chat
export async function loadChat(chatId: string): Promise<{messages: any[], prompt?: string, newsletter?: string} | null> {
	try {
		const response = await fetch(`${API_BASE_URL}/chats/${chatId}`);
		
		if (!response.ok) {
			throw new Error(`API request failed: ${response.status} ${response.statusText}`);
		}
		
		const data = await response.json();
		return data;
	} catch (error) {
		console.error('Error loading chat:', error);
		return null;
	}
}

// Generate newsletter by asking the AI to create one from the conversation
export async function generateNewsletterFromChat(prompt: string): Promise<string> {
	try {
		const response = await sendChatMessage(prompt);
		
		// Handle newline characters properly
		return response.response.replace(/\\n/g, '\n');
	} catch (error) {
		console.error('Error generating newsletter from chat:', error);
		// Fallback to mock newsletter if API is unavailable
		return await generateNewsletterMarkdown();
	}
}

// Helper function to send a message and get AI response
export async function sendMessageAndGetResponse(content: string) {
	// Add user message to store first (so UI updates immediately)
	addMessage(content, true);
	
	// Check if this is the first message (no chatId or no messages)
	const currentChatId = get(currentChatIdState);
	const currentMessages = get(messagesState);
	const isFirstMessage = !currentChatId || currentMessages.length === 0;
	
	// Get current prompt for first message
	const currentPrompt = get(currentPromptState);
	
	// Get AI response from API with updated chat history
	const apiResponse = await sendChatMessage(content, isFirstMessage ? currentPrompt : undefined);

	// Update chat ID if we get a new one (for new chats)
	if (apiResponse.chat_id) {
		currentChatIdState.set(apiResponse.chat_id);
	}
	
	// Add AI response to the store
	addMessage(apiResponse.response, false);
	
	return apiResponse;
}

// Fallback mock newsletter generation function (kept for API fallback)
async function generateNewsletterMarkdown(): Promise<string> {
	// Simulate processing time
	await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));
	
	return `# Weekly Recipe Newsletter

## 📰 Top Stories This Week

### 1. Industry Insights
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

### 2. Technology Updates
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

### 3. Market Analysis
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

## 🎯 Key Takeaways

- **Point 1**: Important insight about the industry
- **Point 2**: Notable technological advancement
- **Point 3**: Market trend to watch

## 📊 Data Highlights

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|---------|
| Engagement | 85% | 78% | +7% |
| Reach | 12.5K | 11.2K | +11.6% |
| Conversion | 3.2% | 2.8% | +14.3% |

## 🔮 Looking Ahead

Next week, we expect to see continued growth in the sector, with particular focus on emerging technologies and market opportunities.

---

*Generated on ${new Date().toLocaleDateString()}*
*Edit this content to match your specific needs and audience.*`;
} 