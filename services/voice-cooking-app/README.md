# Voice Cooking App

A Progressive Web App (PWA) that provides hands-free cooking assistance using voice commands. Users can paste recipe URLs, view extracted recipe information, and interact with an AI assistant through voice commands during cooking.

## Features

- 🎤 **Voice Recognition**: Real-time speech-to-text using Web Speech API
- 🤖 **AI Assistant**: Context-aware recipe assistance with OpenAI
- 📱 **Progressive Web App**: Installable on mobile, tablet, and desktop
- 🔐 **Authentication**: Google OAuth via Supabase
- 📊 **Recipe Display**: Clean UI for viewing recipe steps and ingredients
- 🔄 **Real-time Communication**: WebSocket-based voice interaction
- 🎨 **Responsive Design**: Optimized for mobile, tablet, and desktop
- 📐 **Cross-Device**: Seamless experience across all screen sizes

## Tech Stack

- **Frontend**: React 18 with Vite
- **Styling**: Tailwind CSS with responsive design
- **Authentication**: Supabase Auth with Google OAuth
- **Database**: Supabase PostgreSQL
- **Voice Recognition**: Web Speech API
- **AI Integration**: OpenAI API
- **Real-time**: WebSocket communication
- **PWA**: Vite PWA plugin with service worker

## Responsive Design

The app is designed to work perfectly across all devices:

- **Mobile (320px+)**: Touch-optimized interface with large buttons and readable text
- **Tablet (768px+)**: Enhanced layout with more content visible and better navigation
- **Desktop (1024px+)**: Full-featured interface with additional features and larger content areas

### Responsive Features:
- Adaptive typography that scales with screen size
- Touch-friendly buttons (minimum 44px) for mobile devices
- Flexible grid layouts that adapt to screen width
- Optimized spacing and padding for each device type
- PWA features that work across all platforms

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Supabase account
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd voice-cooking-app
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp env.example .env
```

Edit `.env` and add your API keys:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_OPENAI_API_KEY=your_openai_api_key
VITE_RECIPE_API_URL=your_recipe_extraction_api_url
```

4. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components
├── hooks/         # Custom React hooks
├── utils/         # Utility functions
├── contexts/      # React contexts
├── services/      # API and external service integrations
└── assets/        # Static assets
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### PWA Features

- Service worker for offline functionality
- App manifest for installability
- Responsive design for all screen sizes
- Touch-optimized interface
- Cross-platform compatibility

### Responsive Testing

Test the app across different screen sizes:
- Mobile: 320px - 767px
- Tablet: 768px - 1023px  
- Desktop: 1024px+

Use browser dev tools to test responsive behavior and ensure the app works well on all devices.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test across different screen sizes
5. Add tests if applicable
6. Submit a pull request

## License

MIT License - see LICENSE file for details
