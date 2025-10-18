# LLM Session Manager - Frontend

React frontend for real-time collaborative sessions.

## Features

- Real-time WebSocket communication
- Multi-user presence tracking
- Live chat and code comments
- Cursor position synchronization
- Role-based permissions (Host/Editor/Viewer)
- Beautiful dark-mode UI with TailwindCSS

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at: http://localhost:3000

### 3. Backend Requirement

Make sure the backend is running on port 8000:

```bash
cd ../backend
uvicorn app.main:app --reload
```

## Usage

### Create a Session

1. Go to http://localhost:3000
2. Click "Create New Session"
3. Enter your username and JWT token
4. Share the session ID with collaborators

### Join a Session

1. Get the session ID from the host
2. Go to http://localhost:3000
3. Click "Join Session" and enter the session ID
4. Enter your username and JWT token

### Authentication

You need a JWT token from the backend. Generate one using:

```python
# In backend directory
python generate_token.py --username "YourName"
```

Or use the test token generation script from TESTING_GUIDE.md.

## Components

### `CollaborativeSession`
Main session page with all collaborative features.

### `PresenceBar`
Shows all active participants with their status and role.

### `ChatPanel`
Real-time chat interface with code comment support.

### `MessageBubble`
Individual message display with reactions and metadata.

### `CursorIndicator`
Shows where other users' cursors are positioned.

### `useWebSocket` Hook
Custom hook for WebSocket connection management with auto-reconnect.

## WebSocket Messages

The frontend handles these message types:

**Outgoing:**
- `chat_message` - Send chat message
- `cursor_update` - Update cursor position
- `viewport_update` - Update viewport
- `presence_update` - Update status
- `code_comment` - Add code comment
- `reaction` - Add emoji reaction

**Incoming:**
- `connected` - Welcome message with participants
- `user_joined` - New user joined
- `user_left` - User disconnected
- `chat_message` - Chat message received
- `code_comment` - Code comment received
- `cursor_update` - User cursor moved
- `presence_update` - User status changed
- `reaction_update` - Reactions updated
- `error` - Error message

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatPanel.jsx
│   │   ├── CursorIndicator.jsx
│   │   ├── MessageBubble.jsx
│   │   └── PresenceBar.jsx
│   ├── hooks/               # Custom React hooks
│   │   └── useWebSocket.js
│   ├── pages/               # Page components
│   │   ├── CollaborativeSession.jsx
│   │   └── Home.jsx
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # App entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment

The app uses Vite's proxy to forward API requests to the backend:

- `/api/*` → `http://localhost:8000/api/*`
- `/ws/*` → `ws://localhost:8000/ws/*`

Configure in `vite.config.js` if backend runs on a different port.

## Styling

Using TailwindCSS with custom configuration:

- Dark mode theme
- Custom color palette (primary blue)
- Utility classes for cards, buttons, inputs
- Responsive grid layouts

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- WebSocket support required
- JavaScript enabled

## Troubleshooting

### WebSocket Connection Failed

1. Check backend is running on port 8000
2. Verify JWT token is valid
3. Check browser console for errors
4. Try clearing localStorage and rejoining

### Cannot See Other Users

1. Ensure all users have valid tokens
2. Check all users are in the same session ID
3. Verify backend WebSocket endpoint is working
4. Check network tab for WebSocket messages

### Messages Not Sending

1. Check WebSocket connection status (green dot)
2. Verify you have Editor or Host role (not Viewer)
3. Check message input is not empty
4. Look for error notifications

## Next Steps

- [ ] Add file viewer with syntax highlighting
- [ ] Implement operational transforms for collaborative editing
- [ ] Add voice/video chat
- [ ] Session recording and playback
- [ ] AI-powered code suggestions
- [ ] Integration with VS Code extension

## License

MIT
