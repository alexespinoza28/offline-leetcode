# Interview Coding Platform - Frontend

A React-based web application for the Interview Coding Platform, providing an interactive coding environment with problem solving, code execution, and real-time feedback.

## Architecture Overview

The frontend is built with React and TypeScript, featuring a modern component-based architecture with comprehensive type safety and robust error handling.

### Key Features

- **Interactive Code Editor**: Monaco Editor integration with syntax highlighting and language support
- **Real-time Code Execution**: Direct communication with the Python orchestrator backend
- **Problem Management**: Browse and solve coding problems with detailed descriptions and examples
- **Multi-language Support**: Python, C++, C, JavaScript, and Java
- **Offline Functionality**: Local solution caching and offline problem browsing
- **Responsive Design**: Modern UI with dark/light theme support
- **Connection Management**: Automatic reconnection and network status monitoring

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── CodeEditor.tsx        # Monaco editor wrapper
│   │   ├── ConnectionStatus.tsx  # Network status indicator
│   │   ├── ControlBar.tsx        # Action buttons and controls
│   │   ├── EditorSettings.tsx    # Editor configuration panel
│   │   ├── Layout.tsx            # Main application layout
│   │   ├── Notifications.tsx     # Toast notifications system
│   │   ├── ProblemDescription.tsx # Problem details display
│   │   ├── ProblemList.tsx       # Problem browser
│   │   ├── ProblemView.tsx       # Problem viewer with tabs
│   │   └── ResultsPanel.tsx      # Test results display
│   ├── hooks/             # Custom React hooks
│   │   ├── useAPI.ts             # API communication hook
│   │   ├── useCodeEditor.ts      # Code editor state management
│   │   ├── useConnection.ts      # Network connection monitoring
│   │   └── useNotifications.ts   # Notification system hook
│   ├── services/          # API and external services
│   │   └── api.ts               # HTTP client with caching and error handling
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts             # Comprehensive type definitions
│   ├── App.tsx            # Main application component
│   ├── App.css            # Global styles
│   └── index.tsx          # Application entry point
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## Component Architecture

### Core Components

#### `Layout.tsx`

Main application layout component that orchestrates all other components and manages global state.

**Features:**

- Responsive layout with problem panel and editor
- Settings modal management
- Global notification system
- Connection status monitoring

#### `CodeEditor.tsx`

Advanced code editor component with Monaco Editor integration.

**Features:**

- Syntax highlighting for multiple languages
- Line numbers and code folding
- Tab-based indentation
- Theme support (dark/light)
- Auto-resize functionality

#### `ProblemView.tsx`

Comprehensive problem display with tabbed interface.

**Features:**

- Problem description with markdown support
- Interactive examples with input/output
- Constraints and hints display
- Difficulty and tag indicators

#### `ResultsPanel.tsx`

Test execution results display with detailed feedback.

**Features:**

- Test case results with pass/fail status
- Execution metrics (time, memory)
- Error message display
- Diff highlighting for output comparison

### Custom Hooks

#### `useAPI.ts`

Centralized API communication with error handling and loading states.

**Features:**

- Type-safe API calls
- Automatic error handling
- Loading state management
- Request/response logging

#### `useCodeEditor.ts`

Code editor state management with persistence.

**Features:**

- Language-specific templates
- Settings persistence
- Auto-save functionality
- Language switching

#### `useConnection.ts`

Network connection monitoring and health checks.

**Features:**

- Automatic ping/health checks
- Reconnection attempts
- Connection status tracking
- Latency monitoring

#### `useNotifications.ts`

Toast notification system with auto-dismiss.

**Features:**

- Multiple notification types
- Auto-dismiss timers
- Queue management
- Convenience methods

## Type System

The application uses a comprehensive TypeScript type system defined in `types/index.ts`:

### Core Types

- **Problem**: Problem definition with metadata
- **TestCase**: Individual test case results
- **ExecutionResult**: Code execution response
- **Language**: Programming language configuration
- **EditorSettings**: Editor preferences
- **APIResponse**: Standardized API response format

### Component Props Types

All components have strongly typed props interfaces ensuring type safety throughout the application.

## API Integration

The frontend communicates with the Python orchestrator backend through a robust HTTP client:

### Features

- **Caching**: Intelligent caching with TTL for performance
- **Error Handling**: Comprehensive error types and recovery
- **Retry Logic**: Automatic retry with exponential backoff
- **Offline Support**: Local storage fallback for solutions
- **Network Monitoring**: Connection status tracking

### API Endpoints

- `GET /problems` - Fetch problem list
- `GET /problems/{slug}` - Get specific problem
- `POST /run` - Execute code
- `POST /explain` - Get code explanation
- `POST /gen-tests` - Generate test cases
- `GET /health` - Health check

## Development

### Prerequisites

- Node.js 16+ and npm
- Python orchestrator backend running on port 8000

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Development Features

- **Hot Reload**: Automatic reloading on code changes
- **Type Checking**: Real-time TypeScript validation
- **Linting**: ESLint integration for code quality
- **Testing**: Jest and React Testing Library setup

## Styling

The application uses a modern CSS-in-JS approach with styled-components for component-level styling and CSS modules for global styles.

### Theme System

- **Dark Theme**: Default dark theme optimized for coding
- **Light Theme**: Optional light theme for different preferences
- **Responsive Design**: Mobile-first responsive layout
- **Accessibility**: WCAG compliant color contrast and keyboard navigation

## Performance Optimizations

- **Code Splitting**: Lazy loading of components
- **Memoization**: React.memo and useMemo for expensive operations
- **Caching**: API response caching with intelligent invalidation
- **Bundle Optimization**: Webpack optimizations for smaller bundles

## Testing Strategy

- **Unit Tests**: Component and hook testing with Jest
- **Integration Tests**: API integration testing
- **E2E Tests**: End-to-end workflow testing
- **Type Safety**: Comprehensive TypeScript coverage

## Deployment

The frontend can be deployed as a static site to any hosting provider:

```bash
# Build production bundle
npm run build

# Deploy to hosting provider
# (Copy build/ directory contents)
```

### Docker Support

```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Contributing

1. Follow TypeScript best practices
2. Maintain comprehensive type definitions
3. Write tests for new components and hooks
4. Follow the established component architecture
5. Update documentation for new features

## Future Enhancements

- **Monaco Editor Extensions**: Advanced editor features like IntelliSense
- **Real-time Collaboration**: Multi-user coding sessions
- **Advanced Analytics**: Detailed performance metrics
- **Mobile App**: React Native mobile application
- **PWA Features**: Offline-first progressive web app capabilities
