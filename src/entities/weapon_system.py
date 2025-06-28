import math
from .projectile import Projectile

class WeaponSystem:
    """Centralized weapon system that defines unique properties for each weapon type"""
    
    def __init__(self):
        # Define weapon properties: [damage_multiplier, speed, range, fire_rate_multiplier, projectile_size, special_properties]
        self.weapon_configs = {
            "default": {
                "damage_multiplier": 1.0,
                "projectile_speed": 500,
                "max_range": 600,
                "fire_rate_multiplier": 1.0,
                "projectile_size": 6,
                "projectile_count": 1,
                "spread_angle": 0,
                "description": "Standard energy blaster - balanced damage and speed",
                "mod_slots": 2,  # Number of mod slots available for this weapon
                "applied_mods": []  # List to store applied mods
            },
            "laser_rifle": {
                "damage_multiplier": 0.6,
                "projectile_speed": 800,
                "max_range": 700,
                "fire_rate_multiplier": 0.3,  # Much faster fire rate
                "projectile_size": 4,
                "projectile_count": 3,  # Burst fire
                "spread_angle": 0.1,
                "description": "High-speed laser bursts - fast but lower damage",
                "mod_slots": 2,
                "applied_mods": []
            },
            "plasma_cannon": {
                "damage_multiplier": 3.0,
                "projectile_speed": 300,
                "max_range": 500,
                "fire_rate_multiplier": 2.5,  # Much slower fire rate
                "projectile_size": 12,
                "projectile_count": 1,
                "spread_angle": 0,
                "explosive": True,
                "description": "Devastating plasma shots - slow but massive damage",
                "mod_slots": 1,
                "applied_mods": []
            },
            "shotgun": {
                "damage_multiplier": 0.4,
                "projectile_speed": 450,
                "max_range": 250,  # Short range
                "fire_rate_multiplier": 1.8,
                "projectile_size": 3,
                "projectile_count": 8,
                "spread_angle": 1.2,  # Wide spread
                "description": "Close-range spread weapon - devastating up close",
                "mod_slots": 2,
                "applied_mods": []
            },
            "sniper_rifle": {
                "damage_multiplier": 4.0,
                "projectile_speed": 1000,
                "max_range": 1200,  # Very long range
                "fire_rate_multiplier": 3.0,  # Very slow
                "projectile_size": 5,
                "projectile_count": 1,
                "spread_angle": 0,
                "piercing": True,
                "description": "High-damage precision weapon - perfect accuracy",
                "mod_slots": 2,
                "applied_mods": []
            },
            "machine_gun": {
                "damage_multiplier": 0.5,
                "projectile_speed": 600,
                "max_range": 500,
                "fire_rate_multiplier": 0.15,  # Very fast
                "projectile_size": 4,
                "projectile_count": 1,
                "spread_angle": 0.3,  # Slight spread
                "description": "Rapid-fire weapon - suppresses enemies with volume",
                "mod_slots": 2,
                "applied_mods": []
            },
            "energy_beam": {
                "damage_multiplier": 0.8,
                "projectile_speed": 400,
                "max_range": 800,
                "fire_rate_multiplier": 0.5,
                "projectile_size": 8,
                "projectile_count": 1,
                "spread_angle": 0,
                "piercing": True,
                "description": "Continuous energy beam - pierces through multiple enemies",
                "mod_slots": 1,
                "applied_mods": []
            },
            "plasma_shotgun": {  # Hybrid weapon combining Plasma Cannon and Shotgun traits
                "damage_multiplier": 1.5,
                "projectile_speed": 400,
                "max_range": 300,
                "fire_rate_multiplier": 2.0,
                "projectile_size": 8,
                "projectile_count": 5,
                "spread_angle": 1.0,
                "explosive": True,
                "description": "Hybrid weapon with explosive spread shots - powerful at mid-range",
                "mod_slots": 1,
                "applied_mods": []
            }
        }
        
        # Define available weapon mods
        self.weapon_mods = {
            "scope": {
                "name": "Scope",
                "description": "Increases weapon range by 20%",
                "effect": {"max_range": 1.2}
            },
            "rapid_barrel": {
                "name": "Rapid Barrel",
                "description": "Increases fire rate by 25%",
                "effect": {"fire_rate_multiplier": 0.75}
            },
            "damage_core": {
                "name": "Damage Core",
                "description": "Increases damage by 15%",
                "effect": {"damage_multiplier": 1.15}
            },
            "spread_adapter": {
                "name": "Spread Adapter",
                "description": "Adds slight spread to non-spread weapons",
                "effect": {"spread_angle": 0.3, "projectile_count": 2}
            }
        }
    
    def get_weapon_config(self, weapon_type):
        """Get configuration for a specific weapon type"""
        return self.weapon_configs.get(weapon_type, self.weapon_configs["default"])
    
    def apply_mod(self, weapon_type, mod_id):
        """Apply a mod to a specific weapon type if slots are available"""
        if weapon_type not in self.weapon_configs:
            return False
        
        weapon = self.weapon_configs[weapon_type]
        if len(weapon['applied_mods']) < weapon['mod_slots'] and mod_id in self.weapon_mods:
            weapon['applied_mods'].append(mod_id)
            return True
        return False

    def remove_mod(self, weapon_type, mod_id):
        """Remove a mod from a specific weapon type"""
        if weapon_type in self.weapon_configs and mod_id in self.weapon_configs[weapon_type]['applied_mods']:
            self.weapon_configs[weapon_type]['applied_mods'].remove(mod_id)
            return True
        return False

    def get_modified_config(self, weapon_type):
        """Get weapon configuration with applied mods"""
        base_config = self.get_weapon_config(weapon_type).copy()
        for mod_id in base_config.get('applied_mods', []):
            mod_effects = self.weapon_mods[mod_id]['effect']
            for key, value in mod_effects.items():
                if key in base_config:
                    if key == 'fire_rate_multiplier':
                        base_config[key] *= value  # Multiplicative for fire rate
                    else:
                        base_config[key] = int(base_config[key] * value) if isinstance(base_config[key], (int, float)) else value
                else:
                    base_config[key] = value
        return base_config

    def create_projectiles(self, weapon_type, player_x, player_y, angle, base_damage, player):
        """Create projectiles based on weapon type and player upgrades"""
        config = self.get_modified_config(weapon_type)  # Use modified config with mods
        projectiles = []
        
        # Calculate final damage
        total_damage = int(base_damage * config["damage_multiplier"])
        
        # Handle projectile count and spread
        projectile_count = config["projectile_count"]
        spread_angle = config["spread_angle"]
        
        # Handle existing player upgrades
        if hasattr(player, 'has_double_shot') and player.has_double_shot and weapon_type == "default":
            projectile_count = 2
            spread_angle = 0.2
        elif hasattr(player, 'has_spread_shot') and player.has_spread_shot and weapon_type == "default":
            projectile_count = 3 + getattr(player, 'spread_shot_level', 0)
            spread_angle = math.pi / 6
        
        # Create projectiles
        for i in range(projectile_count):
            if projectile_count == 1:
                proj_angle = angle
            else:
                # Calculate spread
                if projectile_count > 1:
                    angle_offset = (i / (projectile_count - 1) - 0.5) * spread_angle
                    proj_angle = angle + angle_offset
                else:
                    proj_angle = angle
            
            # Create projectile with weapon-specific properties
            proj = Projectile(
                x=player_x,
                y=player_y,
                angle=proj_angle,
                damage=total_damage // projectile_count if projectile_count > 1 else total_damage,
                speed=config["projectile_speed"],
                size=config["projectile_size"],
                weapon_type=weapon_type,
                max_range=config["max_range"]
            )
            
            # Apply special properties
            if config.get("piercing", False) or (hasattr(player, 'has_piercing') and player.has_piercing):
                proj.piercing = True
            
            if config.get("explosive", False) or (hasattr(player, 'has_explosive') and player.has_explosive):
                proj.explosive = True
            
            projectiles.append(proj)
        
        return projectiles
    
    def get_fire_rate_multiplier(self, weapon_type):
        """Get the fire rate multiplier for a weapon type"""
        config = self.get_modified_config(weapon_type)  # Use modified config
        return config["fire_rate_multiplier"]
    
    def get_weapon_description(self, weapon_type):
        """Get the description for a weapon type"""
        config = self.get_weapon_config(weapon_type)
        return config["description"]
    
    def get_all_weapon_types(self):
        """Get list of all available weapon types"""
        return list(self.weapon_configs.keys())
    
    def get_weapon_stats_display(self, weapon_type):
        """Get formatted stats for UI display"""
        config = self.get_modified_config(weapon_type)  # Use modified config
        
        # Convert to readable format
        damage = f"{config['damage_multiplier']:.1f}x"
        speed = f"{config['projectile_speed']}"
        range_val = f"{config['max_range']}"
        fire_rate = f"{1/config['fire_rate_multiplier']:.1f}x" if config['fire_rate_multiplier'] != 1.0 else "1.0x"
        
        # Include mods in description
        mod_desc = ""
        if config.get('applied_mods'):
            mod_desc = " [Mods: " + ", ".join(self.weapon_mods[mod_id]['name'] for mod_id in config['applied_mods']) + "]"
        
        return {
            "damage": damage,
            "speed": speed,
            "range": range_val,
            "fire_rate": fire_rate,
            "description": config["description"] + mod_desc
        }

    def get_available_mods(self):
        """Get list of all available mods"""
        return list(self.weapon_mods.keys())

    def get_mod_description(self, mod_id):
        """Get description for a specific mod"""
        return self.weapon_mods.get(mod_id, {}).get("description", "Unknown mod") 