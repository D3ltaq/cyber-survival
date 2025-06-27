import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic", wave=1):
        super().__init__()
        self.enemy_type = enemy_type
        self.wave = wave  # Track which wave this enemy spawned in
        
        # Base properties (will be scaled by wave)
        if enemy_type == "basic":
            self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
            self.base_health = 30
            self.speed = 60
            self.damage = 15
            self.score_value = 10
            self.color = (255, 100, 100)  # Red
        elif enemy_type == "fast":
            self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
            self.base_health = 15
            self.speed = 90
            self.damage = 10
            self.score_value = 15
            self.color = (255, 255, 100)  # Yellow
        elif enemy_type == "tank":
            self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
            self.base_health = 80
            self.speed = 45  # Increased from 30 to 45
            self.damage = 25
            self.score_value = 30
            self.color = (100, 255, 100)  # Green
        elif enemy_type == "sniper":  # NEW: Long-range, slow but high damage
            self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
            self.base_health = 40
            self.speed = 40  # Increased from 25 to 40
            self.damage = 35
            self.score_value = 25
            self.color = (255, 165, 0)  # Orange
            self.ai_state = "sniper"
            self.sniper_range = 300
            self.attack_cooldown = 2000  # 2 seconds between attacks
            self.last_attack = 0
        elif enemy_type == "swarm":  # NEW: Fast, weak, appears in groups
            self.rect = pygame.Rect(x - 6, y - 6, 12, 12)
            self.base_health = 8
            self.speed = 120
            self.damage = 8
            self.score_value = 8
            self.color = (200, 255, 200)  # Light green
        elif enemy_type == "heavy":  # NEW: Very tanky, slow, high damage
            self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
            self.base_health = 150
            self.speed = 35  # Increased from 20 to 35
            self.damage = 40
            self.score_value = 50
            self.color = (150, 150, 255)  # Blue-ish
        elif enemy_type == "elite":  # NEW: Balanced but strong all-around
            self.rect = pygame.Rect(x - 14, y - 14, 28, 28)
            self.base_health = 100
            self.speed = 50
            self.damage = 30
            self.score_value = 40
            self.color = (255, 200, 100)  # Gold-ish
        elif enemy_type == "boss":
            self.rect = pygame.Rect(x - 25, y - 25, 50, 50)
            self.base_health = 200
            self.speed = 45
            self.damage = 40
            self.score_value = 100
            self.color = (255, 100, 255)  # Magenta
        
        # Apply wave scaling to stats
        self.apply_wave_scaling()
        
        # Required for pygame sprite
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        
        # AI behavior
        self.ai_timer = 0
        self.ai_state = getattr(self, 'ai_state', "chase")  # chase, circle, retreat, sniper
        self.circle_angle = random.uniform(0, 2 * math.pi)
        
        # Special abilities
        self.attack_cooldown = getattr(self, 'attack_cooldown', 0)
        self.last_attack = getattr(self, 'last_attack', 0)
        
        # Visual effects
        self.damage_flash = 0
        
        # Animation properties
        self.animation_timer = 0
        self.hover_offset = 0
        self.rotation_angle = 0
        self.pulse_timer = 0
        self.movement_trail = []  # For movement animation
        self.last_position = (self.rect.centerx, self.rect.centery)
        
        # Colors (New palette)
        self.CORAL = (255, 134, 178)
        self.CYAN = (108, 222, 255)
        self.MINT_GREEN = (108, 255, 222)
        self.MAGENTA = (222, 108, 255)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
    
    def apply_wave_scaling(self):
        """Scale enemy stats based on wave number for progressive difficulty"""
        # Health scaling: +15% per wave (compounds)
        health_multiplier = 1.0 + (self.wave - 1) * 0.15
        
        # Damage scaling: +10% per wave (compounds)
        damage_multiplier = 1.0 + (self.wave - 1) * 0.10
        
        # Speed scaling: +5% per wave (compounds, capped at 2x)
        speed_multiplier = min(2.0, 1.0 + (self.wave - 1) * 0.05)
        
        # Apply scaling
        self.max_health = int(self.base_health * health_multiplier)
        self.health = self.max_health
        self.damage = int(self.damage * damage_multiplier)
        self.speed = int(self.speed * speed_multiplier)
        
        # Bosses get extra scaling
        if self.enemy_type == "boss":
            self.max_health = int(self.max_health * 1.5)  # Extra health for bosses
            self.health = self.max_health
            self.score_value = int(self.score_value * (1 + self.wave * 0.2))  # More score for higher wave bosses
    
    def update(self, dt, player_pos):
        # Update timers
        self.ai_timer += dt
        self.damage_flash = max(0, self.damage_flash - dt)
        self.animation_timer += dt
        self.pulse_timer += dt
        
        # Update animation properties
        self.hover_offset = math.sin(self.animation_timer * 0.003) * 2
        self.rotation_angle += dt * 0.001  # Slow rotation for some enemies
        
        # Track movement for trail effects
        current_pos = (self.rect.centerx, self.rect.centery)
        if current_pos != self.last_position:
            self.movement_trail.append(current_pos)
            if len(self.movement_trail) > 5:  # Keep last 5 positions
                self.movement_trail.pop(0)
        self.last_position = current_pos
        
        # AI behavior
        self.update_ai(dt, player_pos)
        
        # Apply movement
        move_factor = dt / 1000.0
        self.rect.x += self.velocity_x * move_factor
        self.rect.y += self.velocity_y * move_factor
    
    def update_ai(self, dt, player_pos):
        player_x, player_y = player_pos
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance
            
            if self.enemy_type == "basic":
                # Simple chase behavior
                self.velocity_x = dx * self.speed
                self.velocity_y = dy * self.speed
                
            elif self.enemy_type == "fast":
                # Zigzag chase behavior
                if self.ai_timer % 1000 < 500:  # Change direction every 0.5 seconds
                    perpendicular_x = -dy
                    perpendicular_y = dx
                    self.velocity_x = (dx + perpendicular_x * 0.5) * self.speed
                    self.velocity_y = (dy + perpendicular_y * 0.5) * self.speed
                else:
                    self.velocity_x = (dx - dy * 0.5) * self.speed
                    self.velocity_y = (dy + dx * 0.5) * self.speed
                    
            elif self.enemy_type == "tank":
                # Slow but steady chase
                self.velocity_x = dx * self.speed
                self.velocity_y = dy * self.speed
                
            elif self.enemy_type == "sniper":
                # Sniper behavior: maintain distance, stay at range
                ideal_distance = 220
                if distance > ideal_distance + 40:
                    # Too far, move closer
                    self.velocity_x = dx * self.speed * 0.8  # Increased from 0.5
                    self.velocity_y = dy * self.speed * 0.8
                elif distance < ideal_distance - 40:
                    # Too close, retreat
                    self.velocity_x = -dx * self.speed
                    self.velocity_y = -dy * self.speed
                else:
                    # Perfect distance, strafe with some approach
                    perpendicular_x = -dy
                    perpendicular_y = dx
                    self.velocity_x = (perpendicular_x * 0.8 + dx * 0.2) * self.speed
                    self.velocity_y = (perpendicular_y * 0.8 + dy * 0.2) * self.speed
                    
            elif self.enemy_type == "swarm":
                # Swarm behavior: fast and erratic
                if self.ai_timer % 800 < 400:  # Change direction every 0.4 seconds
                    self.velocity_x = dx * self.speed + random.uniform(-20, 20)
                    self.velocity_y = dy * self.speed + random.uniform(-20, 20)
                else:
                    # Sometimes make sharp turns
                    turn_angle = random.uniform(-math.pi/4, math.pi/4)
                    rotated_dx = dx * math.cos(turn_angle) - dy * math.sin(turn_angle)
                    rotated_dy = dx * math.sin(turn_angle) + dy * math.cos(turn_angle)
                    self.velocity_x = rotated_dx * self.speed
                    self.velocity_y = rotated_dy * self.speed
                    
            elif self.enemy_type == "heavy":
                # Heavy behavior: slow and steady, can't be easily stopped
                self.velocity_x = dx * self.speed
                self.velocity_y = dy * self.speed
                
            elif self.enemy_type == "elite":
                # Elite behavior: smart tactical movement
                if distance > 120:
                    # Chase when far
                    self.velocity_x = dx * self.speed
                    self.velocity_y = dy * self.speed
                else:
                    # Circle when close - faster and more aggressive
                    self.circle_angle += dt * 0.006  # Doubled speed
                    circle_dx = math.cos(self.circle_angle)
                    circle_dy = math.sin(self.circle_angle)
                    self.velocity_x = (dx * 0.2 + circle_dx * 0.8) * self.speed
                    self.velocity_y = (dy * 0.2 + circle_dy * 0.8) * self.speed
                    
            elif self.enemy_type == "boss":
                # Complex AI: circle around player at medium distance
                ideal_distance = 130
                
                if distance < ideal_distance - 30:
                    # Too close, move away
                    self.velocity_x = -dx * self.speed
                    self.velocity_y = -dy * self.speed
                elif distance > ideal_distance + 30:
                    # Too far, move closer
                    self.velocity_x = dx * self.speed
                    self.velocity_y = dy * self.speed
                else:
                    # Perfect distance, circle around - faster movement
                    self.circle_angle += dt * 0.005  # Increased from 0.002
                    circle_dx = math.cos(self.circle_angle)
                    circle_dy = math.sin(self.circle_angle)
                    # Mix circling with slight approach for more dynamic movement
                    self.velocity_x = (circle_dx * 0.8 + dx * 0.2) * self.speed
                    self.velocity_y = (circle_dy * 0.8 + dy * 0.2) * self.speed
    
    def take_damage(self, damage):
        self.health -= damage
        self.damage_flash = 200  # Flash for 200ms
        
        # Clamp health
        self.health = max(0, self.health)
    
    def draw(self, surface):
        center_x, center_y = self.rect.center
        
        # Draw enemy glow/aura for higher waves or special types
        if self.wave >= 5 or self.enemy_type in ["boss", "elite"]:
            self._draw_elite_aura(surface, center_x, center_y)
        
        # Determine color based on type and damage flash
        draw_color = self.color
        if self.damage_flash > 0:
            draw_color = self.WHITE
        
        # Draw based on enemy type
        if self.enemy_type == "basic":
            self.draw_basic_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "fast":
            self.draw_fast_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "tank":
            self.draw_tank_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "sniper":
            self.draw_sniper_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "swarm":
            self.draw_swarm_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "heavy":
            self.draw_heavy_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "elite":
            self.draw_elite_enemy(surface, center_x, center_y, draw_color)
        elif self.enemy_type == "boss":
            self.draw_boss_enemy(surface, center_x, center_y, draw_color)
        
        # Draw health bar for damaged enemies
        if self.health < self.max_health:
            self.draw_health_bar(surface)
    
    def _draw_elite_aura(self, surface, center_x, center_y):
        """Draw aura for high-wave enemies or special types"""
        import time
        current_time = time.time() * 1000
        
        # Aura intensity based on wave and type
        if self.enemy_type == "boss":
            wave_factor = 1.0
            aura_color = (255, 100, 255)  # Magenta for bosses
        elif self.enemy_type == "elite":
            wave_factor = 0.8
            aura_color = (255, 200, 100)  # Gold for elite
        else:
            wave_factor = min(1.0, (self.wave - 5) / 10)  # Stronger aura for higher waves
            aura_color = (255, 150, 150)  # Red for high-wave enemies
        
        pulse = math.sin(current_time * 0.01) * 0.3 + 0.7
        
        # Draw aura rings
        for ring in range(2):
            radius = self.rect.width // 2 + 5 + ring * 3
            aura_alpha = int(40 * wave_factor * pulse)
            
            # Create aura surface
            aura_surf = pygame.Surface((radius * 2, radius * 2))
            aura_surf.set_alpha(aura_alpha)
            pygame.draw.circle(aura_surf, aura_color, (radius, radius), radius, 2)
            surface.blit(aura_surf, (center_x - radius, center_y - radius))
    
    def draw_basic_enemy(self, surface, center_x, center_y, color):
        """Enhanced basic cyborg drone with animations"""
        # Animation offsets
        hover_y = center_y + int(self.hover_offset)
        pulse_scale = 1.0 + math.sin(self.pulse_timer * 0.01) * 0.1
        
        # Color variations
        dark_metal = (40, 45, 50)
        light_metal = (120, 130, 140)
        energy_blue = (100, 150, 255)
        warning_red = (255, 100, 100)
        
        # Main chassis - hexagonal shape for more interesting design
        chassis_points = []
        for i in range(6):
            angle = i * math.pi / 3 + self.rotation_angle * 0.5
            x = center_x + math.cos(angle) * 8 * pulse_scale
            y = hover_y + math.sin(angle) * 8 * pulse_scale
            chassis_points.append((int(x), int(y)))
        pygame.draw.polygon(surface, dark_metal, chassis_points)
        pygame.draw.polygon(surface, color, chassis_points, 2)
        
        # Inner core - pulsing energy
        core_radius = int(4 * pulse_scale)
        pygame.draw.circle(surface, energy_blue, (center_x, hover_y), core_radius)
        pygame.draw.circle(surface, self.WHITE, (center_x, hover_y), core_radius - 1)
        pygame.draw.circle(surface, color, (center_x, hover_y), core_radius - 2)
        
        # Weapon systems - animated barrels
        barrel_extend = math.sin(self.animation_timer * 0.005) * 2
        
        # Left weapon
        left_barrel = pygame.Rect(center_x - 12 - barrel_extend, hover_y - 1, 6, 2)
        pygame.draw.rect(surface, light_metal, left_barrel)
        pygame.draw.rect(surface, energy_blue, 
                        pygame.Rect(center_x - 13 - barrel_extend, hover_y - 0.5, 2, 1))
        
        # Right weapon  
        right_barrel = pygame.Rect(center_x + 6 + barrel_extend, hover_y - 1, 6, 2)
        pygame.draw.rect(surface, light_metal, right_barrel)
        pygame.draw.rect(surface, energy_blue, 
                        pygame.Rect(center_x + 11 + barrel_extend, hover_y - 0.5, 2, 1))
        
        # Sensor arrays - blinking lights
        blink_on = (self.animation_timer % 1000) < 500
        sensor_color = energy_blue if blink_on else dark_metal
        
        # Top sensors
        pygame.draw.circle(surface, sensor_color, (center_x - 4, hover_y - 6), 1)
        pygame.draw.circle(surface, sensor_color, (center_x + 4, hover_y - 6), 1)
        
        # Side sensors
        pygame.draw.circle(surface, self.CYAN, (center_x - 8, hover_y), 1)
        pygame.draw.circle(surface, self.CYAN, (center_x + 8, hover_y), 1)
        
        # Thruster effects (bottom)
        pygame.draw.circle(surface, (50, 100, 200), (center_x, hover_y + 8), 2)
        pygame.draw.circle(surface, energy_blue, (center_x, hover_y + 8), 1)
        
        # Damage indicators
        if self.damage_flash > 0:
            flash_alpha = int(self.damage_flash * 0.3)
            for point in chassis_points:
                pygame.draw.circle(surface, warning_red, point, 2)
    
    def draw_fast_enemy(self, surface, center_x, center_y, color):
        """Enhanced fast reconnaissance cyborg with speed animations"""
        # Animation offsets - more aggressive movement
        hover_y = center_y + int(self.hover_offset * 1.5)
        speed_wobble = math.sin(self.animation_timer * 0.02) * 1.5
        
        # Color variations
        dark_metal = (30, 35, 45)
        light_metal = (140, 150, 160)
        speed_yellow = (255, 255, 100)
        energy_trail = (255, 200, 0)
        
        # Main body - streamlined diamond shape
        body_points = [
            (center_x, hover_y - 8),
            (center_x + 6 + speed_wobble, hover_y + 2),
            (center_x + 3, hover_y + 8),
            (center_x - 3, hover_y + 8),
            (center_x - 6 - speed_wobble, hover_y + 2)
        ]
        pygame.draw.polygon(surface, dark_metal, body_points)
        pygame.draw.polygon(surface, color, body_points, 2)
        
        # Speed trails behind the enemy
        for i, trail_pos in enumerate(self.movement_trail):
            if i < len(self.movement_trail) - 1:
                alpha = (i + 1) * 50
                trail_radius = 3 - i
                # Create temporary surface for alpha blending
                trail_surf = pygame.Surface((trail_radius * 2, trail_radius * 2))
                trail_surf.set_alpha(alpha)
                pygame.draw.circle(trail_surf, energy_trail, (trail_radius, trail_radius), trail_radius)
                surface.blit(trail_surf, (trail_pos[0] - trail_radius, trail_pos[1] - trail_radius))
        
        # Head/scanner - rotating
        scanner_angle = self.rotation_angle * 2
        scanner_x = center_x + math.cos(scanner_angle) * 2
        scanner_y = hover_y - 4 + math.sin(scanner_angle) * 1
        
        pygame.draw.circle(surface, dark_metal, (center_x, hover_y - 4), 4)
        pygame.draw.circle(surface, color, (center_x, hover_y - 4), 4, 1)
        
        # Scanning eye - moving
        pygame.draw.circle(surface, speed_yellow, (int(scanner_x), int(scanner_y)), 2)
        pygame.draw.circle(surface, self.WHITE, (int(scanner_x), int(scanner_y)), 1)
        
        # Wing thrusters - animated
        thruster_pulse = math.sin(self.animation_timer * 0.03)
        left_thruster_x = center_x - 4 + thruster_pulse
        right_thruster_x = center_x + 4 - thruster_pulse
        
        # Thruster flames
        pygame.draw.line(surface, energy_trail, 
                        (left_thruster_x, hover_y + 6), 
                        (left_thruster_x - 4, hover_y + 12), 3)
        pygame.draw.line(surface, energy_trail, 
                        (right_thruster_x, hover_y + 6), 
                        (right_thruster_x + 4, hover_y + 12), 3)
        
        # Speed boost indicators - pulsing
        boost_intensity = int(150 + 100 * math.sin(self.animation_timer * 0.04))
        boost_color = (255, boost_intensity, 0)
        pygame.draw.circle(surface, boost_color, (center_x - 2, hover_y + 10), 2)
        pygame.draw.circle(surface, boost_color, (center_x + 2, hover_y + 10), 2)
        
        # Wing stabilizers
        pygame.draw.line(surface, light_metal, 
                        (center_x - 6, hover_y), (center_x - 10, hover_y + 2), 2)
        pygame.draw.line(surface, light_metal, 
                        (center_x + 6, hover_y), (center_x + 10, hover_y + 2), 2)
    
    def draw_tank_enemy(self, surface, center_x, center_y, color):
        """Enhanced heavy assault cyborg with mechanical animations"""
        # Animation offsets - heavy, slow movement
        hover_y = center_y + int(self.hover_offset * 0.5)  # Less hovering for heavy unit
        mechanical_sway = math.sin(self.animation_timer * 0.008) * 1
        
        # Color variations
        heavy_armor = (60, 70, 80)
        dark_armor = (30, 40, 50)
        weapon_metal = (100, 110, 120)
        danger_red = (255, 80, 80)
        energy_green = (100, 255, 150)
        
        # Main chassis - more angular and imposing
        main_body = pygame.Rect(center_x - 12 + mechanical_sway, hover_y - 10, 24, 20)
        pygame.draw.rect(surface, heavy_armor, main_body)
        pygame.draw.rect(surface, color, main_body, 3)
        
        # Reinforced armor plating with more detail
        armor_rects = [
            pygame.Rect(center_x - 10 + mechanical_sway, hover_y - 8, 8, 6),
            pygame.Rect(center_x + 2 + mechanical_sway, hover_y - 8, 8, 6),
            pygame.Rect(center_x - 10 + mechanical_sway, hover_y + 2, 8, 6),
            pygame.Rect(center_x + 2 + mechanical_sway, hover_y + 2, 8, 6)
        ]
        for i, armor in enumerate(armor_rects):
            pygame.draw.rect(surface, dark_armor, armor)
            pygame.draw.rect(surface, color, armor, 2)
            # Armor rivets
            rivet_x = armor.centerx + (1 if i % 2 else -1)
            rivet_y = armor.centery
            pygame.draw.circle(surface, weapon_metal, (rivet_x, rivet_y), 1)
        
        # Command turret - rotating slightly
        turret_angle = math.sin(self.animation_timer * 0.004) * 0.1
        turret_offset_x = math.sin(turret_angle) * 2
        
        head_rect = pygame.Rect(center_x - 6 + turret_offset_x, hover_y - 15, 12, 8)
        pygame.draw.rect(surface, heavy_armor, head_rect)
        pygame.draw.rect(surface, color, head_rect, 2)
        
        # Enhanced sensor array
        sensor_pulse = math.sin(self.animation_timer * 0.01)
        sensor_intensity = int(150 + 100 * sensor_pulse)
        sensor_color = (sensor_intensity, sensor_intensity, 255)
        
        pygame.draw.circle(surface, sensor_color, (center_x - 3 + turret_offset_x, hover_y - 11), 3)
        pygame.draw.circle(surface, sensor_color, (center_x + 3 + turret_offset_x, hover_y - 11), 3)
        pygame.draw.circle(surface, self.WHITE, (center_x - 3 + turret_offset_x, hover_y - 11), 1)
        pygame.draw.circle(surface, self.WHITE, (center_x + 3 + turret_offset_x, hover_y - 11), 1)
        
        # Heavy weapon systems - with recoil animation
        weapon_recoil = math.sin(self.animation_timer * 0.02) * 1
        
        # Left cannon
        left_weapon = pygame.Rect(center_x - 15 - weapon_recoil, hover_y - 2, 6, 3)
        pygame.draw.rect(surface, weapon_metal, left_weapon)
        pygame.draw.rect(surface, danger_red, 
                        pygame.Rect(center_x - 16 - weapon_recoil, hover_y - 1, 2, 1))
        
        # Right cannon
        right_weapon = pygame.Rect(center_x + 9 + weapon_recoil, hover_y - 2, 6, 3)
        pygame.draw.rect(surface, weapon_metal, right_weapon)
        pygame.draw.rect(surface, danger_red, 
                        pygame.Rect(center_x + 14 + weapon_recoil, hover_y - 1, 2, 1))
        
        # Missile pods on shoulders
        pygame.draw.rect(surface, dark_armor, 
                        pygame.Rect(center_x - 8, hover_y - 12, 3, 4))
        pygame.draw.rect(surface, dark_armor, 
                        pygame.Rect(center_x + 5, hover_y - 12, 3, 4))
        
        # Enhanced treads/mobility system
        tread_animation = int(self.animation_timer * 0.01) % 8
        for i in range(-10, 11, 3):
            tread_y = hover_y + 12 + (1 if (i + tread_animation) % 6 < 3 else 0)
            pygame.draw.circle(surface, weapon_metal, (center_x + i, tread_y), 2)
            pygame.draw.circle(surface, color, (center_x + i, tread_y), 2, 1)
        
        # Power core indicators
        core_glow = int(100 + 50 * math.sin(self.animation_timer * 0.008))
        core_color = (core_glow, 255, core_glow)
        pygame.draw.circle(surface, core_color, (center_x, hover_y), 2)
        
        # Exhaust vents
        exhaust_intensity = int(100 + 50 * math.sin(self.animation_timer * 0.015))
        exhaust_color = (255, exhaust_intensity, 0)
        pygame.draw.circle(surface, exhaust_color, (center_x - 12, hover_y + 8), 1)
        pygame.draw.circle(surface, exhaust_color, (center_x + 12, hover_y + 8), 1)
    
    def draw_sniper_enemy(self, surface, center_x, center_y, color):
        """Enhanced sniper cyborg with precision targeting systems"""
        # Animation offsets
        hover_y = center_y + int(self.hover_offset * 0.8)
        targeting_sweep = math.sin(self.animation_timer * 0.006) * 3
        
        # Color variations
        sniper_armor = (50, 40, 35)
        scope_metal = (120, 100, 80)
        targeting_laser = (255, 50, 50)
        precision_orange = (255, 165, 0)
        energy_cells = (255, 200, 100)
        
        # Main body - angular sniper design
        body_points = [
            (center_x, hover_y - 10),
            (center_x + 8, hover_y + 2),
            (center_x + 4, hover_y + 10),
            (center_x - 4, hover_y + 10),
            (center_x - 8, hover_y + 2)
        ]
        pygame.draw.polygon(surface, sniper_armor, body_points)
        pygame.draw.polygon(surface, color, body_points, 2)
        
        # Sniper rifle barrel - long and precise
        barrel_length = 15 + int(targeting_sweep)
        barrel_rect = pygame.Rect(center_x - barrel_length, hover_y - 1, barrel_length, 2)
        pygame.draw.rect(surface, scope_metal, barrel_rect)
        
        # Muzzle flash/targeting laser
        laser_intensity = int(150 + 100 * math.sin(self.animation_timer * 0.02))
        laser_color = (255, laser_intensity//2, 0)
        pygame.draw.circle(surface, laser_color, (center_x - barrel_length - 2, hover_y), 2)
        pygame.draw.circle(surface, targeting_laser, (center_x - barrel_length - 2, hover_y), 1)
        
        # Advanced targeting scope
        scope_rect = pygame.Rect(center_x - 6, hover_y - 8, 12, 6)
        pygame.draw.rect(surface, sniper_armor, scope_rect)
        pygame.draw.rect(surface, color, scope_rect, 2)
        
        # Scope lens with targeting reticle
        lens_center_x = center_x + int(targeting_sweep * 0.5)
        pygame.draw.circle(surface, (20, 40, 60), (lens_center_x, hover_y - 5), 4)
        pygame.draw.circle(surface, targeting_laser, (lens_center_x, hover_y - 5), 3, 1)
        
        # Targeting reticle
        reticle_size = 2
        pygame.draw.line(surface, targeting_laser, 
                        (lens_center_x - reticle_size, hover_y - 5), 
                        (lens_center_x + reticle_size, hover_y - 5), 1)
        pygame.draw.line(surface, targeting_laser, 
                        (lens_center_x, hover_y - 5 - reticle_size), 
                        (lens_center_x, hover_y - 5 + reticle_size), 1)
        
        # Stabilizer legs - mechanical precision
        leg_extend = math.sin(self.animation_timer * 0.004) * 1
        
        # Left stabilizer
        pygame.draw.line(surface, scope_metal, 
                        (center_x - 6, hover_y + 8), 
                        (center_x - 10, hover_y + 15 + leg_extend), 3)
        pygame.draw.circle(surface, energy_cells, (center_x - 10, hover_y + 15 + leg_extend), 2)
        
        # Right stabilizer  
        pygame.draw.line(surface, scope_metal, 
                        (center_x + 6, hover_y + 8), 
                        (center_x + 10, hover_y + 15 + leg_extend), 3)
        pygame.draw.circle(surface, energy_cells, (center_x + 10, hover_y + 15 + leg_extend), 2)
        
        # Energy cells and cooling vents
        cell_pulse = math.sin(self.animation_timer * 0.01)
        cell_intensity = int(150 + 100 * cell_pulse)
        cell_color = (255, cell_intensity, 0)
        
        pygame.draw.rect(surface, cell_color, 
                        pygame.Rect(center_x + 2, hover_y + 2, 2, 4))
        pygame.draw.rect(surface, cell_color, 
                        pygame.Rect(center_x + 5, hover_y + 2, 2, 4))
        
        # Precision targeting indicators
        if hasattr(self, 'last_attack') and (self.animation_timer - self.last_attack) < 500:
            # Show charging indicator when about to attack
            charge_bar_width = 8
            charge_progress = ((self.animation_timer - self.last_attack) / 500) * charge_bar_width
            pygame.draw.rect(surface, (100, 100, 100), 
                           pygame.Rect(center_x - 4, hover_y - 12, charge_bar_width, 2))
            pygame.draw.rect(surface, targeting_laser, 
                           pygame.Rect(center_x - 4, hover_y - 12, int(charge_progress), 2))
    
    def draw_swarm_enemy(self, surface, center_x, center_y, color):
        """Enhanced swarm scout with rapid movement systems"""
        # Animation offsets - very erratic and fast
        hover_y = center_y + int(self.hover_offset * 2)
        swarm_jitter = math.sin(self.animation_timer * 0.05) * 1.5
        rapid_pulse = math.sin(self.animation_timer * 0.03) * 0.3 + 0.7
        
        # Color variations
        scout_metal = (40, 50, 45)
        agile_green = (100, 255, 150)
        swarm_yellow = (255, 255, 100)
        micro_thrusters = (150, 255, 200)
        
        # Main body - compact and agile design
        body_scale = rapid_pulse
        body_size = int(6 * body_scale)
        body_rect = pygame.Rect(center_x - body_size + swarm_jitter, hover_y - body_size, 
                               body_size * 2, body_size * 2)
        pygame.draw.rect(surface, scout_metal, body_rect)
        pygame.draw.rect(surface, color, body_rect, 2)
        
        # Micro-wings for agility
        wing_flap = math.sin(self.animation_timer * 0.08) * 3
        
        # Left wing
        left_wing_points = [
            (center_x - 8 + swarm_jitter, hover_y),
            (center_x - 12 + wing_flap + swarm_jitter, hover_y - 3),
            (center_x - 10 + wing_flap + swarm_jitter, hover_y + 3)
        ]
        pygame.draw.polygon(surface, scout_metal, left_wing_points)
        pygame.draw.polygon(surface, agile_green, left_wing_points, 1)
        
        # Right wing
        right_wing_points = [
            (center_x + 8 + swarm_jitter, hover_y),
            (center_x + 12 - wing_flap + swarm_jitter, hover_y - 3),
            (center_x + 10 - wing_flap + swarm_jitter, hover_y + 3)
        ]
        pygame.draw.polygon(surface, scout_metal, right_wing_points)
        pygame.draw.polygon(surface, agile_green, right_wing_points, 1)
        
        # Central scanner eye - very active
        eye_size = int(3 * rapid_pulse)
        scanner_rotation = self.animation_timer * 0.02
        eye_x = center_x + math.cos(scanner_rotation) * 1 + swarm_jitter
        eye_y = hover_y + math.sin(scanner_rotation) * 1
        
        pygame.draw.circle(surface, swarm_yellow, (int(eye_x), int(eye_y)), eye_size)
        pygame.draw.circle(surface, self.WHITE, (int(eye_x), int(eye_y)), 1)
        
        # Micro-thrusters - very active
        thruster_intensity = int(200 + 55 * math.sin(self.animation_timer * 0.06))
        thruster_color = (micro_thrusters[0], thruster_intensity, micro_thrusters[2])
        
        # Multiple small thrusters for maneuverability
        thrusters = [
            (center_x - 8 + swarm_jitter, hover_y - 1),
            (center_x + 6 + swarm_jitter, hover_y - 1),
            (center_x + swarm_jitter, hover_y + 6),
            (center_x + swarm_jitter, hover_y - 6)
        ]
        
        for thruster_pos in thrusters:
            thruster_size = 1 + int(rapid_pulse)
            pygame.draw.circle(surface, thruster_color, thruster_pos, thruster_size)
        
        # Swarm communication antenna
        antenna_sway = math.sin(self.animation_timer * 0.04) * 2
        antenna_tip_x = center_x + antenna_sway + swarm_jitter
        antenna_tip_y = hover_y - 8
        
        pygame.draw.line(surface, agile_green, 
                        (center_x + swarm_jitter, hover_y - 4), 
                        (antenna_tip_x, antenna_tip_y), 1)
        pygame.draw.circle(surface, swarm_yellow, (antenna_tip_x, antenna_tip_y), 1)
        
        # Energy trails for speed indication
        for i, trail_pos in enumerate(self.movement_trail[-3:]):  # Only last 3 positions
            if i < len(self.movement_trail) - 1:
                alpha = (i + 1) * 80
                trail_surf = pygame.Surface((2, 2))
                trail_surf.set_alpha(alpha)
                pygame.draw.circle(trail_surf, agile_green, (1, 1), 1)
                surface.blit(trail_surf, (trail_pos[0] - 1, trail_pos[1] - 1))
    
    def draw_heavy_enemy(self, surface, center_x, center_y, color):
        """Enhanced heavy assault cyborg - larger than tank with more firepower"""
        # Animation offsets - slow but powerful
        hover_y = center_y + int(self.hover_offset * 0.3)  # Minimal hovering for ultra-heavy unit
        heavy_sway = math.sin(self.animation_timer * 0.005) * 1.5
        power_surge = math.sin(self.animation_timer * 0.008) * 0.5 + 0.5
        
        # Color variations
        ultra_armor = (70, 80, 90)
        reinforced_steel = (40, 50, 60)
        heavy_weapons = (120, 130, 140)
        plasma_core = (100, 150, 255)
        warning_lights = (255, 100, 100)
        
        # Main chassis - massive and imposing
        chassis_width = int(28 * (1 + power_surge * 0.1))
        chassis_height = 24
        main_body = pygame.Rect(center_x - chassis_width//2 + heavy_sway, hover_y - 12, 
                               chassis_width, chassis_height)
        pygame.draw.rect(surface, ultra_armor, main_body)
        pygame.draw.rect(surface, color, main_body, 4)
        
        # Layered armor plating with energy conduits
        armor_rects = [
            pygame.Rect(center_x - 12 + heavy_sway, hover_y - 10, 10, 8),
            pygame.Rect(center_x + 2 + heavy_sway, hover_y - 10, 10, 8),
            pygame.Rect(center_x - 12 + heavy_sway, hover_y + 2, 10, 8),
            pygame.Rect(center_x + 2 + heavy_sway, hover_y + 2, 10, 8)
        ]
        for i, armor in enumerate(armor_rects):
            pygame.draw.rect(surface, reinforced_steel, armor)
            pygame.draw.rect(surface, color, armor, 3)
            
            # Energy conduits in armor
            conduit_pulse = math.sin(self.animation_timer * 0.01 + i) * 0.5 + 0.5
            conduit_color = (int(100 * conduit_pulse), int(150 * conduit_pulse), 255)
            pygame.draw.line(surface, conduit_color,
                           (armor.left + 2, armor.centery),
                           (armor.right - 2, armor.centery), 2)
            
            # Armor bolts/rivets
            for bolt_x in range(armor.left + 3, armor.right - 2, 4):
                pygame.draw.circle(surface, heavy_weapons, (bolt_x, armor.centery), 1)
        
        # Command center - heavily armored
        head_sway_offset = heavy_sway * 0.5
        head_rect = pygame.Rect(center_x - 8 + head_sway_offset, hover_y - 20, 16, 10)
        pygame.draw.rect(surface, ultra_armor, head_rect)
        pygame.draw.rect(surface, color, head_rect, 3)
        
        # Advanced sensor array
        sensor_sweep = math.sin(self.animation_timer * 0.008) * 2
        sensor_left_x = center_x - 4 + head_sway_offset + sensor_sweep
        sensor_right_x = center_x + 4 + head_sway_offset - sensor_sweep
        
        # Left sensor
        pygame.draw.circle(surface, plasma_core, (sensor_left_x, hover_y - 15), 3)
        pygame.draw.circle(surface, self.WHITE, (sensor_left_x, hover_y - 15), 1)
        
        # Right sensor  
        pygame.draw.circle(surface, plasma_core, (sensor_right_x, hover_y - 15), 3)
        pygame.draw.circle(surface, self.WHITE, (sensor_right_x, hover_y - 15), 1)
        
        # Heavy weapon systems - dual cannons
        weapon_recoil = math.sin(self.animation_timer * 0.015) * 2
        
        # Left heavy cannon
        left_cannon = pygame.Rect(center_x - 20 - weapon_recoil, hover_y - 3, 8, 4)
        pygame.draw.rect(surface, heavy_weapons, left_cannon)
        pygame.draw.rect(surface, warning_lights, 
                        pygame.Rect(center_x - 22 - weapon_recoil, hover_y - 2, 3, 2))
        
        # Right heavy cannon
        right_cannon = pygame.Rect(center_x + 12 + weapon_recoil, hover_y - 3, 8, 4)
        pygame.draw.rect(surface, heavy_weapons, right_cannon)
        pygame.draw.rect(surface, warning_lights, 
                        pygame.Rect(center_x + 19 + weapon_recoil, hover_y - 2, 3, 2))
        
        # Shoulder-mounted missile launchers
        pygame.draw.rect(surface, reinforced_steel, 
                        pygame.Rect(center_x - 10 + heavy_sway, hover_y - 18, 4, 6))
        pygame.draw.rect(surface, reinforced_steel, 
                        pygame.Rect(center_x + 6 + heavy_sway, hover_y - 18, 4, 6))
        
        # Missile indicators
        missile_ready = (self.animation_timer % 2000) < 1000  # Blink every 2 seconds
        if missile_ready:
            pygame.draw.circle(surface, warning_lights, 
                             (center_x - 8 + heavy_sway, hover_y - 15), 1)
            pygame.draw.circle(surface, warning_lights, 
                             (center_x + 8 + heavy_sway, hover_y - 15), 1)
        
        # Enhanced mobility system - heavy treads
        tread_animation = int(self.animation_timer * 0.008) % 12
        for i in range(-12, 13, 3):
            tread_y = hover_y + 15 + (1 if (i + tread_animation) % 6 < 3 else 0)
            pygame.draw.circle(surface, heavy_weapons, (center_x + i + heavy_sway, tread_y), 3)
            pygame.draw.circle(surface, color, (center_x + i + heavy_sway, tread_y), 3, 1)
            
            # Tread spikes for traction
            pygame.draw.circle(surface, reinforced_steel, 
                             (center_x + i + heavy_sway, tread_y), 1)
        
        # Central power core - massive
        core_pulse = math.sin(self.animation_timer * 0.006)
        core_size = int(4 + core_pulse * 2)
        core_intensity = max(0, min(255, int(150 + 100 * core_pulse)))
        core_color = (core_intensity, 200, 255)
        
        pygame.draw.circle(surface, core_color, (center_x + heavy_sway, hover_y), core_size)
        pygame.draw.circle(surface, self.WHITE, (center_x + heavy_sway, hover_y), 2)
        
        # Heat exhaust vents
        exhaust_intensity = max(0, min(255, int(150 + 100 * math.sin(self.animation_timer * 0.01))))
        exhaust_color = (255, exhaust_intensity, 0)
        
        # Multiple exhaust ports
        exhaust_ports = [
            (center_x - 14 + heavy_sway, hover_y + 10),
            (center_x + 14 + heavy_sway, hover_y + 10),
            (center_x + heavy_sway, hover_y + 12)
        ]
        
        for port in exhaust_ports:
            pygame.draw.circle(surface, exhaust_color, port, 2)
            pygame.draw.circle(surface, (255, 200, 100), port, 1)
    
    def draw_elite_enemy(self, surface, center_x, center_y, color):
        """Enhanced elite cyborg commander with advanced systems"""
        # Animation offsets
        hover_y = center_y + int(self.hover_offset * 1.2)
        command_sway = math.sin(self.animation_timer * 0.004) * 2
        elite_pulse = math.sin(self.animation_timer * 0.007) * 0.3 + 0.7
        
        # Color variations
        command_armor = (60, 50, 80)
        elite_gold = (200, 150, 50)
        command_blue = (50, 100, 200)
        tactical_green = (100, 200, 100)
        elite_energy = (255, 200, 100)
        
        # Main torso - command structure
        torso_width = int(32 * elite_pulse)
        torso_height = 28
        torso_rect = pygame.Rect(center_x - torso_width//2 + command_sway, hover_y - 14, 
                                torso_width, torso_height)
        pygame.draw.rect(surface, command_armor, torso_rect)
        pygame.draw.rect(surface, color, torso_rect, 4)
        
        # Command insignia on chest
        insignia_rect = pygame.Rect(center_x - 6 + command_sway, hover_y - 8, 12, 8)
        pygame.draw.rect(surface, elite_gold, insignia_rect)
        pygame.draw.rect(surface, color, insignia_rect, 2)
        
        # Elite rank indicators
        for i in range(3):
            rank_y = hover_y - 6 + i * 3
            pygame.draw.rect(surface, elite_gold, 
                           pygame.Rect(center_x - 2 + command_sway, rank_y, 4, 1))
        
        # Advanced command head
        head_width = 20
        head_height = 12
        head_rect = pygame.Rect(center_x - head_width//2 + command_sway, hover_y - 26, 
                               head_width, head_height)
        pygame.draw.rect(surface, command_armor, head_rect)
        pygame.draw.rect(surface, color, head_rect, 3)
        
        # Command visor - advanced HUD
        visor_rect = pygame.Rect(center_x - 8 + command_sway, hover_y - 23, 16, 6)
        pygame.draw.rect(surface, command_blue, visor_rect)
        pygame.draw.rect(surface, elite_energy, visor_rect, 2)
        
        # HUD elements in visor
        hud_pulse = math.sin(self.animation_timer * 0.01)
        hud_intensity = max(0, min(255, int(150 + 100 * hud_pulse)))
        hud_color = (hud_intensity, 200, 255)
        
        # HUD lines
        for i in range(3):
            hud_y = hover_y - 22 + i * 2
            pygame.draw.line(surface, hud_color,
                           (center_x - 6 + command_sway, hud_y),
                           (center_x + 6 + command_sway, hud_y), 1)
        
        # Multiple tactical sensors
        sensor_positions = [-6, 0, 6]
        for i, x_offset in enumerate(sensor_positions):
            sensor_pulse = math.sin(self.animation_timer * (0.008 + i * 0.002)) * 0.5 + 0.5
            sensor_size = int(2 + sensor_pulse * 2)
            
            if i == 1:  # Main command sensor
                sensor_color = elite_energy
            else:  # Tactical sensors
                sensor_color = tactical_green
            
            pygame.draw.circle(surface, sensor_color, 
                             (center_x + x_offset + command_sway, hover_y - 20), sensor_size)
            pygame.draw.circle(surface, self.WHITE, 
                             (center_x + x_offset + command_sway, hover_y - 20), 1)
        
        # Elite weapon systems - advanced arms
        weapon_sway = math.sin(self.animation_timer * 0.006) * 1.5
        
        # Left command arm
        left_arm = pygame.Rect(center_x - 28 + weapon_sway, hover_y - 10, 10, 18)
        pygame.draw.rect(surface, command_armor, left_arm)
        pygame.draw.rect(surface, color, left_arm, 3)
        
        # Left weapon system
        left_weapon = pygame.Rect(center_x - 35 + weapon_sway, hover_y - 3, 8, 3)
        pygame.draw.rect(surface, elite_gold, left_weapon)
        pygame.draw.rect(surface, elite_energy, 
                        pygame.Rect(center_x - 36 + weapon_sway, hover_y - 2, 3, 1))
        
        # Right command arm
        right_arm = pygame.Rect(center_x + 18 - weapon_sway, hover_y - 10, 10, 18)
        pygame.draw.rect(surface, command_armor, right_arm)
        pygame.draw.rect(surface, color, right_arm, 3)
        
        # Right weapon system
        right_weapon = pygame.Rect(center_x + 27 - weapon_sway, hover_y - 3, 8, 3)
        pygame.draw.rect(surface, elite_gold, right_weapon)
        pygame.draw.rect(surface, elite_energy, 
                        pygame.Rect(center_x + 33 - weapon_sway, hover_y - 2, 3, 1))
        
        # Elite power core - advanced energy system
        core_pulse = math.sin(self.animation_timer * 0.009)
        core_size = int(6 + core_pulse * 3)
        core_intensity = max(0, min(255, int(180 + 75 * core_pulse)))
        core_color = (core_intensity, 150, 255)
        
        pygame.draw.circle(surface, core_color, (center_x + command_sway, hover_y), core_size, 3)
        pygame.draw.circle(surface, elite_energy, (center_x + command_sway, hover_y), core_size - 2)
        pygame.draw.circle(surface, self.WHITE, (center_x + command_sway, hover_y), 2)
        
        # Energy distribution network
        for angle in range(0, 360, 60):
            network_angle = math.radians(angle + self.rotation_angle * 30)
            network_end_x = center_x + math.cos(network_angle) * 12 + command_sway
            network_end_y = hover_y + math.sin(network_angle) * 12
            pygame.draw.line(surface, elite_energy, 
                           (center_x + command_sway, hover_y), 
                           (network_end_x, network_end_y), 1)
        
        # Elite mobility system - advanced legs
        leg_hydraulics = math.sin(self.animation_timer * 0.005) * 2
        
        # Left leg system
        left_leg = pygame.Rect(center_x - 14 + command_sway, hover_y + 14 + leg_hydraulics, 10, 14)
        pygame.draw.rect(surface, command_armor, left_leg)
        pygame.draw.rect(surface, color, left_leg, 3)
        
        # Left leg hydraulics
        pygame.draw.line(surface, elite_gold,
                        (center_x - 9 + command_sway, hover_y + 12),
                        (center_x - 9 + command_sway, hover_y + 18 + leg_hydraulics), 2)
        
        # Right leg system
        right_leg = pygame.Rect(center_x + 4 + command_sway, hover_y + 14 + leg_hydraulics, 10, 14)
        pygame.draw.rect(surface, command_armor, right_leg)
        pygame.draw.rect(surface, color, right_leg, 3)
        
        # Right leg hydraulics
        pygame.draw.line(surface, elite_gold,
                        (center_x + 9 + command_sway, hover_y + 12),
                        (center_x + 9 + command_sway, hover_y + 18 + leg_hydraulics), 2)
        
        # Advanced communication arrays - command network
        antenna_rotation = self.rotation_angle * 2
        for i, side in enumerate([-1, 1]):
            antenna_base_x = center_x + side * 10 + command_sway
            antenna_base_y = hover_y - 26
            
            antenna_tip_x = antenna_base_x + math.cos(antenna_rotation + i * math.pi) * 6
            antenna_tip_y = antenna_base_y - 6 + math.sin(antenna_rotation + i * math.pi) * 2
            
            pygame.draw.line(surface, elite_gold, 
                           (antenna_base_x, antenna_base_y), 
                           (antenna_tip_x, antenna_tip_y), 3)
            pygame.draw.circle(surface, elite_energy, (antenna_tip_x, antenna_tip_y), 3)
            
            # Command signal indicators
            signal_pulse = math.sin(self.animation_timer * 0.015 + i)
            if signal_pulse > 0:
                signal_intensity = int(signal_pulse * 150)
                signal_color = (255, signal_intensity, signal_intensity)
                pygame.draw.circle(surface, signal_color, (antenna_tip_x, antenna_tip_y), 1)
    
    def draw_boss_enemy(self, surface, center_x, center_y, color):
        """Ultimate boss cyborg with advanced animations and effects"""
        # Advanced animation offsets
        hover_y = center_y + int(self.hover_offset * 1.5)
        boss_pulse = 1.0 + math.sin(self.pulse_timer * 0.008) * 0.15
        power_surge = math.sin(self.animation_timer * 0.006) * 0.5 + 0.5
        
        # Advanced color palette
        boss_armor = (80, 20, 80)  # Dark purple
        elite_metal = (150, 120, 180)
        danger_red = (255, 50, 50)
        boss_energy = (255, 100, 255)  # Magenta energy
        core_white = (255, 255, 255)
        warning_orange = (255, 150, 0)
        
        # Energy field around boss
        field_radius = int(30 * boss_pulse)
        field_alpha = int(30 * power_surge)
        
        for ring in range(3):
            ring_radius = field_radius + ring * 8
            # Create temporary surface for alpha blending
            field_surf = pygame.Surface((ring_radius * 2, ring_radius * 2))
            field_surf.set_alpha(field_alpha)
            pygame.draw.circle(field_surf, boss_energy, (ring_radius, ring_radius), ring_radius, 2)
            surface.blit(field_surf, (center_x - ring_radius, hover_y - ring_radius))
        
        # Main torso - imposing and animated
        torso_scale = boss_pulse
        torso_width = int(36 * torso_scale)
        torso_height = int(30 * torso_scale)
        torso_rect = pygame.Rect(center_x - torso_width//2, hover_y - 15, torso_width, torso_height)
        pygame.draw.rect(surface, boss_armor, torso_rect)
        pygame.draw.rect(surface, color, torso_rect, 4)
        
        # Armor plating with energy channels
        for i in range(3):
            plate_y = hover_y - 10 + i * 8
            plate_rect = pygame.Rect(center_x - 15, plate_y, 30, 4)
            pygame.draw.rect(surface, elite_metal, plate_rect)
            # Energy flowing through armor
            energy_flow = int(self.animation_timer * 0.02) % 30
            energy_x = center_x - 15 + energy_flow
            pygame.draw.circle(surface, boss_energy, (energy_x, plate_y + 2), 1)
        
        # Command head - rotating slightly
        head_sway = math.sin(self.animation_timer * 0.003) * 2
        head_rect = pygame.Rect(center_x - 12 + head_sway, hover_y - 25, 24, 15)
        pygame.draw.rect(surface, boss_armor, head_rect)
        pygame.draw.rect(surface, color, head_rect, 3)
        
        # Advanced visor with scanning beam
        visor_rect = pygame.Rect(center_x - 10 + head_sway, hover_y - 22, 20, 8)
        pygame.draw.rect(surface, danger_red, visor_rect)
        pygame.draw.rect(surface, core_white, visor_rect, 2)
        
        # Scanning beam effect
        beam_intensity = max(0, min(255, int(200 * power_surge)))
        beam_color = (255, beam_intensity, beam_intensity)
        pygame.draw.rect(surface, beam_color, 
                        pygame.Rect(center_x - 8 + head_sway, hover_y - 21, 16, 2))
        
        # Multiple sensor eyes - each with different animation
        eye_positions = [-6, 0, 6]
        for i, x_offset in enumerate(eye_positions):
            eye_pulse = math.sin(self.animation_timer * (0.01 + i * 0.002)) * 0.5 + 0.5
            eye_size = int(3 + eye_pulse * 2)
            eye_color = boss_energy if i == 1 else warning_orange
            
            pygame.draw.circle(surface, eye_color, 
                             (center_x + x_offset + head_sway, hover_y - 18), eye_size)
            pygame.draw.circle(surface, core_white, 
                             (center_x + x_offset + head_sway, hover_y - 18), 1)
        
        # Massive shoulder weapon systems - with recoil
        weapon_recoil = math.sin(self.animation_timer * 0.01) * 3
        
        # Left weapon arm
        left_arm = pygame.Rect(center_x - 28 - weapon_recoil, hover_y - 8, 10, 20)
        pygame.draw.rect(surface, boss_armor, left_arm)
        pygame.draw.rect(surface, color, left_arm, 3)
        
        # Right weapon arm
        right_arm = pygame.Rect(center_x + 18 + weapon_recoil, hover_y - 8, 10, 20)
        pygame.draw.rect(surface, boss_armor, right_arm)
        pygame.draw.rect(surface, color, right_arm, 3)
        
        # Massive weapon barrels with energy charging
        charge_pulse = math.sin(self.animation_timer * 0.015)
        charge_color = (255, max(0, min(255, int(100 + 155 * charge_pulse))), 0)
        
        # Left cannon
        left_barrel = pygame.Rect(center_x - 35 - weapon_recoil, hover_y - 3, 8, 4)
        pygame.draw.rect(surface, elite_metal, left_barrel)
        pygame.draw.rect(surface, charge_color, 
                        pygame.Rect(center_x - 36 - weapon_recoil, hover_y - 2, 3, 2))
        
        # Right cannon
        right_barrel = pygame.Rect(center_x + 27 + weapon_recoil, hover_y - 3, 8, 4)
        pygame.draw.rect(surface, elite_metal, right_barrel)
        pygame.draw.rect(surface, charge_color, 
                        pygame.Rect(center_x + 33 + weapon_recoil, hover_y - 2, 3, 2))
        
        # Central power core - massive and pulsing
        core_size = int(10 * boss_pulse)
        core_intensity = max(0, min(255, int(200 + 55 * power_surge)))
        core_color = (core_intensity, 100, 255)
        
        pygame.draw.circle(surface, core_color, (center_x, hover_y), core_size, 3)
        pygame.draw.circle(surface, core_white, (center_x, hover_y), core_size - 2)
        pygame.draw.circle(surface, boss_energy, (center_x, hover_y), core_size - 4)
        
        # Power conduits emanating from core
        for angle in range(0, 360, 45):
            conduit_angle = math.radians(angle + self.rotation_angle * 50)
            conduit_end_x = center_x + math.cos(conduit_angle) * 15
            conduit_end_y = hover_y + math.sin(conduit_angle) * 15
            pygame.draw.line(surface, boss_energy, 
                           (center_x, hover_y), (conduit_end_x, conduit_end_y), 2)
        
        # Reinforced leg systems with hydraulics
        leg_extend = math.sin(self.animation_timer * 0.006) * 2
        
        # Left leg
        left_leg = pygame.Rect(center_x - 12, hover_y + 15 + leg_extend, 10, 15)
        pygame.draw.rect(surface, boss_armor, left_leg)
        pygame.draw.rect(surface, color, left_leg, 3)
        
        # Right leg
        right_leg = pygame.Rect(center_x + 2, hover_y + 15 + leg_extend, 10, 15)
        pygame.draw.rect(surface, boss_armor, right_leg)
        pygame.draw.rect(surface, color, right_leg, 3)
        
        # Hydraulic pistons
        pygame.draw.line(surface, elite_metal, 
                        (center_x - 7, hover_y + 12), (center_x - 7, hover_y + 18 + leg_extend), 3)
        pygame.draw.line(surface, elite_metal, 
                        (center_x + 7, hover_y + 12), (center_x + 7, hover_y + 18 + leg_extend), 3)
        
        # Advanced communication arrays - rotating
        antenna_angle = self.rotation_angle * 3
        for i, side in enumerate([-1, 1]):
            antenna_base_x = center_x + side * 8 + head_sway
            antenna_base_y = hover_y - 25
            
            antenna_tip_x = antenna_base_x + math.cos(antenna_angle + i) * 8
            antenna_tip_y = antenna_base_y - 8 + math.sin(antenna_angle + i) * 3
            
            pygame.draw.line(surface, elite_metal, 
                           (antenna_base_x, antenna_base_y), 
                           (antenna_tip_x, antenna_tip_y), 3)
            pygame.draw.circle(surface, boss_energy, (antenna_tip_x, antenna_tip_y), 3)
        
        # Boss health indicator (special)
        if self.health < self.max_health * 0.5:  # When damaged, show more aggressive effects
            danger_pulse = math.sin(self.animation_timer * 0.02)
            danger_alpha = int(100 + 100 * danger_pulse)
            # Create temporary surface for alpha blending
            danger_surf = pygame.Surface(((field_radius + 10) * 2, (field_radius + 10) * 2))
            danger_surf.set_alpha(danger_alpha)
            pygame.draw.circle(danger_surf, danger_red, (field_radius + 10, field_radius + 10), field_radius + 10, 3)
            surface.blit(danger_surf, (center_x - field_radius - 10, hover_y - field_radius - 10))
    
    def draw_health_bar(self, surface):
        bar_width = self.rect.width
        bar_height = 4
        bar_x = self.rect.x
        bar_y = self.rect.y - 8
        
        # Background
        pygame.draw.rect(surface, self.WHITE, 
                        pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        
        if health_ratio > 0.6:
            health_color = self.MINT_GREEN
        elif health_ratio > 0.3:
            health_color = self.CYAN
        else:
            health_color = self.CORAL
            
        pygame.draw.rect(surface, health_color, 
                        pygame.Rect(bar_x, bar_y, health_width, bar_height))


class EnemySpawner:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_timer = 0
        self.base_spawn_delay = 1000  # Base spawn delay
        self.min_spawn_delay = 100   # Minimum spawn delay (faster for horde)
        self.current_spawn_delay = self.base_spawn_delay
        
        # Track boss wave logic
        self.boss_spawned_this_wave = False
        
        # Define enemy introduction waves
        self.enemy_unlock_waves = {
            "basic": 1,
            "fast": 2,
            "swarm": 3,
            "tank": 4,
            "sniper": 6,
            "heavy": 8,
            "elite": 10,
            "boss": 5  # Bosses appear every 5 waves
        }
    
    def should_spawn(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.current_spawn_delay:
            self.spawn_timer = 0
            return True
        return False
    
    def spawn_enemy(self, wave, player_pos):
        # Check if this is a boss wave (every 5 waves)
        is_boss_wave = (wave % 5 == 0) and wave >= 5
        
        # Choose spawn position (off-screen)
        spawn_x, spawn_y = self.get_spawn_position(player_pos)
        
        # Choose enemy type based on wave progression
        enemy_type = self.choose_enemy_type(wave, is_boss_wave)
        
        return Enemy(spawn_x, spawn_y, enemy_type, wave)
    
    def get_spawn_position(self, player_pos):
        player_x, player_y = player_pos
        
        # Choose a side to spawn from
        side = random.choice(["top", "bottom", "left", "right"])
        
        if side == "top":
            return random.randint(0, self.screen_width), -30
        elif side == "bottom":
            return random.randint(0, self.screen_width), self.screen_height + 30
        elif side == "left":
            return -30, random.randint(0, self.screen_height)
        else:  # right
            return self.screen_width + 30, random.randint(0, self.screen_height)
    
    def choose_enemy_type(self, wave, is_boss_wave=False):
        """Choose enemy type based on progressive horde system"""
        
        # Boss wave logic - spawn 1-2 bosses per boss wave
        if is_boss_wave and not self.boss_spawned_this_wave:
            self.boss_spawned_this_wave = True
            return "boss"
        
        # Get available enemy types for this wave
        available_types = []
        for enemy_type, unlock_wave in self.enemy_unlock_waves.items():
            if wave >= unlock_wave and enemy_type != "boss":
                available_types.append(enemy_type)
        
        # Progressive probability system based on wave
        if wave <= 2:
            # Early waves: mostly basic enemies
            weights = {
                "basic": 0.8,
                "fast": 0.2 if wave >= 2 else 0.0
            }
        elif wave <= 4:
            # Early-mid waves: introduce swarm and tank
            weights = {
                "basic": 0.5,
                "fast": 0.3,
                "swarm": 0.2 if wave >= 3 else 0.0,
                "tank": 0.1 if wave >= 4 else 0.0
            }
        elif wave <= 7:
            # Mid waves: more variety, introduce sniper
            weights = {
                "basic": 0.3,
                "fast": 0.25,
                "swarm": 0.25,
                "tank": 0.15,
                "sniper": 0.05 if wave >= 6 else 0.0
            }
        elif wave <= 12:
            # Late waves: introduce heavy enemies
            weights = {
                "basic": 0.2,
                "fast": 0.2,
                "swarm": 0.3,  # More swarm for horde feel
                "tank": 0.15,
                "sniper": 0.1,
                "heavy": 0.05 if wave >= 8 else 0.0
            }
        else:
            # End game waves: all enemy types, elite enemies
            weights = {
                "basic": 0.15,
                "fast": 0.15,
                "swarm": 0.3,
                "tank": 0.15,
                "sniper": 0.1,
                "heavy": 0.1,
                "elite": 0.05 if wave >= 10 else 0.0
            }
        
        # Filter weights to only include available types
        filtered_weights = {enemy_type: weight for enemy_type, weight in weights.items() 
                           if enemy_type in available_types}
        
        # Handle swarm special spawning (spawn multiple)
        if random.random() < 0.3 and "swarm" in filtered_weights and wave >= 3:
            return "swarm"
            
        # Weighted random selection
        if not filtered_weights:
            return "basic"
            
        rand = random.random()
        cumulative = 0
        total_weight = sum(filtered_weights.values())
        
        for enemy_type, weight in filtered_weights.items():
            cumulative += weight / total_weight
            if rand <= cumulative:
                return enemy_type
        
        return "basic"  # Fallback
    
    def get_spawn_count_for_type(self, enemy_type, wave):
        """Get how many enemies of this type to spawn at once"""
        if enemy_type == "swarm":
            # Spawn swarm enemies in groups
            return random.randint(3, min(8, 3 + wave // 2))
        elif enemy_type == "boss":
            # Bosses spawn alone, but more bosses in later waves
            return min(3, 1 + wave // 10)
        else:
            # Normal enemies usually spawn alone, sometimes in small groups
            if wave >= 8 and random.random() < 0.3:
                return random.randint(2, 3)
            return 1
    
    def reset_boss_flag(self):
        """Reset boss flag for new wave"""
        self.boss_spawned_this_wave = False
    
    def update_spawn_rate(self, wave):
        """Update spawn rate based on wave (horde-like faster spawning)"""
        # Spawn rate increases with wave number
        wave_multiplier = max(0.3, 1.0 - (wave - 1) * 0.05)
        self.current_spawn_delay = max(
            self.min_spawn_delay, 
            int(self.base_spawn_delay * wave_multiplier)
        )
    
    def increase_difficulty(self):
        """Legacy method - now handled by update_spawn_rate"""
        pass 