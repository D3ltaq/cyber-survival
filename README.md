# Cyber Survival

A cyberpunk-themed wave-based survival game built with Python and Pygame.

## 🎮 Game Features

- **Wave-based survival gameplay** with increasing difficulty
- **Cyberpunk aesthetic** with neon colors and futuristic visuals
- **Character progression** with XP system and upgrades
- **Multiple weapon types** including auto-targeting and passive weapons
- **Various enemy types** with unique behaviors and AI
- **Power-ups** for temporary boosts
- **Particle effects** and visual polish

## 🚀 Quick Start

### Requirements

- Python 3.7+
- Pygame 2.0+

### Installation

1. Clone or download this repository
2. Install dependencies:

**On Windows:**
```bash
scripts/install.bat
```

**On macOS/Linux:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

**Manual installation:**
```bash
pip install pygame
```

### Running the Game

```bash
python main.py
```

## 📁 Project Structure

```
PythonGame/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── main.py              # Game initialization and main loop
│   │
│   ├── core/                # Core game logic
│   │   ├── __init__.py
│   │   ├── game.py          # Main game class and logic
│   │   └── level_system.py  # XP and upgrade system
│   │
│   ├── entities/            # Game objects
│   │   ├── __init__.py
│   │   ├── player.py        # Player character and weapons
│   │   ├── enemy.py         # Enemy types and AI
│   │   ├── projectile.py    # Bullets and projectiles
│   │   └── powerup.py       # Collectible power-ups
│   │
│   ├── systems/             # Game systems
│   │   ├── __init__.py
│   │   ├── particle.py      # Particle effects system
│   │   └── sound_manager.py # Audio management
│   │
│   ├── ui/                  # User interface
│   │   ├── __init__.py
│   │   ├── ui.py            # HUD and game UI
│   │   ├── main_menu.py     # Main menu screen
│   │   └── level_up_ui.py   # Level up selection screen
│   │
│   └── utils/               # Utility functions
│       └── __init__.py
│
├── assets/                  # Game assets (currently unused)
├── docs/                    # Documentation
│   ├── README.md           # Detailed game documentation
│   └── GAME_FEATURES.md    # Complete feature list
│
└── scripts/                # Setup and utility scripts
    ├── install.bat         # Windows installation script
    └── install.sh          # Unix installation script
```

## 🎯 How to Play

### Controls

- **Movement:** WASD keys or Arrow keys
- **Shooting:** Mouse or Spacebar
- **Pause:** ESC key

### Gameplay

1. **Survive waves** of increasingly difficult enemies
2. **Collect XP** by defeating enemies
3. **Level up** and choose from 3 random upgrades
4. **Collect power-ups** for temporary advantages
5. **Aim for high scores** and see how long you can survive!

### Upgrade Types

- **Weapon Upgrades:** Rapid fire, double shot, spread shot, piercing, explosive rounds
- **New Weapons:** Auto-targeting system, laser rifle, plasma cannon, cybernetic shotgun
- **Passive Weapons:** Orbital missiles, energy shuriken, shoulder laser, combat drones
- **Character Upgrades:** Health boost, speed boost, damage boost, regeneration, shields
- **Utility:** Area damage, time dilation, XP magnet

## 🛠️ Development

### Code Organization

The project follows a modular architecture:

- **Core:** Contains the main game loop and systems
- **Entities:** Game objects with their own logic and rendering
- **Systems:** Reusable systems like particles and audio
- **UI:** All user interface components
- **Utils:** Shared utility functions

### Adding New Features

1. **New Entity:** Add to `src/entities/`
2. **New System:** Add to `src/systems/`
3. **New UI Component:** Add to `src/ui/`
4. **Core Logic:** Modify `src/core/game.py`

## 📜 License

This project is open source. Feel free to modify and distribute.

## 🎨 Credits

- Built with Python and Pygame
- Original cyberpunk-inspired design
- Procedural particle effects and visual polish 