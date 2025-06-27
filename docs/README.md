# Cyber Survival

A cyberpunk-themed, pixel art style wave-based survival game built with Python and Pygame.

## Description

Cyber Survival is an intense top-down survival shooter set in a cyberpunk universe. Fight against waves of increasingly difficult enemies using your cybernetic enhancements and weapons. Survive as long as possible while earning points and collecting power-ups.

## Features

- **Wave-based survival gameplay** - Endless waves of enemies with increasing difficulty
- **Cyberpunk pixel art style** - Detailed cyborg characters with neon colors and retro-futuristic aesthetics
- **Multiple cyborg enemy types**:
  - Basic cyborg drones with surveillance equipment
  - Fast reconnaissance units with scanning systems
  - Heavy assault cyborgs with armor and weapons
  - Elite commander units with advanced AI patterns
- **Power-up system**:
  - Health restoration
  - Damage boost
  - Speed enhancement
- **Visual effects**:
  - Particle explosions
  - Camera shake
  - Neon glow effects
  - Cyberpunk grid background
- **Game features**:
  - Score system
  - Health system with visual indicators
  - Pause functionality
  - Restart option

## Controls

- **Movement**: WASD keys or Arrow keys
- **Shooting**: Mouse click or Spacebar (aims toward mouse cursor)
- **Pause**: ESC key
- **Restart**: R key (when game over)

## Installation

1. Make sure you have Python 3.6+ installed
2. Install pygame:
   ```bash
   pip install -r requirements.txt
   ```
   Or directly:
   ```bash
   pip install pygame
   ```

## How to Run

```bash
python main.py
```

## Gameplay Tips

1. **Keep moving** - Standing still makes you an easy target
2. **Aim carefully** - Your bullets follow your mouse cursor
3. **Collect power-ups** - They appear after completing waves
4. **Watch your health** - Use health power-ups wisely
5. **Learn enemy patterns** - Different enemies have different behaviors
6. **Use the environment** - The play area has boundaries that can help

## Game Mechanics

### Wave System
- Each wave has a specific number of enemies
- Enemy count increases with each wave
- Brief break between waves for preparation
- Boss enemies start appearing from wave 5

### Enemy Types
- **Basic Cyborg Drone (Red)**: Floating surveillance unit with sensors and thrusters
- **Fast Reconnaissance Cyborg (Yellow)**: Sleek scout with scanning equipment and speed boosters
- **Heavy Assault Cyborg (Green)**: Armored tank unit with weapon systems and treads
- **Elite Cyborg Commander (Magenta)**: Advanced unit with multiple sensors, weapons, and command arrays

### Power-ups
- **Health (Green Cross)**: Restores 50 health points
- **Damage (Pink Star)**: Doubles damage for 10 seconds
- **Speed (Yellow Lightning)**: 1.5x movement speed for 8 seconds

### Scoring
- Points for killing enemies (varies by type)
- Bonus points for completing waves
- Track your high score!

## Technical Details

- Built with Python and Pygame
- 60 FPS game loop
- Pixel-perfect collision detection
- Procedural particle effects
- Modular code structure

## File Structure

```
├── main.py           # Entry point
├── game.py           # Main game class and loop
├── player.py         # Player character logic
├── enemy.py          # Enemy classes and AI
├── projectile.py     # Bullet/projectile system
├── powerup.py        # Power-up system
├── ui.py             # User interface elements
├── particle.py       # Particle effects system
├── sound_manager.py  # Sound system (basic)
└── requirements.txt  # Dependencies
```

## Future Enhancements

Potential improvements that could be added:
- Sound effects and music
- More enemy types
- Additional power-ups
- Weapon variety
- High score persistence
- Better graphics/sprites
- Multiplayer support

## License

This project is open source and available under the MIT License.

Enjoy the game and survive as long as you can in the cyberpunk wasteland! 