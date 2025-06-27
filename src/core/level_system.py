import random
import math

class LevelSystem:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 50  # Starting XP requirement (matches new formula)
        
        # Upgrade definitions
        self.available_upgrades = {
            # Weapons
            "rapid_fire": {
                "name": "Rapid Fire",
                "description": "Reduce shooting cooldown by 25%",
                "type": "weapon_upgrade",
                "max_level": 5
            },
            "double_shot": {
                "name": "Double Shot", 
                "description": "Fire two projectiles at once",
                "type": "weapon_new",
                "max_level": 1
            },
            "spread_shot": {
                "name": "Spread Shot",
                "description": "Fire 3 projectiles in a spread",
                "type": "weapon_new", 
                "max_level": 3
            },
            "piercing_rounds": {
                "name": "Piercing Rounds",
                "description": "Bullets pierce through enemies",
                "type": "weapon_upgrade",
                "max_level": 1
            },
            "explosive_rounds": {
                "name": "Explosive Rounds",
                "description": "Bullets explode on impact",
                "type": "weapon_upgrade",
                "max_level": 1
            },
            "auto_targeting": {
                "name": "Auto-Targeting System",
                "description": "Automatically aims and fires at nearest enemy",
                "type": "weapon_new",
                "max_level": 3
            },
            "laser_rifle": {
                "name": "Laser Rifle",
                "description": "Replace gun with continuous laser beam",
                "type": "weapon_new",
                "max_level": 1
            },
            "plasma_cannon": {
                "name": "Plasma Cannon",
                "description": "Slow but devastating plasma shots",
                "type": "weapon_new",
                "max_level": 1
            },
            "shotgun": {
                "name": "Cybernetic Shotgun",
                "description": "Close-range spread weapon",
                "type": "weapon_new",
                "max_level": 1
            },
            "sniper_rifle": {
                "name": "Precision Rifle",
                "description": "High-damage long-range weapon with piercing",
                "type": "weapon_new",
                "max_level": 1
            },
            "machine_gun": {
                "name": "Rapid-Fire Gun",
                "description": "Very fast firing rate with slight spread",
                "type": "weapon_new",
                "max_level": 1
            },
            "energy_beam": {
                "name": "Energy Beam",
                "description": "Continuous beam that pierces enemies",
                "type": "weapon_new",
                "max_level": 1
            },
            
            # Passive traits
            "health_boost": {
                "name": "Health Boost",
                "description": "Increase max health by 25",
                "type": "passive",
                "max_level": 4
            },
            "speed_boost": {
                "name": "Speed Boost", 
                "description": "Increase movement speed by 15%",
                "type": "passive",
                "max_level": 3
            },
            "damage_boost": {
                "name": "Damage Boost",
                "description": "Increase weapon damage by 25%",
                "type": "passive",
                "max_level": 5
            },
            "xp_magnet": {
                "name": "XP Magnet",
                "description": "Increase XP pickup range",
                "type": "passive",
                "max_level": 3
            },
            "regeneration": {
                "name": "Regeneration",
                "description": "Slowly regenerate health over time",
                "type": "passive",
                "max_level": 3
            },
            "shield": {
                "name": "Energy Shield",
                "description": "Absorb damage before losing health",
                "type": "passive",
                "max_level": 2
            },
            "orbital_missiles": {
                "name": "Orbital Missiles",
                "description": "Launch homing missiles periodically",
                "type": "passive",
                "max_level": 4
            },
            "energy_shuriken": {
                "name": "Energy Shuriken",
                "description": "Spinning blades orbit around you",
                "type": "passive",
                "max_level": 3
            },
            "laser_turret": {
                "name": "Shoulder Laser",
                "description": "Auto-firing laser targets enemies",
                "type": "passive",
                "max_level": 3
            },
            "drone_companion": {
                "name": "Combat Drone",
                "description": "AI drone follows and shoots enemies",
                "type": "passive",
                "max_level": 2
            },
            
            # Utility
            "area_damage": {
                "name": "Area Damage",
                "description": "Damage nearby enemies periodically",
                "type": "utility",
                "max_level": 4
            },
            "time_slow": {
                "name": "Time Dilation",
                "description": "Occasionally slow down time",
                "type": "utility",
                "max_level": 2
            }
        }
        
        # Player's current upgrades
        self.player_upgrades = {}
    
    def add_xp(self, amount):
        """Add XP and check for level up"""
        self.xp += amount
        
        if self.xp >= self.xp_to_next_level:
            return self.level_up()
        return False
    
    def level_up(self):
        """Level up the player and calculate next XP requirement"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        
        # Much faster XP scaling: next_xp = base * (level^0.8) 
        self.xp_to_next_level = int(50 * math.pow(self.level, 0.8))
        
        return True
    
    def get_available_upgrade_choices(self, count=3):
        """Get random upgrade choices for level up"""
        available = []
        
        for upgrade_id, upgrade_data in self.available_upgrades.items():
            current_level = self.player_upgrades.get(upgrade_id, 0)
            if current_level < upgrade_data["max_level"]:
                available.append(upgrade_id)
        
        # If we don't have enough unique upgrades, allow some repeats
        if len(available) < count:
            # Add some duplicates of upgrades that can be leveled up
            for upgrade_id, upgrade_data in self.available_upgrades.items():
                current_level = self.player_upgrades.get(upgrade_id, 0)
                if current_level < upgrade_data["max_level"] and upgrade_data["max_level"] > 1:
                    available.extend([upgrade_id] * (upgrade_data["max_level"] - current_level))
        
        # Select random upgrades
        choices = random.sample(available, min(count, len(available)))
        
        # If still not enough, add health boost as fallback
        while len(choices) < count:
            choices.append("health_boost")
        
        return choices[:count]
    
    def apply_upgrade(self, upgrade_id):
        """Apply the selected upgrade to the player"""
        if upgrade_id not in self.available_upgrades:
            return False
        
        current_level = self.player_upgrades.get(upgrade_id, 0)
        max_level = self.available_upgrades[upgrade_id]["max_level"]
        
        if current_level < max_level:
            self.player_upgrades[upgrade_id] = current_level + 1
            return True
        
        return False
    
    def get_upgrade_info(self, upgrade_id):
        """Get detailed info about an upgrade"""
        if upgrade_id not in self.available_upgrades:
            return None
        
        upgrade_data = self.available_upgrades[upgrade_id].copy()
        current_level = self.player_upgrades.get(upgrade_id, 0)
        upgrade_data["current_level"] = current_level
        upgrade_data["upgrade_id"] = upgrade_id
        
        return upgrade_data
    
    def get_xp_progress(self):
        """Get XP progress as a percentage"""
        return self.xp / self.xp_to_next_level
    
    def has_upgrade(self, upgrade_id):
        """Check if player has a specific upgrade"""
        return self.player_upgrades.get(upgrade_id, 0) > 0
    
    def get_upgrade_level(self, upgrade_id):
        """Get the level of a specific upgrade"""
        return self.player_upgrades.get(upgrade_id, 0)


class XPOrb:
    """XP pickup that enemies drop"""
    def __init__(self, x, y, value=5):
        self.x = x
        self.y = y
        self.value = value
        self.lifetime = 30000  # 30 seconds before despawning
        self.timer = 0
        
        # Visual properties
        self.float_offset = 0
        self.pulse = 0
        
        # Colors
        self.XP_COLOR = (255, 255, 100)  # Golden yellow
        self.XP_GLOW = (255, 200, 50)
        
    def update(self, dt, player_pos, magnet_range=50):
        """Update XP orb with optional magnetic attraction"""
        self.timer += dt
        
        # Animate floating and pulsing
        self.float_offset = math.sin(self.timer * 0.005) * 2
        self.pulse = math.sin(self.timer * 0.008) * 0.3 + 0.7
        
        # Magnetic attraction to player
        player_x, player_y = player_pos
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < magnet_range and distance > 0:
            # Move towards player
            speed = 200 * (dt / 1000.0)
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed
        
        # Check if expired
        return self.timer < self.lifetime
    
    def draw(self, surface):
        """Draw the XP orb"""
        import pygame
        
        center_x = int(self.x)
        center_y = int(self.y + self.float_offset)
        
        # Main orb (larger and more visible)
        orb_radius = max(3, int(6 * self.pulse))
        pygame.draw.circle(surface, self.XP_COLOR, (center_x, center_y), orb_radius)
        
        # Inner highlight
        inner_radius = max(1, orb_radius - 2)
        if inner_radius > 0:
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), inner_radius)
        
        # Outer glow (simpler approach)
        glow_radius = orb_radius + 2
        for i in range(3):
            alpha = 60 - (i * 20)
            glow_color = (self.XP_GLOW[0], self.XP_GLOW[1], self.XP_GLOW[2])
            # Create a temporary surface for glow
            temp_surface = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4))
            temp_surface.set_alpha(alpha)
            temp_surface.fill((0, 0, 0))
            temp_surface.set_colorkey((0, 0, 0))
            pygame.draw.circle(temp_surface, glow_color, 
                             (glow_radius + 2, glow_radius + 2), glow_radius - i)
            surface.blit(temp_surface, 
                        (center_x - glow_radius - 2, center_y - glow_radius - 2))
        
        # Core
        pygame.draw.circle(surface, (255, 255, 150), (center_x, center_y), max(1, orb_radius - 1))
    
    def get_rect(self):
        """Get collision rectangle"""
        import pygame
        return pygame.Rect(int(self.x) - 6, int(self.y) - 6, 12, 12) 