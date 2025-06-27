# Cyber Survival - Game Features

## 🎮 Core Gameplay
- **Top-down survival shooter** with detailed cyberpunk cyborg characters
- **Wave-based difficulty progression** - survive increasing enemy waves
- **Mouse-aimed shooting** system with projectile trails
- **WASD/Arrow key movement** with smooth diagonal movement
- **Health system** with damage invincibility frames

## 🤖 Cyborg Enemy Types
| Enemy Type | Color | Visual Design | Behavior | Health | Speed | Score |
|------------|-------|---------------|----------|--------|-------|-------|
| Basic Drone | Red | Floating unit with sensors & thrusters | Simple chase | 30 | 80 | 10 |
| Recon Cyborg | Yellow | Sleek scout with scanning equipment | Zigzag movement | 15 | 150 | 15 |
| Assault Cyborg | Green | Armored tank with weapons & treads | Slow but tanky | 80 | 40 | 30 |
| Elite Commander | Magenta | Advanced unit with multiple systems | Circles player | 200 | 60 | 100 |

## ⚡ Power-ups
- **Health (Green Cross)**: +50 health
- **Damage (Pink Star)**: 2x damage for 10 seconds
- **Speed (Yellow Lightning)**: 1.5x speed for 8 seconds

## 🎨 Visual Effects
- **Detailed cyborg character designs** with realistic proportions and cybernetic features
- **Enhanced energy bolt projectiles** with glow effects and trails
- **Cyberpunk grid background** with neon colors
- **Particle explosions** on enemy death and hits
- **Camera shake** on damage and impacts
- **Neon glow effects** on projectiles and UI
- **Health bars** for damaged enemies
- **Power-up indicators** with timers

## 🎯 Game Mechanics
- **Score system** with enemy kill bonuses and wave completion rewards
- **Progressive difficulty** - more enemies and faster spawning each wave
- **Power-up spawning** - 30% chance after completing waves
- **Collision detection** between all game objects
- **Screen boundaries** keep player within play area

## 🎵 Audio System
- **Basic sound manager** (expandable for future audio)
- **Sound effect placeholders** for shooting, hits, deaths, etc.
- **Graceful fallback** if audio system unavailable

## 🖥️ Technical Features
- **60 FPS game loop** with delta time updates
- **Modular code structure** - easy to extend and modify
- **Pygame sprite system** for efficient collision detection
- **Object-oriented design** with separate classes for each game element
- **Error handling** for missing dependencies

## 🎮 Controls
```
Movement: WASD or Arrow Keys
Shooting: Mouse Click or Spacebar (aims toward mouse)
Pause: ESC
Restart: R (when game over)
```

## 📊 Game States
- **Playing**: Normal gameplay
- **Paused**: Game paused with overlay
- **Game Over**: Death screen with final score and restart option
- **Wave Break**: Brief pause between waves with countdown

## 🚀 Performance
- Optimized sprite rendering
- Efficient particle system cleanup
- Smooth 60 FPS gameplay
- Low memory footprint 