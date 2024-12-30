# Messaging App

A Windows thin client for iMessage built with Python and Tkinter.

## Features

- Real-time message synchronization
- Thread management and organization
- Modern UI with customizable themes
- File and image attachment support
- Message search functionality
- Event-driven architecture

## Architecture

The application follows Clean Architecture principles with distinct layers:

- **Domain**: Core business logic and models
- **Services**: Business operations and state management
- **Controllers**: Coordination between UI and services
- **UI**: User interface components and event handling

### Key Components

- `EventBus`: Manages application-wide event publishing/subscription
- `ChatController`: Main controller orchestrating message and thread handling
- `MessageService`: Handles message operations and synchronization
- `ThreadManager`: Manages chat threads and their state
- `MessageDisplayManager`: Handles message rendering and display
- `UIManager`: Manages UI state and user interactions

## Setup

### Prerequisites

- Python 3.8+
- Tkinter
- asyncio
- aiohttp

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd messaging-app
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows
```

3. Install dependencies
```bash
pip install -e .
```

## Running the Application

```bash
python -m messaging_app.main
```

## Project Structure

```
messaging_app/
├── domain/           # Business entities and interfaces
├── services/         # Core business logic
├── controllers/      # Application controllers
├── ui/              # User interface components
│   └── components/  # Reusable UI elements
├── utils/           # Utility functions
├── bubbles/         # Message bubble implementations
└── config/          # Configuration management
```

## Development

### Adding New Features

1. Define interfaces in `domain/interfaces.py`
2. Implement business logic in services
3. Add controller methods for coordination
4. Create or update UI components
5. Register event handlers
