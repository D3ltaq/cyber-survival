import pygame
import math
import random
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
        self.speed = 180  # pixels per second (reduced from 300 for better balance)
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
        
        # Animation properties
        self.animation_timer = 0
        self.walk_cycle = 0
        self.is_moving = False
        self.facing_direction = 0  # 0 = right, 1 = left, 2 = up, 3 = down
        self.last_movement = (0, 0)
        
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
        
        # Cybernetic Implants (new passive upgrades)
        self.has_night_vision = False  # Could be used to detect stealth enemies
        self.night_vision_level = 0
        self.has_neural_link = False  # Reduces cooldowns
        self.neural_link_level = 0
        self.has_cyber_armor = False  # Increases damage resistance
        self.cyber_armor_level = 0
        self.damage_reduction = 1.0  # Multiplier for incoming damage
        
    def update(self, keys, dt, screen_width, screen_height):
        # Update timers
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.damage_cooldown = max(0, self.damage_cooldown - dt)
        self.regen_timer = max(0, self.regen_timer - dt)
        self.area_damage_timer = max(0, self.area_damage_timer - dt)
        
        # Update animation
        self.animation_timer += dt
        
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
            elif powerup_type == "overclock":
                self.shoot_delay_multiplier = 1.0
        
        # Apply neural link effect (reduces cooldowns)
        if self.has_neural_link:
            neural_link_reduction = 1.0 - (self.neural_link_level * 0.05)  # 5% reduction per level
            self.shoot_delay_multiplier = min(self.shoot_delay_multiplier, neural_link_reduction)
        
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
        
        # Update movement state and facing direction
        self.is_moving = (dx != 0 or dy != 0)
        if self.is_moving:
            # Update facing direction based on movement
            if abs(dx) > abs(dy):
                self.facing_direction = 0 if dx > 0 else 1  # Right or Left
            else:
                self.facing_direction = 3 if dy > 0 else 2  # Down or Up
            
            # Update walk cycle
            self.walk_cycle += dt * 0.01  # Walking animation speed
        
        self.last_movement = (dx, dy)
        
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
        if self.health > 999:
            return False
        
        # Apply damage reduction from cyber armor
        if self.has_cyber_armor:
            self.damage_reduction = 1.0 - (self.cyber_armor_level * 0.1)  # 10% reduction per level
            damage = int(damage * self.damage_reduction)
        
        if self.damage_cooldown <= 0:
            # Damage shield first if available
            if self.shield_current > 0:
                shield_damage = min(damage, self.shield_current)
                self.shield_current -= shield_damage
                damage -= shield_damage
            
            if damage > 0:
                self.health -= damage
                self.damage_cooldown = self.damage_delay
            
            if self.health <= 0:
                return True  # Player died
            return False  # Player survived
        return False  # No damage taken due to cooldown
    
    def can_take_damage(self):
        """Check if player can take damage"""
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
        # Draw enhanced player with animations and effects
        center_x, center_y = self.rect.center
        
        # Determine if player is invincible (flashing effect)
        is_invincible = self.damage_cooldown > 0
        flash = is_invincible and (self.damage_cooldown % 200 < 100)
        
        # Draw shield effect first (behind player)
        if self.shield_current > 0:
            self._draw_shield_effect(surface, center_x, center_y)
        
        # Draw energy aura for powered-up states
        if "damage" in self.powerup_timers or "speed" in self.powerup_timers:
            self._draw_power_aura(surface, center_x, center_y)
        
        if not flash:
            self._draw_detailed_player(surface, center_x, center_y)
        else:
            # Draw damage sparks when hit
            if is_invincible:
                for _ in range(5):  # Draw random sparks
                    spark_x = center_x + random.randint(-10, 10)
                    spark_y = center_y + random.randint(-10, 10)
                    pygame.draw.line(surface, (255, 200, 0), (spark_x, spark_y), 
                                    (spark_x + random.randint(-5, 5), spark_y + random.randint(-5, 5)), 2)
    
    def _draw_detailed_player(self, surface, center_x, center_y):
        """Draw detailed animated cyberpunk player character"""
        # Scale factor to make character bigger
        scale = 1.5
        
        # Color palette - more sophisticated cyberpunk colors
        base_armor = (25, 30, 40)
        armor_highlight = (45, 55, 70)
        armor_detail = (80, 90, 110)
        energy_core = (0, 255, 200)
        visor_glow = (100, 200, 255)
        skin_tone = (220, 180, 140)
        metal_accent = (150, 160, 180)
        warning_red = (255, 80, 80)
        
        # Power-up color modifications
        if "damage" in self.powerup_timers:
            energy_core = (255, 100, 150)
            visor_glow = (255, 150, 200)
        elif "speed" in self.powerup_timers:
            energy_core = (150, 255, 100)
            visor_glow = (200, 255, 150)
        
        # Cybernetic implant visual modifications
        if self.has_night_vision:
            visor_glow = (100, 255, 100)  # Green glow for night vision
        elif self.has_neural_link:
            energy_core = (200, 100, 255)  # Purple core for neural link
        
        # Animation offsets (scaled)
        walk_offset = 0
        bob_offset = 0
        if self.is_moving:
            walk_offset = int(math.sin(self.walk_cycle) * 3 * scale)
            bob_offset = int(math.sin(self.walk_cycle * 2) * 1.5 * scale)
        
        # Breathing animation when idle with enhanced effect
        if not self.is_moving:
            bob_offset = int(math.sin(self.animation_timer * 0.003) * 1.2 * scale)  # More pronounced breathing
        
        # Shooting animation for right arm
        shoot_offset = 0
        shoot_angle_adjust = 0
        if self.shoot_cooldown > 0:
            shoot_offset = int(math.sin(self.shoot_cooldown * 0.1) * 2 * scale)  # Recoil effect
            shoot_angle_adjust = 0.2  # Slight forward lean during shooting for combat stance
        
        # Base position with animation
        base_x = center_x
        base_y = center_y + bob_offset
        
        # Adjust torso tilt based on direction for more dynamic movement
        torso_tilt = 0
        if self.is_moving:
            if self.facing_direction == 0:  # Right
                torso_tilt = int(math.sin(self.walk_cycle) * 1 * scale)
            elif self.facing_direction == 1:  # Left
                torso_tilt = -int(math.sin(self.walk_cycle) * 1 * scale)
            elif self.facing_direction == 2:  # Up
                torso_tilt = -int(math.sin(self.walk_cycle) * 0.5 * scale)
            elif self.facing_direction == 3:  # Down
                torso_tilt = int(math.sin(self.walk_cycle) * 0.5 * scale)
        
        # 1. Realistic shaped shadow (like enemies)
        self.draw_shadow(surface, center_x, center_y)
        
        # 2. Legs with walking animation (scaled) and directional adjustment
        leg_offset = walk_offset if self.is_moving else 0
        leg_width = int(4 * scale)
        leg_height = int(10 * scale)
        leg_spread = int(4 * scale)  # Default spread between legs
        if self.facing_direction == 2:  # Facing up, legs closer together
            leg_spread = int(3 * scale)
        elif self.facing_direction == 3:  # Facing down, legs slightly wider
            leg_spread = int(5 * scale)
        
        # Left leg
        left_leg_x = base_x - leg_spread
        if self.facing_direction == 0:  # Right
            left_leg_x += leg_offset
        elif self.facing_direction == 1:  # Left
            left_leg_x -= leg_offset
        elif self.facing_direction == 2:  # Up
            left_leg_x -= leg_offset * 0.5  # Reduced offset for up/down movement
        elif self.facing_direction == 3:  # Down
            left_leg_x += leg_offset * 0.5  # Reduced offset for up/down movement
        pygame.draw.rect(surface, base_armor, 
                        pygame.Rect(left_leg_x - leg_width//2, base_y + int(4 * scale), leg_width, leg_height))
        pygame.draw.rect(surface, armor_highlight, 
                        pygame.Rect(left_leg_x - int(1 * scale), base_y + int(5 * scale), int(2 * scale), int(3 * scale)))
        pygame.draw.rect(surface, energy_core, 
                        pygame.Rect(left_leg_x, base_y + int(7 * scale), int(1 * scale), int(1 * scale)))
        # Add cybernetic circuit lines on legs with glow
        pygame.draw.line(surface, energy_core, (left_leg_x - int(1 * scale), base_y + int(6 * scale)), 
                        (left_leg_x - int(1 * scale), base_y + int(10 * scale)), int(1 * scale))
        pygame.draw.line(surface, energy_core, (left_leg_x + int(1 * scale), base_y + int(8 * scale)), 
                        (left_leg_x + int(1 * scale), base_y + int(12 * scale)), int(1 * scale))
        
        # Right leg
        right_leg_x = base_x + leg_spread
        if self.facing_direction == 0:  # Right
            right_leg_x -= leg_offset
        elif self.facing_direction == 1:  # Left
            right_leg_x += leg_offset
        elif self.facing_direction == 2:  # Up
            right_leg_x += leg_offset * 0.5  # Reduced offset for up/down movement
        elif self.facing_direction == 3:  # Down
            right_leg_x -= leg_offset * 0.5  # Reduced offset for up/down movement
        pygame.draw.rect(surface, base_armor, 
                        pygame.Rect(right_leg_x - leg_width//2, base_y + int(4 * scale), leg_width, leg_height))
        pygame.draw.rect(surface, armor_highlight, 
                        pygame.Rect(right_leg_x - int(1 * scale), base_y + int(5 * scale), int(2 * scale), int(3 * scale)))
        pygame.draw.rect(surface, energy_core, 
                        pygame.Rect(right_leg_x, base_y + int(7 * scale), int(1 * scale), int(1 * scale)))
        # Add cybernetic circuit lines on legs with glow
        pygame.draw.line(surface, energy_core, (right_leg_x + int(1 * scale), base_y + int(6 * scale)), 
                        (right_leg_x + int(1 * scale), base_y + int(10 * scale)), int(1 * scale))
        pygame.draw.line(surface, energy_core, (right_leg_x - int(1 * scale), base_y + int(8 * scale)), 
                        (right_leg_x - int(1 * scale), base_y + int(12 * scale)), int(1 * scale))
        
        # 3. Main torso - more detailed (scaled) with directional tilt
        # Core body
        torso_width = int(12 * scale)
        torso_height = int(12 * scale)
        torso_y = base_y - int(6 * scale) + torso_tilt
        torso_rect = pygame.Rect(base_x - torso_width//2, torso_y, torso_width, torso_height)
        pygame.draw.rect(surface, base_armor, torso_rect)
        
        # Chest plate with energy core
        chest_width = int(10 * scale)
        chest_height = int(6 * scale)
        chest_rect = pygame.Rect(base_x - chest_width//2, torso_y + int(1 * scale), chest_width, chest_height)
        pygame.draw.rect(surface, armor_highlight, chest_rect)
        
        # Energy core in chest - pulsing with more detail
        core_intensity = int(128 + 127 * math.sin(self.animation_timer * 0.01))
        core_radius = int(2 * scale)
        inner_core_radius = int(1 * scale)
        pygame.draw.circle(surface, energy_core, (base_x, torso_y + int(4 * scale)), core_radius)
        pygame.draw.circle(surface, (255, 255, 255), (base_x, torso_y + int(4 * scale)), inner_core_radius)
        # Add radiating lines from core for enhanced effect
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            start_x = base_x + math.cos(rad) * core_radius
            start_y = torso_y + int(4 * scale) + math.sin(rad) * core_radius
            end_x = base_x + math.cos(rad) * (core_radius + 2 * scale)
            end_y = torso_y + int(4 * scale) + math.sin(rad) * (core_radius + 2 * scale)
            pygame.draw.line(surface, energy_core, (start_x, start_y), (end_x, end_y), 1)
        
        # Side armor panels with cybernetic details
        panel_width = int(2 * scale)
        panel_height = int(4 * scale)
        pygame.draw.rect(surface, armor_detail, 
                        pygame.Rect(base_x - int(6 * scale), torso_y + int(4 * scale), panel_width, panel_height))
        pygame.draw.rect(surface, armor_detail, 
                        pygame.Rect(base_x + int(4 * scale), torso_y + int(4 * scale), panel_width, panel_height))
        # Add glowing circuit lines on panels
        pygame.draw.line(surface, energy_core, (base_x - int(5 * scale), torso_y + int(5 * scale)), 
                        (base_x - int(5 * scale), torso_y + int(7 * scale)), 1)
        pygame.draw.line(surface, energy_core, (base_x + int(5 * scale), torso_y + int(5 * scale)), 
                        (base_x + int(5 * scale), torso_y + int(7 * scale)), 1)
        # Additional circuit detail on panels
        pygame.draw.line(surface, energy_core, (base_x - int(5 * scale), torso_y + int(6 * scale)), 
                        (base_x - int(4 * scale), torso_y + int(6 * scale)), 1)
        pygame.draw.line(surface, energy_core, (base_x + int(5 * scale), torso_y + int(6 * scale)), 
                        (base_x + int(4 * scale), torso_y + int(6 * scale)), 1)
        
        # Additional armor plating if cyber armor is active
        if self.has_cyber_armor:
            extra_armor_width = int(3 * scale)
            extra_armor_height = int(2 * scale)
            pygame.draw.rect(surface, metal_accent, 
                            pygame.Rect(base_x - int(7 * scale), torso_y + int(2 * scale), extra_armor_width, extra_armor_height))
            pygame.draw.rect(surface, metal_accent, 
                            pygame.Rect(base_x + int(4 * scale), torso_y + int(2 * scale), extra_armor_width, extra_armor_height))
            # Add detail to extra armor
            pygame.draw.rect(surface, armor_highlight, 
                            pygame.Rect(base_x - int(6 * scale), torso_y + int(3 * scale), int(1 * scale), int(1 * scale)))
            pygame.draw.rect(surface, armor_highlight, 
                            pygame.Rect(base_x + int(5 * scale), torso_y + int(3 * scale), int(1 * scale), int(1 * scale)))
        
        # 4. Arms with weapon positioning (scaled)
        arm_angle = 0
        if self.is_moving and self.facing_direction in [0, 1]:  # Moving horizontally
            arm_angle = math.sin(self.walk_cycle * 1.5) * 0.3
        arm_angle += shoot_angle_adjust  # Adjust arm angle during shooting for combat stance
        
        # Adjust arm positions based on facing direction
        left_arm_offset_x = -int(8 * scale)
        right_arm_offset_x = int(5 * scale)
        if self.facing_direction == 2:  # Facing up, arms closer to body
            left_arm_offset_x = -int(6 * scale)
            right_arm_offset_x = int(3 * scale)
        elif self.facing_direction == 3:  # Facing down, arms slightly outward
            left_arm_offset_x = -int(9 * scale)
            right_arm_offset_x = int(8 * scale)
        
        # Left arm
        arm_width = int(3 * scale)
        arm_height = int(8 * scale)
        left_arm_x = base_x + left_arm_offset_x + int(math.sin(arm_angle) * 2 * scale)
        left_arm_y = base_y - int(3 * scale) + int(math.cos(arm_angle) * 1 * scale)
        pygame.draw.rect(surface, base_armor, 
                        pygame.Rect(left_arm_x, left_arm_y, arm_width, arm_height))
        pygame.draw.rect(surface, armor_highlight, 
                        pygame.Rect(left_arm_x, left_arm_y, int(2 * scale), int(3 * scale)))
        # Add cybernetic detail to arm with multiple lines
        pygame.draw.line(surface, energy_core, (left_arm_x + int(1 * scale), left_arm_y + int(4 * scale)), 
                        (left_arm_x + int(1 * scale), left_arm_y + int(6 * scale)), 1)
        pygame.draw.line(surface, energy_core, (left_arm_x + int(2 * scale), left_arm_y + int(5 * scale)), 
                        (left_arm_x + int(2 * scale), left_arm_y + int(7 * scale)), 1)
        # Add mechanical joint
        pygame.draw.circle(surface, metal_accent, (left_arm_x + int(1.5 * scale), left_arm_y + int(3 * scale)), int(1 * scale))
        
        # Right arm (weapon arm) with shooting animation
        right_arm_x = base_x + right_arm_offset_x - int(math.sin(arm_angle) * 2 * scale)
        right_arm_y = base_y - int(3 * scale) - int(math.cos(arm_angle) * 1 * scale) - shoot_offset
        pygame.draw.rect(surface, base_armor, 
                        pygame.Rect(right_arm_x, right_arm_y, arm_width, arm_height))
        pygame.draw.rect(surface, armor_highlight, 
                        pygame.Rect(right_arm_x + int(1 * scale), right_arm_y, int(2 * scale), int(3 * scale)))
        # Add cybernetic detail to arm with multiple lines
        pygame.draw.line(surface, energy_core, (right_arm_x + int(1 * scale), right_arm_y + int(4 * scale)), 
                        (right_arm_x + int(1 * scale), right_arm_y + int(6 * scale)), 1)
        pygame.draw.line(surface, energy_core, (right_arm_x + int(2 * scale), right_arm_y + int(5 * scale)), 
                        (right_arm_x + int(2 * scale), right_arm_y + int(7 * scale)), 1)
        # Add mechanical joint
        pygame.draw.circle(surface, metal_accent, (right_arm_x + int(1.5 * scale), right_arm_y + int(3 * scale)), int(1 * scale))
        
        # Weapon mount on right arm with shooting flash
        weapon_mount_y = right_arm_y + int(2 * scale)
        if self.facing_direction == 2:  # Facing up, weapon higher
            weapon_mount_y = right_arm_y + int(1 * scale)
        elif self.facing_direction == 3:  # Facing down, weapon lower
            weapon_mount_y = right_arm_y + int(3 * scale)
        pygame.draw.rect(surface, metal_accent, 
                        pygame.Rect(right_arm_x + int(1 * scale), weapon_mount_y, int(2 * scale), int(3 * scale)))
        pygame.draw.rect(surface, energy_core, 
                        pygame.Rect(right_arm_x + int(1 * scale), weapon_mount_y + int(1 * scale), int(1 * scale), int(1 * scale)))
        if self.shoot_cooldown > 0 and self.shoot_cooldown < 50:  # Flash effect when shooting
            pygame.draw.rect(surface, (255, 255, 100), 
                            pygame.Rect(right_arm_x + int(1 * scale), weapon_mount_y + int(2 * scale), int(2 * scale), int(2 * scale)))
        
        # 5. Head/Helmet - more detailed (scaled) with directional adjustment
        # Main helmet
        helmet_width = int(10 * scale)
        helmet_height = int(8 * scale)
        helmet_y = base_y - int(12 * scale) + torso_tilt
        if self.facing_direction == 2:  # Facing up, head tilted back
            helmet_y -= int(1 * scale)
        elif self.facing_direction == 3:  # Facing down, head tilted forward
            helmet_y += int(1 * scale)
        helmet_rect = pygame.Rect(base_x - helmet_width//2, helmet_y, helmet_width, helmet_height)
        pygame.draw.rect(surface, base_armor, helmet_rect)
        
        # Helmet ridge
        ridge_width = int(8 * scale)
        ridge_height = int(2 * scale)
        pygame.draw.rect(surface, armor_highlight, 
                        pygame.Rect(base_x - ridge_width//2, helmet_y + int(1 * scale), ridge_width, ridge_height))
        
        # Visor - animated glow
        visor_width = int(8 * scale)
        visor_height = int(3 * scale)
        visor_rect = pygame.Rect(base_x - visor_width//2, helmet_y + int(2 * scale), visor_width, visor_height)
        pygame.draw.rect(surface, (20, 40, 60), visor_rect)
        
        # Visor glow effect with enhanced pulsing
        glow_intensity = int(100 + 50 * math.sin(self.animation_timer * 0.008))  # Faster pulse
        glow_width = int(6 * scale)
        glow_height = int(1 * scale)
        pygame.draw.rect(surface, visor_glow, 
                        pygame.Rect(base_x - glow_width//2, helmet_y + int(3 * scale), glow_width, glow_height))
        # Add secondary glow line for more tech look
        pygame.draw.rect(surface, visor_glow, 
                        pygame.Rect(base_x - glow_width//2, helmet_y + int(4 * scale), glow_width, int(0.5 * scale)))
        
        # Helmet details with cybernetic enhancements
        detail_width = int(1 * scale)
        detail_height = int(3 * scale)
        pygame.draw.rect(surface, metal_accent, 
                        pygame.Rect(base_x - int(5 * scale), helmet_y + int(4 * scale), detail_width, detail_height))
        pygame.draw.rect(surface, metal_accent, 
                        pygame.Rect(base_x + int(4 * scale), helmet_y + int(4 * scale), detail_width, detail_height))
        # Add small glowing dots for tech effect
        pygame.draw.rect(surface, energy_core, 
                        pygame.Rect(base_x - int(5 * scale), helmet_y + int(5 * scale), int(0.5 * scale), int(0.5 * scale)))
        pygame.draw.rect(surface, energy_core, 
                        pygame.Rect(base_x + int(4 * scale), helmet_y + int(5 * scale), int(0.5 * scale), int(0.5 * scale)))
        
        # Antenna/sensors with directional adjustment
        antenna_height = int(3 * scale)
        antenna_base_x = base_x + int(3 * scale)
        antenna_base_y = helmet_y
        if self.facing_direction == 1:  # Facing left, antenna on other side
            antenna_base_x = base_x - int(3 * scale)
        pygame.draw.line(surface, metal_accent, (antenna_base_x, antenna_base_y), 
                        (antenna_base_x, antenna_base_y - antenna_height), int(1 * scale))
        # Add glowing tip to antenna
        pygame.draw.rect(surface, energy_core, 
                        pygame.Rect(antenna_base_x - int(0.5 * scale), antenna_base_y - antenna_height - int(1 * scale), 
                                    int(1 * scale), int(1 * scale)))
    
    def _draw_shield_effect(self, surface, center_x, center_y):
        """Draw shield visual effect around player"""
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Shield strength determines visual intensity
        shield_percentage = self.shield_current / self.shield_max if self.shield_max > 0 else 0
        
        # Pulsing shield effect
        pulse = abs(math.sin(current_time * 0.005)) * 0.5 + 0.5
        shield_alpha = int(80 * shield_percentage * pulse)
        
        # Multiple shield layers for depth
        for layer in range(3):
            radius = 20 + layer * 3
            layer_alpha = max(20, shield_alpha - layer * 20)
            
            # Create shield color (cyan-blue)
            shield_color = (self.CYAN[0], self.CYAN[1], self.CYAN[2])
            
            # Draw shield ring
            pygame.draw.circle(surface, shield_color, (int(center_x), int(center_y)), radius, 2)
        
        # Shield energy sparks
        if shield_percentage > 0.5:
            for i in range(6):
                angle = (current_time * 0.01 + i * math.pi / 3) % (2 * math.pi)
                spark_x = center_x + math.cos(angle) * 22
                spark_y = center_y + math.sin(angle) * 22
                pygame.draw.circle(surface, (255, 255, 255), (int(spark_x), int(spark_y)), 1)
    
    def _draw_power_aura(self, surface, center_x, center_y):
        """Draw power-up aura around player"""
        import time
        current_time = time.time() * 1000
        
        # Determine aura color based on power-up type
        if "damage" in self.powerup_timers:
            aura_color = self.HOT_PINK
        elif "speed" in self.powerup_timers:
            aura_color = self.MINT_GREEN
        else:
            aura_color = self.ELECTRIC_BLUE
        
        # Pulsing aura effect
        pulse = math.sin(current_time * 0.008) * 0.4 + 0.6
        
        # Multiple aura layers
        for layer in range(4):
            radius = int((25 + layer * 5) * pulse)
            layer_alpha = max(10, int(40 - layer * 8))
            
            # Create semi-transparent surface for aura
            aura_surf = pygame.Surface((radius * 2, radius * 2))
            aura_surf.set_alpha(layer_alpha)
            aura_surf.fill(aura_color)
            
            # Draw as circle
            pygame.draw.circle(aura_surf, aura_color, (radius, radius), radius)
            surface.blit(aura_surf, (center_x - radius, center_y - radius))
        
        # Energy particles around player
        for i in range(8):
            angle = (current_time * 0.01 + i * math.pi / 4) % (2 * math.pi)
            particle_distance = 30 + math.sin(current_time * 0.01 + i) * 5
            particle_x = center_x + math.cos(angle) * particle_distance
            particle_y = center_y + math.sin(angle) * particle_distance
            
            particle_size = 2 + int(math.sin(current_time * 0.015 + i) * 1)
            pygame.draw.circle(surface, (255, 255, 255), (int(particle_x), int(particle_y)), particle_size)
    
    def get_health_percentage(self):
        actual_max_health = self.max_health + self.max_health_bonus
        return self.health / actual_max_health
    
    def apply_level_upgrade(self, upgrade_id, level_system):
        # Weapon upgrades
        if upgrade_id == "rapid_fire":
            self.shoot_delay_multiplier *= 0.8  # 20% faster firing
            if self.shoot_delay_multiplier < 0.4:  # Cap at 60% reduction
                if "rapid_fire" in level_system.available_upgrades:
                    del level_system.available_upgrades["rapid_fire"]
        elif upgrade_id == "double_shot":
            self.has_double_shot = True
            if "double_shot" in level_system.available_upgrades:
                del level_system.available_upgrades["double_shot"]
        elif upgrade_id == "spread_shot":
            self.has_spread_shot = True
            self.spread_shot_level += 1
            if self.spread_shot_level >= 3 and "spread_shot" in level_system.available_upgrades:
                del level_system.available_upgrades["spread_shot"]
        elif upgrade_id == "piercing":
            self.has_piercing = True
            if "piercing" in level_system.available_upgrades:
                del level_system.available_upgrades["piercing"]
        elif upgrade_id == "explosive":
            self.has_explosive = True
            if "explosive" in level_system.available_upgrades:
                del level_system.available_upgrades["explosive"]
        # New weapons
        elif upgrade_id in self.weapon_system.get_all_weapon_types():
            self.current_weapon = upgrade_id
            if upgrade_id in level_system.available_upgrades:
                del level_system.available_upgrades[upgrade_id]
        # Passive weapons
        elif upgrade_id == "auto_targeting":
            self.auto_targeting_level += 1
            if self.auto_targeting_level >= 3 and "auto_targeting" in level_system.available_upgrades:
                del level_system.available_upgrades["auto_targeting"]
        elif upgrade_id == "orbital_missiles":
            self.orbital_missiles_level += 1
            if self.orbital_missiles_level >= 3 and "orbital_missiles" in level_system.available_upgrades:
                del level_system.available_upgrades["orbital_missiles"]
        elif upgrade_id == "energy_shuriken":
            self.energy_shuriken_level += 1
            if self.energy_shuriken_level >= 3 and "energy_shuriken" in level_system.available_upgrades:
                del level_system.available_upgrades["energy_shuriken"]
        elif upgrade_id == "laser_turret":
            self.laser_turret_level += 1
            if self.laser_turret_level >= 3 and "laser_turret" in level_system.available_upgrades:
                del level_system.available_upgrades["laser_turret"]
        elif upgrade_id == "drone_companion":
            self.drone_companion_level += 1
            if self.drone_companion_level >= 3 and "drone_companion" in level_system.available_upgrades:
                del level_system.available_upgrades["drone_companion"]
        # Character upgrades
        elif upgrade_id == "health_boost":
            self.max_health_bonus += 20
            self.max_health += 20
            self.health += 20
            if self.max_health_bonus >= 100 and "health_boost" in level_system.available_upgrades:
                del level_system.available_upgrades["health_boost"]
        elif upgrade_id == "speed_boost":
            self.base_speed_multiplier += 0.1  # 10% speed increase
            if self.base_speed_multiplier >= 1.5 and "speed_boost" in level_system.available_upgrades:  # Cap at 50% increase
                del level_system.available_upgrades["speed_boost"]
        elif upgrade_id == "damage_boost":
            self.base_damage_multiplier += 0.1  # 10% damage increase
            if self.base_damage_multiplier >= 1.5 and "damage_boost" in level_system.available_upgrades:  # Cap at 50% increase
                del level_system.available_upgrades["damage_boost"]
        elif upgrade_id == "regeneration":
            self.has_regeneration = True
            self.regen_level += 1
            if self.regen_level >= 3 and "regeneration" in level_system.available_upgrades:
                del level_system.available_upgrades["regeneration"]
        elif upgrade_id == "shield":
            self.shield_max += 20
            self.shield_current += 20
            if self.shield_max >= 100 and "shield" in level_system.available_upgrades:
                del level_system.available_upgrades["shield"]
        # Utility
        elif upgrade_id == "area_damage":
            self.has_area_damage = True
            self.area_damage_level += 1
            if self.area_damage_level >= 3 and "area_damage" in level_system.available_upgrades:
                del level_system.available_upgrades["area_damage"]
        elif upgrade_id == "time_dilation":
            level_system.apply_time_dilation(5000)  # 5 seconds
            if "time_dilation" in level_system.available_upgrades:
                del level_system.available_upgrades["time_dilation"]
        elif upgrade_id == "xp_magnet":
            level_system.xp_magnet_multiplier *= 2.0
            if "xp_magnet" in level_system.available_upgrades:
                del level_system.available_upgrades["xp_magnet"]
        # New cybernetic implants
        elif upgrade_id == "night_vision":
            self.has_night_vision = True
            self.night_vision_level += 1
            if self.night_vision_level >= 3 and "night_vision" in level_system.available_upgrades:
                del level_system.available_upgrades["night_vision"]
        elif upgrade_id == "neural_link":
            self.has_neural_link = True
            self.neural_link_level += 1
            if self.neural_link_level >= 3 and "neural_link" in level_system.available_upgrades:
                del level_system.available_upgrades["neural_link"]
        elif upgrade_id == "cyber_armor":
            self.has_cyber_armor = True
            self.cyber_armor_level += 1
            if self.cyber_armor_level >= 3 and "cyber_armor" in level_system.available_upgrades:
                del level_system.available_upgrades["cyber_armor"]
        # Temporary upgrades
        elif upgrade_id == "overclock":
            self.apply_powerup("overclock", 30000)  # 30 seconds duration
            self.shoot_delay_multiplier = 0.5  # 50% faster firing
            # Do not remove overclock from available upgrades as it can be reapplied
    
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
        # Cap auto-targeting level to prevent excessive firing
        effective_level = min(self.auto_targeting_level, 5)
        if effective_level > 0 and self.auto_target_timer <= 0:
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
                damage = int(15 * effective_level * self.base_damage_multiplier)
                proj = Projectile(self.rect.centerx, self.rect.centery, angle, damage=damage, 
                                speed=600, weapon_type="auto_targeting", max_range=400)
                
                # Set cooldown based on level - more reasonable scaling
                base_cooldown = 1000  # Base 1 second cooldown
                level_reduction = min(effective_level * 100, 600)  # Max 600ms reduction
                self.auto_target_timer = max(400, base_cooldown - level_reduction)  # Min 400ms cooldown
                
                return proj
        return None
    
    def get_passive_attacks(self):
        """Get passive weapon attacks (missiles, shuriken, etc.)"""
        attacks = []
        
        # Orbital Missiles
        if self.orbital_missiles_level > 0 and self.missile_timer <= 0:
            missile_count = min(self.orbital_missiles_level, 4)  # Cap at 4 missiles per volley
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
            # Faster firing with higher levels but reasonable limits
            base_cooldown = 2500  # Base 2.5 seconds
            level_reduction = min(self.orbital_missiles_level * 200, 1500)  # Max 1.5s reduction
            self.missile_timer = max(1000, base_cooldown - level_reduction)  # Min 1s cooldown
        
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
            # Proper timer calculation: faster with level but never too fast
            base_cooldown = 400  # Base 400ms cooldown
            level_reduction = min(self.laser_turret_level * 50, 300)  # Max 300ms reduction
            self.turret_timer = max(100, base_cooldown - level_reduction)  # Min 100ms cooldown
        
        # Combat Drone
        if self.drone_companion_level > 0 and self.drone_timer <= 0:
            drone_count = min(self.drone_companion_level, 3)  # Cap at 3 drones
            for i in range(drone_count):
                drone = {
                    "type": "drone_shot",
                    "x": self.rect.centerx + (i * 40) - 20,
                    "y": self.rect.centery + 30,
                    "damage": 12 * self.drone_companion_level,
                    "auto_aim": True
                }
                attacks.append(drone)
            # Faster firing with higher levels but reasonable limits
            base_cooldown = 1200  # Base 1.2 seconds
            level_reduction = min(self.drone_companion_level * 100, 700)  # Max 700ms reduction
            self.drone_timer = max(500, base_cooldown - level_reduction)  # Min 500ms cooldown
        
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
    
    def draw_shadow(self, surface, center_x, center_y):
        """Draw realistic shaped shadow for the player (same system as enemies)"""
        # Shadow offset (sun from South-West) - same as enemies
        shadow_offset_x = 4
        shadow_offset_y = 6
        shadow_alpha = 60
        shadow_color = (30, 30, 30)
        
        # Create shadow surface for armored soldier
        shadow_surf = pygame.Surface((30, 35))
        shadow_surf.set_alpha(shadow_alpha)
        shadow_surf.fill((0, 0, 0))
        shadow_surf.set_colorkey((0, 0, 0))
        
        # Head shadow
        pygame.draw.ellipse(shadow_surf, shadow_color, (10, 2, 10, 8))
        
        # Main torso shadow
        pygame.draw.ellipse(shadow_surf, shadow_color, (8, 8, 14, 12))
        
        # Arms shadows
        pygame.draw.ellipse(shadow_surf, shadow_color, (4, 10, 6, 8))  # Left arm
        pygame.draw.ellipse(shadow_surf, shadow_color, (20, 10, 6, 8))  # Right arm
        
        # Legs shadows
        pygame.draw.ellipse(shadow_surf, shadow_color, (9, 18, 5, 12))  # Left leg
        pygame.draw.ellipse(shadow_surf, shadow_color, (16, 18, 5, 12))  # Right leg
        
        # Weapon shadow extending from right arm
        pygame.draw.ellipse(shadow_surf, shadow_color, (24, 12, 8, 3))
        
        # Position shadow with offset
        shadow_x = center_x - shadow_surf.get_width() // 2 + shadow_offset_x
        shadow_y = center_y - shadow_surf.get_height() // 2 + shadow_offset_y
        
        surface.blit(shadow_surf, (shadow_x, shadow_y)) 