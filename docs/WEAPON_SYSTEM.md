# Weapon System Documentation

The game now features a comprehensive weapon system where each weapon type has unique projectile characteristics, including different speeds, ranges, damage, and visual effects.

## Weapon Types

### 1. Default Energy Blaster
- **Damage**: 1.0x (base)
- **Speed**: 500 pixels/second
- **Range**: 600 pixels
- **Fire Rate**: 1.0x (base)
- **Projectile**: Standard energy bolt with trail
- **Description**: Balanced weapon good for all situations

### 2. Laser Rifle
- **Damage**: 0.6x (lower damage)
- **Speed**: 800 pixels/second (very fast)
- **Range**: 700 pixels
- **Fire Rate**: 3.3x faster (0.3x delay)
- **Projectile**: Bright laser beams (3 shots per burst)
- **Description**: High-speed continuous laser bursts - fast but lower damage

### 3. Plasma Cannon
- **Damage**: 3.0x (very high)
- **Speed**: 300 pixels/second (slow)
- **Range**: 500 pixels
- **Fire Rate**: 0.4x slower (2.5x delay)
- **Projectile**: Large pulsating plasma balls with explosive effect
- **Special**: Explosive damage on impact
- **Description**: Devastating slow-moving projectiles

### 4. Cybernetic Shotgun
- **Damage**: 0.4x per pellet (8 pellets = 3.2x total at close range)
- **Speed**: 450 pixels/second
- **Range**: 250 pixels (short range)
- **Fire Rate**: 0.56x slower (1.8x delay)
- **Projectile**: 8 small pellets in wide spread
- **Description**: Devastating at close range, ineffective at distance

### 5. Precision Rifle (Sniper)
- **Damage**: 4.0x (highest single shot)
- **Speed**: 1000 pixels/second (very fast)
- **Range**: 1200 pixels (very long)
- **Fire Rate**: 0.33x slower (3.0x delay)
- **Projectile**: Precise tracer bullet
- **Special**: Piercing through multiple enemies
- **Description**: High-damage precision weapon with perfect accuracy

### 6. Rapid-Fire Gun (Machine Gun)
- **Damage**: 0.5x (low per shot)
- **Speed**: 600 pixels/second
- **Range**: 500 pixels
- **Fire Rate**: 6.7x faster (0.15x delay)
- **Projectile**: Small bullets with slight spread
- **Description**: Suppresses enemies with volume of fire

### 7. Energy Beam
- **Damage**: 0.8x
- **Speed**: 400 pixels/second
- **Range**: 800 pixels
- **Fire Rate**: 2x faster (0.5x delay)
- **Projectile**: Pulsating energy orbs
- **Special**: Piercing through multiple enemies
- **Description**: Continuous beam effect piercing through enemies

## Projectile Visual Differences

Each weapon type has distinctive visual projectiles:

- **Default**: Diamond-shaped energy bolt with cyan trail
- **Laser Rifle**: Bright blue laser lines with white core
- **Plasma Cannon**: Large purple pulsating spheres with multiple glow layers
- **Shotgun**: Small hot pink pellets, bright and compact
- **Sniper Rifle**: Yellow tracer lines with bright white tips
- **Machine Gun**: Orange bullet lines with yellow cores
- **Energy Beam**: Green pulsating energy orbs
- **Auto-targeting**: Light purple homing projectiles

## Range System

All projectiles now have maximum ranges before disappearing:
- Projectiles track distance traveled and self-destruct when reaching max range
- Different weapons have different effective ranges
- Short-range weapons (shotgun) become ineffective at distance
- Long-range weapons (sniper) maintain effectiveness across the map

## Upgrade Compatibility

The new weapon system is compatible with existing upgrade systems:
- Piercing rounds work with any weapon
- Explosive rounds add explosion effects to any weapon  
- Double shot and spread shot modifiers apply to default weapon
- Rapid fire upgrades stack with weapon-specific fire rates

## How to Unlock

New weapons are available as level-up upgrades:
- Each weapon type appears as a selectable upgrade option
- Once selected, it replaces your current weapon
- Weapon upgrades are permanent for the current run

## Balancing

Each weapon fills a specific role:
- **Close range**: Shotgun excels in tight spaces
- **Long range**: Sniper rifle for precise elimination
- **Crowd control**: Machine gun for multiple weak enemies
- **Heavy damage**: Plasma cannon for tough targets
- **Speed**: Laser rifle for fast enemies
- **Versatile**: Default blaster for balanced gameplay
- **Piercing**: Energy beam for lined-up enemies 