# 🏰 AI Dungeon - LangGraph + Gemini Text Adventure

An immersive text-based adventure game powered by **LangGraph** and **Google Gemini AI** for dynamic world generation and intelligent dialogue.

## ✨ Features

- **🤖 AI-Powered World Generation**: Locations, NPCs, and items are dynamically created using Google Gemini
- **🕸️ LangGraph Orchestration**: Sophisticated AI workflows for content generation
- **📦 Rich Inventory System**: Weight-based inventory with item properties and equipment slots
- **📈 Character Progression**: Level up your character with stats and abilities
- **💬 Dynamic Dialogue**: NPCs respond intelligently based on context and history
- **🎮 Rich Terminal UI**: Beautiful interface powered by Textual
- **💾 Save/Load System**: Persist your adventures
- **🎯 Command History**: Navigate previous commands with arrow keys

## 🏗️ Project Structure

```
src/ai_dungeon/
├── core/           # Core game models and utilities
│   ├── models.py   # Game data structures
│   ├── utils.py    # Command parsing and utilities
│   └── engine.py   # Main game engine
├── player/         # Player management
│   ├── inventory.py # Inventory system
│   └── player.py   # Player character
├── world/          # World management
│   └── world.py    # Locations, NPCs, items
├── ai/             # AI integration
│   └── gemini_engine.py # LangGraph + Gemini AI
├── ui/             # User interface
│   └── app.py      # Textual UI
└── main.py         # Entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- Google Gemini API key (optional, for AI features)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd 2025-08-21-textual_ai_dungeon
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Set up your API key (optional):**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   export GOOGLE_API_KEY="your-key-here"
   ```

4. **Run the game:**
   ```bash
   source venv/bin/activate
   python -m ai_dungeon.main
   ```

### Alternative: Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Run the game
python -m ai_dungeon.main
```

## 🎮 How to Play

### Basic Commands

- **Movement**: `north`, `south`, `east`, `west` (or `n`, `s`, `e`, `w`)
- **Inventory**: `inventory`, `take [item]`, `drop [item]`, `use [item]`
- **Interaction**: `look`, `examine [item]`, `talk to [character]`
- **System**: `help`, `quit`, `save`, `load`, `status`

### Keyboard Shortcuts

- `Ctrl+C`: Quit game
- `Ctrl+H`: Show help
- `Ctrl+S`: Save game
- `Ctrl+L`: Load game
- `Ctrl+I`: Show inventory
- `Ctrl+T`: Show character stats
- `↑/↓`: Navigate command history

### Example Session

```
> look
You find yourself in a dimly lit stone chamber. Ancient runes cover the walls, 
and a mysterious energy fills the air. This appears to be some kind of ritual chamber.

You notice: rusty key
Exits: north, east

> take key
You take the rusty key.

> north
You step into a long, narrow corridor. Torches mounted on the walls cast 
dancing shadows. The passage continues deeper into the structure.

Exits: south, north, west

> examine key
The rusty key: An old, rusty key. It looks like it might open something important.
```

## 🤖 AI Features

### World Generation
The AI creates new locations, NPCs, and items dynamically as you explore:

- **Locations**: Atmospheric descriptions with appropriate exits and contents
- **NPCs**: Characters with personalities, backgrounds, and dynamic dialogue
- **Items**: Objects with properties, descriptions, and interactive behaviors

### LangGraph Workflow
The AI system uses LangGraph to orchestrate content generation:

1. **Request Analysis**: Understands what type of content to generate
2. **Context Processing**: Considers game state, location, and player history
3. **Content Generation**: Creates appropriate content using Gemini
4. **Response Formatting**: Structures the output for the game engine

### Running Without AI
You can run the game without AI features using fallback content:

```bash
python -m ai_dungeon.main --no-ai
```

## 🛠️ Development

### Project Philosophy
- **Clean Architecture**: Modular design with clear separation of concerns
- **Type Safety**: Comprehensive type hints throughout
- **AI Integration**: Seamless blend of traditional game logic and AI generation
- **User Experience**: Rich, responsive terminal interface

### Key Components

1. **Game Engine** (`core/engine.py`): Orchestrates all game systems
2. **World System** (`world/world.py`): Manages locations, NPCs, and items
3. **Player System** (`player/`): Handles character progression and inventory
4. **AI Engine** (`ai/gemini_engine.py`): LangGraph workflows for content generation
5. **UI System** (`ui/app.py`): Rich terminal interface with Textual

### Adding New Features

The modular design makes it easy to extend:

- **New Commands**: Add to `CommandParser` in `core/utils.py`
- **New AI Content**: Extend workflows in `ai/gemini_engine.py`
- **New UI Elements**: Modify `ui/app.py`
- **New Game Mechanics**: Extend `core/engine.py`

## 📋 Dependencies

### Core Dependencies
- `textual>=0.40.0` - Rich terminal UI
- `pydantic>=2.0.0` - Data validation

### AI Dependencies
- `langgraph>=0.2.0` - AI workflow orchestration
- `langchain-google-genai>=1.0.0` - Google Gemini integration
- `langchain-core>=0.3.0` - Core LangChain functionality

### Development
- `python-dotenv>=1.0.0` - Environment variable management
- `typing-extensions>=4.8.0` - Extended type hints

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `DEBUG_MODE`: Enable debug output (true/false)
- `AI_TEMPERATURE`: Control AI creativity (0.0-1.0)
- `AI_MAX_TOKENS`: Maximum tokens per AI response

### Command Line Options
```bash
python -m ai_dungeon.main --help

options:
  --api-key API_KEY     Google Gemini API key
  --no-ai              Run without AI features
  --debug              Enable debug mode
```

## 🎯 Future Enhancements

- **Multiplayer Support**: Share adventures with friends
- **Custom World Import**: Load pre-built worlds
- **Voice Commands**: Speech recognition integration
- **Graphics Mode**: Optional ASCII art and maps
- **Quest System**: Structured storylines and objectives
- **Combat System**: Turn-based battle mechanics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📄 License

This project is open source and available under the MIT License.

---

*Embark on an adventure where every location, character, and story is unique, powered by the magic of AI! 🧙‍♂️✨*
