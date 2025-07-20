import { writable, derived, get } from 'svelte/store';

export interface ChatMessage {
	id: string;
	content: string;
	isUser: boolean;
	timestamp: Date;
}

export interface ChatInfo {
	id: string;
	title: string;
	prompt?: string;
	newsletter?: string;
	created_at: string;
	updated_at: string;
	message_count: number;
}

// Chats store - array of all chats
export const chatsState = writable<ChatInfo[]>([]);

// Messages store - array of messages for the current chat
export const messagesState = writable<ChatMessage[]>([]);

// Current chat ID
export const currentChatIdState = writable<string>('');

// Current prompt and newsletter for the selected chat
export const currentPromptState = writable<string>(`You are an expert recipe curator for families writing a weekly newsletter called "The Family Table." Our target persona is a mom cooking for her family. We proactively give recipes every week without her trying. Every recipe is highly rated. Most mom's probably have a good "routine" number of meals, and we want to add to that repitore as much as possible.

RULES:

Keep the formatting clean and scannable.

Recipes are represented very concisely with the following format:

## [Recipe Title](link)

- Servings

- <Estimated total cost per serving> 💸

- Main ingredients 🍗 / :steak-emoji: whatever

We choose recipes based on the season: right now, its the middle of summer

The newsletter should have a clear "intro", "recipes" and "conclusion" but these sections should not be marked by headers of the same name.

Use emojis to help distinguish recipes: good for kids, money saver, crowd pleaser (good for hospitality) etc...

Recipes are already curated and provided in a structured format (title, ingredients, effort level, tools needed, etc.). Your job is to transform that data into a delightful newsletter.`);

export const currentNewsletterState = writable<string>('');

// UI state
export const promptIsEditingState = writable<boolean>(false);
export const newsletterIsSavingState = writable<boolean>(false);

// Derived store for API-compatible chat history
export const chatHistoryForAPI = derived(messagesState, ($messagesState) => {
	return $messagesState.map(message => ({
		role: message.isUser ? 'user' : 'assistant',
		content: message.content
	}));
});

// Helper functions
export function addMessage(content: string, isUser: boolean) {
	const message: ChatMessage = {
		id: crypto.randomUUID(),
		content,
		isUser,
		timestamp: new Date()
	};
	
	messagesState.update(messages => [...messages, message]);
}

export function setMessages(messages: ChatMessage[]) {
	messagesState.set(messages);
}

export function clearMessages() {
	messagesState.set([]);
}

export function setChats(chats: ChatInfo[]) {
	chatsState.set(chats);
}

export function setCurrentChatId(chatId: string) {
	currentChatIdState.set(chatId);
}

export function setCurrentPrompt(prompt: string) {
	currentPromptState.set(prompt);
}

export function setCurrentNewsletter(newsletter: string) {
	currentNewsletterState.set(newsletter);
}

export function setPromptIsEditing(isEditing: boolean) {
	promptIsEditingState.set(isEditing);
}

export function setNewsletterIsSaving(isSaving: boolean) {
	newsletterIsSavingState.set(isSaving);
}

// Get current chat info
export function getCurrentChat(): ChatInfo | undefined {
	const chats = get(chatsState);
	const currentChatId = get(currentChatIdState);
	return chats.find(chat => chat.id === currentChatId);
}

// Update chat in the chats array
export function updateChat(chatId: string, updates: Partial<ChatInfo>) {
	chatsState.update(chats => 
		chats.map(chat => 
			chat.id === chatId ? { ...chat, ...updates } : chat
		)
	);
} 