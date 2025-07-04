# AI Recipe Assistant + Newsletter Editor

A modern SvelteKit application that combines an AI recipe assistant with a newsletter editor, built with TypeScript and Tailwind CSS. The app integrates with a backend API to provide intelligent recipe recommendations and generate newsletters through conversation.

## ✨ Features

### AI Recipe Assistant
- **Real-time recipe chat** with AI-powered responses
- **Recipe search and recommendations** via backend API
- **Cooking tips and advice** from the AI assistant
- **Newsletter-focused conversations** that build comprehensive content
- **Message history** with timestamps
- **Loading states** with typing indicators
- **Keyboard shortcuts** (Enter to send, Shift+Enter for new line)

### Newsletter Editor
- **AI-generated newsletters** from chat conversations
- **Markdown editing** with live preview
- **Split-screen layout** (editor on left, preview on right)
- **Conversation-driven content** that builds naturally through chat
- **Easy navigation** between chat and editor modes

### Technical Features
- **SvelteKit** for modern web development
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Svelte stores** for state management
- **Marked.js** for Markdown rendering
- **Backend API integration** for intelligent responses
- **Error handling** with fallback responses
- **Accessibility** focused design

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Backend API server running on `http://localhost:8000`

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd webapp
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

## 🔌 API Integration

The application integrates with a backend API that provides:

### Endpoints Used
- `POST /chat` - Send messages and receive AI responses with recipe recommendations and newsletter generation

### API Configuration
The API base URL is configured in `src/lib/utils.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

### Request/Response Format
- **Chat messages** include conversation history in the format expected by the API
- **Newsletter generation** happens through the chat endpoint with a specific prompt
- **Error handling** provides fallback responses when the API is unavailable

## 📁 Project Structure

```
src/
├── lib/
│   ├── stores.ts      # Svelte stores for state management
│   └── utils.ts       # API integration and utility functions
├── routes/
│   └── +page.svelte   # Main application component
└── app.css           # Global styles with Tailwind CSS
```

## 🎯 Usage

### Chat with AI Recipe Assistant
1. Type your recipe question in the input field
2. Press Enter or click "Send" to submit
3. Receive AI-powered responses with recipe recommendations
4. Continue the conversation to build context for newsletter generation
5. The AI is designed to guide conversations toward newsletter content

### Generate Newsletter
1. Have a conversation with the AI about recipes and cooking
2. Click the "Generate Newsletter" button (top-right)
3. The AI will analyze your conversation and generate markdown content
4. Edit the content in the left panel
5. See live preview in the right panel
6. Click "Back to Chat" to return to conversation mode

### Example Conversations
- "What are some easy Mexican recipes?"
- "How do I make guacamole?"
- "Show me vegetarian pasta dishes"
- "What's a good substitute for buttermilk?"
- "Tell me about current cooking trends"

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run check` - Type check with svelte-check
- `npm run lint` - Run ESLint and Prettier
- `npm run format` - Format code with Prettier
- `npm run test` - Run unit tests

### Key Technologies

- **SvelteKit** - Full-stack web framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Marked.js** - Markdown parser and compiler
- **Fetch API** - HTTP requests to backend
- **Vite** - Fast build tool and dev server

## 🎨 Customization

### API Configuration
Edit `src/lib/utils.ts` to customize:
- API base URL
- Request/response handling
- Error fallback responses
- Newsletter generation prompt

### Styling
The application uses Tailwind CSS for styling. You can customize the design by:
- Modifying the Tailwind classes in the Svelte components
- Updating the `tailwind.config.js` file
- Adding custom CSS in the `<style>` blocks

### State Management
The application uses Svelte stores for state management:
- `chatMessages` - Stores conversation history
- `newsletterState` - Manages newsletter editing state
- `chatHistoryForAPI` - Derived store for API-compatible format

## 🔧 API Contract

The application expects the backend API to follow this contract:

### POST /chat
```json
{
  "message": "What are some easy Mexican recipes?",
  "chat_history": [
    {"role": "user", "content": "I want Mexican food"},
    {"role": "assistant", "content": "I can help you find Mexican recipes!"}
  ]
}
```

**Response:**
```json
{
  "response": "I found several delicious Mexican recipes for you! Here are some easy options:\n\n1. **Chicken Enchiladas** - A classic Mexican dish...",
  "recipes": [
    {
      "id": "recipe_001",
      "title": "Easy Chicken Enchiladas", 
      "summary": "Classic Mexican enchiladas with tender chicken",
      "url": "https://example.com/recipes/chicken-enchiladas",
      "score": 0.92
    }
  ],
  "tool_calls": [
    {
      "tool_name": "search_recipes",
      "arguments": {"query": "easy Mexican recipes"},
      "result": "Found 5 recipes matching criteria"
    }
  ]
}
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

---

Built with ❤️ using SvelteKit and AI-powered recipe assistance
