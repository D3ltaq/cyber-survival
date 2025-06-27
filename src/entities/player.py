import pygame
import math
from .projectile import Projectile
from .weapon_system import WeaponSystem

# Fix linter errors for pygame constants
if not hasattr(pygame, 'K_LEFT'):
    pygame.K_LEFT = 276
    pygame.K_RIGHT = 275
    pygame.K_UP = 273
    pygame.K_DOWN = 274
    pygame.K_a = 97
    pygame.K_d = 100
    pygame.K_w = 119
    pygame.K_s = 115

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.image = pygame.Surface((30, 30))  # Required for pygame sprite
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        self.speed = 300  # pixels per second
        self.max_health = 100
        self.health = self.max_health
        
        # Weapon system
        self.weapon_system = WeaponSystem()
        
        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay = 150  # milliseconds
        
        # Damage invincibility
        self.damage_cooldown = 0
        self.damage_delay = 1000  # 1 second
        
        # Colors (New palette)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.MINT_GREEN = (108, 255, 222)
        self.CYAN = (108, 222, 255)
        self.ELECTRIC_BLUE = (108, 178, 255)
        self.ROYAL_BLUE = (108, 134, 255)
        self.DEEP_BLUE = (56, 89, 178)
        self.PURPLE = (134, 108, 255)
        self.VIOLET = (178, 108, 255)
        self.MAGENTA = (222, 108, 255)
        self.HOT_PINK = (255, 108, 222)
        self.CORAL = (255, 134, 178)
        self.DARK_PURPLE = (44, 26, 89)
        
        # Power-ups
        self.damage_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.powerup_timers = {}
        
        # Weapon upgrades
        self.shoot_delay_multiplier = 1.0
        self.has_double_shot = False
        self.has_spread_shot = False
        self.spread_shot_level = 0
        self.has_piercing = False
        self.has_explosive = False
        
        # New weapon systems
        self.auto_targeting_level = 0
        self.auto_target_timer = 0
        self.current_weapon = "default"  # default, laser_rifle, plasma_cannon, shotgun
        
        # Passive weapon systems
        self.orbital_missiles_level = 0
        self.missile_timer = 0
        self.energy_shuriken_level = 0
        self.shuriken_angle = 0
        self.shuriken_hit_enemies = set()  # Track recently hit enemies
        self.shuriken_hit_reset_timer = 0
        self.laser_turret_level = 0
        self.turret_timer = 0
        self.drone_companion_level = 0
        self.drone_timer = 0
        
        # Passive upgrades
        self.base_damage_multiplier = 1.0
        self.base_speed_multiplier = 1.0
        self.max_health_bonus = 0
        self.has_regeneration = False
        self.regen_level = 0
        self.regen_timer = 0
        self.shield_max = 0
        self.shield_current = 0
        
        # Utility
        self.has_area_damage = False
        self.area_damage_level = 0
        self.area_damage_timer = 0
        
    def update(self, keys, dt, screen_width, screen_height):
        # Update timers
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.damage_cooldown = max(0, self.damage_cooldown - dt)
        self.regen_timer = max(0, self.regen_timer - dt)
        self.area_damage_timer = max(0, self.area_damage_timer - dt)
        
        # Update passive weapon timers
        self.auto_target_timer = max(0, self.auto_target_timer - dt)
        self.missile_timer = max(0, self.missile_timer - dt)
        self.turret_timer = max(0, self.turret_timer - dt)
        self.drone_timer = max(0, self.drone_timer - dt)
        self.shuriken_angle += dt * 0.003  # Rotate shuriken
        
        # Reset shuriken hit tracking periodically
        self.shuriken_hit_reset_timer -= dt
        if self.shuriken_hit_reset_timer <= 0:
            self.shuriken_hit_enemies.clear()
            self.shuriken_hit_reset_timer = 200  # Reset every 200ms
        
        # Handle regeneration
        if self.has_regeneration and self.regen_timer <= 0:
            regen_amount = self.regen_level * 2  # 2 HP per level per second
            self.heal(regen_amount)
            self.regen_timer = 1000  # Regen every second
        
        # Update power-up timers
        expired_powerups = []
        for powerup_type, timer in self.powerup_timers.items():
            self.powerup_timers[powerup_type] = timer - dt
            if self.powerup_timers[powerup_type] <= 0:
                expired_powerups.append(powerup_type)
        
        # Remove expired power-ups
        for powerup_type in expired_powerups:
            del self.powerup_timers[powerup_type]
            if powerup_type == "damage":
                self.damage_multiplier = 1.0
            elif powerup_type == "speed":
                self.speed_multiplier = 1.0
        
        # Movement
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707
        
        # Apply movement with upgrades
        total_speed_multiplier = self.speed_multiplier * self.base_speed_multiplier
        move_speed = self.speed * total_speed_multiplier * (dt / 1000.0)
        self.rect.x += dx * move_speed
        self.rect.y += dy * move_speed
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height))
    
    def shoot(self, camera_x=0.0, camera_y=0.0):
        # Get weapon-specific fire rate multiplier
        fire_rate_multiplier = self.weapon_system.get_fire_rate_multiplier(self.current_weapon)
        actual_shoot_delay = self.shoot_delay * self.shoot_delay_multiplier * fire_rate_multiplier
        
        if self.shoot_cooldown <= 0:
            # Get mouse position for direction
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Convert mouse coordinates to world coordinates
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y
            
            # Calculate angle to mouse in world space
            dx = world_mouse_x - self.rect.centerx
            dy = world_mouse_y - self.rect.centery
            angle = math.atan2(dy, dx)
            
            # Calculate base damage
            base_damage = int(20 * self.damage_multiplier * self.base_damage_multiplier)
            
            # Use weapon system to create projectiles
            projectiles = self.weapon_system.create_projectiles(
                self.current_weapon,
                self.rect.centerx,
                self.rect.centery,
                angle,
                base_damage,
                self
            )
            
            self.shoot_cooldown = actual_shoot_delay
            return projectiles
        return []
    
    def take_damage(self, damage):
        # God mode check (if health is very high, assume god mode)
        if self.health > 9000:
            return
            
        if self.can_take_damage():
            # Shield absorbs damage first
            if self.shield_current > 0:
                shield_damage = min(damage, self.shield_current)
                self.shield_current -= shield_damage
                damage -= shield_damage
            
            # Apply remaining damage to health
            if damage > 0:
                self.health -= damage
                self.damage_cooldown = self.damage_delay
            
            # Clamp health
            self.health = max(0, self.health)
    
    def can_take_damage(self):
        return self.damage_cooldown <= 0
    
    def heal(self, amount):
        actual_max_health = self.max_health + self.max_health_bonus
        self.health = min(actual_max_health, self.health + amount)
    
    def apply_powerup(self, powerup_type, duration):
        self.powerup_timers[powerup_type] = duration
        
        if powerup_type == "damage":
            self.damage_multiplier = 2.0
        elif powerup_type == "speed":
            self.speed_multiplier = 1.5
        elif powerup_type == "health":
            self.heal(50)
    
    def draw(self, surface):
        # Draw player based on the provided pixel art reference
        center_x, center_y = self.rect.center
        
        # Determine if player is invincible (flashing effect)
        is_invincible = self.damage_cooldown > 0
        flash = is_invincible and (self.damage_cooldown % 200 < 100)
        
        if not flash:
            # Color palette from the reference image
            dark_gray = (40, 45, 52)
            med_gray = (68, 76, 88)
            light_gray = (120, 130, 140)
            skin_tone = (200, 160, 120)
            visor_blue = self.MINT_GREEN
            visor_dark = (40, 100, 140)
            accent_pink = (200, 80, 140)
            accent_cyan = (80, 200, 200)
            
            # Power-up color modifications
            if "damage" in self.powerup_timers:
                visor_blue = self.HOT_PINK
                accent_cyan = (255, 100, 180)
            elif "speed" in self.powerup_timers:
                visor_blue = self.MINT_GREEN
                accent_cyan = (100, 255, 150)
            
            # Scale factor for the character (reference appears to be about 20x30 pixels)
            scale = 1
            
            # Base position adjustments
            base_x = center_x
            base_y = center_y
            
            # 1. Legs (dark pants/armor)
            # Left leg
            pygame.draw.rect(surface, dark_gray, 
                           pygame.Rect(base_x - 6, base_y + 3, 5, 9))
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x - 5, base_y + 4, 3, 2))
            
            # Right leg  
            pygame.draw.rect(surface, dark_gray, 
                           pygame.Rect(base_x + 1, base_y + 3, 5, 9))
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x + 2, base_y + 4, 3, 2))
            
            # 2. Main torso (dark armor/suit)
            torso_main = pygame.Rect(base_x - 7, base_y - 8, 14, 15)
            pygame.draw.rect(surface, dark_gray, torso_main)
            
            # Chest armor details
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x - 6, base_y - 6, 12, 3))
            pygame.draw.rect(surface, light_gray, 
                           pygame.Rect(base_x - 5, base_y - 5, 10, 1))
            
            # Side torso accents
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x - 7, base_y - 3, 2, 6))
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x + 5, base_y - 3, 2, 6))
            
            # 3. Arms
            # Left arm
            pygame.draw.rect(surface, dark_gray, 
                           pygame.Rect(base_x - 10, base_y - 5, 4, 10))
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x - 9, base_y - 4, 2, 3))
            
            # Right arm (with cyan accent - energy weapon/tool)
            pygame.draw.rect(surface, dark_gray, 
                           pygame.Rect(base_x + 6, base_y - 5, 4, 10))
            pygame.draw.rect(surface, accent_cyan, 
                           pygame.Rect(base_x + 7, base_y - 2, 2, 4))
            
            # 4. Head/Helmet
            # Main helmet shape
            helmet_rect = pygame.Rect(base_x - 6, base_y - 15, 12, 10)
            pygame.draw.rect(surface, dark_gray, helmet_rect)
            
            # Helmet top/crown
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x - 5, base_y - 14, 10, 2))
            
            # Face/skin area
            pygame.draw.rect(surface, skin_tone, 
                           pygame.Rect(base_x - 3, base_y - 10, 6, 4))
            
            # Visor/eye area
            pygame.draw.rect(surface, visor_dark, 
                           pygame.Rect(base_x - 4, base_y - 12, 8, 3))
            pygame.draw.rect(surface, visor_blue, 
                           pygame.Rect(base_x - 3, base_y - 11, 6, 1))
            
            # Helmet side details
            pygame.draw.rect(surface, light_gray, 
                           pygame.Rect(base_x - 6, base_y - 12, 1, 4))
            pygame.draw.rect(surface, light_gray, 
                           pygame.Rect(base_x + 5, base_y - 12, 1, 4))
            
            # Small accent details
            if "damage" in self.powerup_timers:
                pygame.draw.rect(surface, accent_pink, 
                               pygame.Rect(base_x + 6, base_y - 8, 1, 2))
            
            # 5. Additional cybernetic details
            # Shoulder pads/armor
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x - 8, base_y - 7, 2, 3))
            pygame.draw.rect(surface, med_gray, 
                           pygame.Rect(base_x + 6, base_y - 7, 2, 3))
            
            # Belt/waist detail
            pygame.draw.rect(surface, light_gray, 
                           pygame.Rect(base_x - 5, base_y + 1, 10, 1))
            
            # Power indicators when powered up
            if "speed" in self.powerup_timers or "damage" in self.powerup_timers:
                # Glowing elements
                pygame.draw.rect(surface, accent_cyan, 
                               pygame.Rect(base_x - 1, base_y - 2, 2, 1))
                pygame.draw.rect(surface, accent_cyan, 
                               pygame.Rect(base_x - 1, base_y + 8, 2, 2))
    
    def get_health_percentage(self):
        actual_max_health = self.max_health + self.max_health_bonus
        return self.health / actual_max_health
    
    def apply_level_upgrade(self, upgrade_id, level_system):
        """Apply a level-up upgrade to the player"""
        if upgrade_id == "rapid_fire":
            self.shoot_delay_multiplier *= 0.75  # 25% faster
        elif upgrade_id == "double_shot":
            self.has_double_shot = True
        elif upgrade_id == "spread_shot":
            self.has_spread_shot = True
            self.spread_shot_level = level_system.get_upgrade_level("spread_shot")
        elif upgrade_id == "piercing_rounds":
            self.has_piercing = True
        elif upgrade_id == "explosive_rounds":
            self.has_explosive = True
        elif upgrade_id == "health_boost":
            self.max_health_bonus += 25
            self.heal(25)  # Also heal when taking health boost
        elif upgrade_id == "speed_boost":
            self.base_speed_multiplier *= 1.15  # 15% faster
        elif upgrade_id == "damage_boost":
            self.base_damage_multiplier *= 1.25  # 25% more damage
        elif upgrade_id == "regeneration":
            self.has_regeneration = True
            self.regen_level = level_system.get_upgrade_level("regeneration")
        elif upgrade_id == "shield":
            shield_level = level_system.get_upgrade_level("shield")
            self.shield_max = shield_level * 50  # 50 shield per level
            self.shield_current = self.shield_max  # Full shield on pickup
        elif upgrade_id == "area_damage":
            self.has_area_damage = True
            self.area_damage_level = level_system.get_upgrade_level("area_damage")
        elif upgrade_id == "auto_targeting":
            self.auto_targeting_level = level_system.get_upgrade_level("auto_targeting")
        elif upgrade_id == "laser_rifle":
            self.current_weapon = "laser_rifle"
        elif upgrade_id == "plasma_cannon":
            self.current_weapon = "plasma_cannon"
        elif upgrade_id == "shotgun":
            self.current_weapon = "shotgun"
        elif upgrade_id == "sniper_rifle":
            self.current_weapon = "sniper_rifle"
        elif upgrade_id == "machine_gun":
            self.current_weapon = "machine_gun"
        elif upgrade_id == "energy_beam":
            self.current_weapon = "energy_beam"
        elif upgrade_id == "orbital_missiles":
            self.orbital_missiles_level = level_system.get_upgrade_level("orbital_missiles")
        elif upgrade_id == "energy_shuriken":
            self.energy_shuriken_level = level_system.get_upgrade_level("energy_shuriken")
        elif upgrade_id == "laser_turret":
            self.laser_turret_level = level_system.get_upgrade_level("laser_turret")
        elif upgrade_id == "drone_companion":
            self.drone_companion_level = level_system.get_upgrade_level("drone_companion")
    
    def get_area_damage_info(self):
        """Get area damage info for game logic"""
        if self.has_area_damage and self.area_damage_timer <= 0:
            self.area_damage_timer = 2000  # Every 2 seconds
            damage = self.area_damage_level * 15  # 15 damage per level
            radius = 80 + (self.area_damage_level * 20)  # Increasing radius
            return damage, radius
        return None, None
    
    def get_auto_target_shot(self, enemies):
        """Get auto-targeting projectile if ready"""
        if self.auto_targeting_level > 0 and self.auto_target_timer <= 0:
            # Find nearest enemy
            nearest_enemy = None
            min_distance = float('inf')
            
            for enemy in enemies:
                dx = enemy.rect.centerx - self.rect.centerx
                dy = enemy.rect.centery - self.rect.centery
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy
            
            if nearest_enemy and min_distance < 400:  # Range limit
                # Calculate angle to enemy
                dx = nearest_enemy.rect.centerx - self.rect.centerx
                dy = nearest_enemy.rect.centery - self.rect.centery
                angle = math.atan2(dy, dx)
                
                # Create projectile with auto-targeting type
                damage = int(15 * self.auto_targeting_level * self.base_damage_multiplier)
                proj = Projectile(self.rect.centerx, self.rect.centery, angle, damage=damage, 
                                speed=600, weapon_type="auto_targeting", max_range=400)
                
                # Set cooldown based on level
                cooldown = max(800 - (self.auto_targeting_level * 200), 200)
                self.auto_target_timer = cooldown
                
                return proj
        return None
    
    def get_passive_attacks(self):
        """Get passive weapon attacks (missiles, shuriken, etc.)"""
        attacks = []
        
        # Orbital Missiles
        if self.orbital_missiles_level > 0 and self.missile_timer <= 0:
            missile_count = self.orbital_missiles_level
            for i in range(missile_count):
                angle = (i / missile_count) * 2 * math.pi
                # Missiles spawn around player and seek targets
                missile = {
                    "type": "missile",
                    "x": self.rect.centerx + math.cos(angle) * 30,
                    "y": self.rect.centery + math.sin(angle) * 30,
                    "damage": 25 * self.orbital_missiles_level,
                    "homing": True
                }
                attacks.append(missile)
            self.missile_timer = 3000  # Every 3 seconds
        
        # Laser Turret
        if self.laser_turret_level > 0 and self.turret_timer <= 0:
            laser = {
                "type": "laser",
                "x": self.rect.centerx,
                "y": self.rect.centery - 20,  # Shoulder mounted
                "damage": 8 * self.laser_turret_level,
                "continuous": True
            }
            attacks.append(laser)
            self.turret_timer = 100 * (4 - self.laser_turret_level)  # Faster with level
        
        # Combat Drone
        if self.drone_companion_level > 0 and self.drone_timer <= 0:
            drone_count = self.drone_companion_level
            for i in range(drone_count):
                drone = {
                    "type": "drone_shot",
                    "x": self.rect.centerx + (i * 40) - 20,
                    "y": self.rect.centery + 30,
                    "damage": 12 * self.drone_companion_level,
                    "auto_aim": True
                }
                attacks.append(drone)
            self.drone_timer = 1500  # Every 1.5 seconds
        
        return attacks
    
    def draw_passive_weapons(self, surface):
        """Draw orbiting shuriken and other passive visual effects"""
        center_x, center_y = self.rect.center
        
        # Energy Shuriken
        if self.energy_shuriken_level > 0:
            for i in range(self.energy_shuriken_level):
                angle = self.shuriken_angle + (i * 2 * math.pi / self.energy_shuriken_level)
                radius = 40 + (i * 10)
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                
                # Draw spinning shuriken
                points = []
                for j in range(6):  # 6-pointed star
                    star_angle = angle * 3 + (j * math.pi / 3)  # Spin 3x faster
                    if j % 2 == 0:
                        r = 8
                    else:
                        r = 4
                    points.append((
                        x + math.cos(star_angle) * r,
                        y + math.sin(star_angle) * r
                    ))
                
                if len(points) >= 3:
                    pygame.draw.polygon(surface, self.CYAN, points)
        
        # Combat Drone indicator
        if self.drone_companion_level > 0:
            for i in range(self.drone_companion_level):
                drone_x = center_x + (i * 40) - 20
                drone_y = center_y + 30
                
                # Simple drone representation
                pygame.draw.circle(surface, self.ELECTRIC_BLUE, (int(drone_x), int(drone_y)), 6)
                pygame.draw.circle(surface, self.WHITE, (int(drone_x), int(drone_y)), 3) 