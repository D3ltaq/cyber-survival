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
            self.speed = 30
            self.damage = 25
            self.score_value = 30
            self.color = (100, 255, 100)  # Green
        elif enemy_type == "sniper":  # NEW: Long-range, slow but high damage
            self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
            self.base_health = 40
            self.speed = 25
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
            self.speed = 20
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
                ideal_distance = 250
                if distance > ideal_distance + 50:
                    # Too far, move closer slowly
                    self.velocity_x = dx * self.speed * 0.5
                    self.velocity_y = dy * self.speed * 0.5
                elif distance < ideal_distance - 50:
                    # Too close, retreat
                    self.velocity_x = -dx * self.speed
                    self.velocity_y = -dy * self.speed
                else:
                    # Perfect distance, strafe
                    perpendicular_x = -dy
                    perpendicular_y = dx
                    self.velocity_x = perpendicular_x * self.speed * 0.7
                    self.velocity_y = perpendicular_y * self.speed * 0.7
                    
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
                if distance > 100:
                    # Chase when far
                    self.velocity_x = dx * self.speed
                    self.velocity_y = dy * self.speed
                else:
                    # Circle when close
                    self.circle_angle += dt * 0.003
                    circle_dx = math.cos(self.circle_angle)
                    circle_dy = math.sin(self.circle_angle)
                    self.velocity_x = (dx * 0.3 + circle_dx * 0.7) * self.speed
                    self.velocity_y = (dy * 0.3 + circle_dy * 0.7) * self.speed
                    
            elif self.enemy_type == "boss":
                # Complex AI: circle around player at medium distance
                ideal_distance = 150
                
                if distance < ideal_distance - 20:
                    # Too close, move away
                    self.velocity_x = -dx * self.speed
                    self.velocity_y = -dy * self.speed
                elif distance > ideal_distance + 20:
                    # Too far, move closer
                    self.velocity_x = dx * self.speed
                    self.velocity_y = dy * self.speed
                else:
                    # Perfect distance, circle around
                    self.circle_angle += dt * 0.002
                    circle_dx = math.cos(self.circle_angle)
                    circle_dy = math.sin(self.circle_angle)
                    self.velocity_x = circle_dx * self.speed
                    self.velocity_y = circle_dy * self.speed
    
    def take_damage(self, damage):
        self.health -= damage
        self.damage_flash = 200  # Flash for 200ms
        
        # Clamp health
        self.health = max(0, self.health)
    
    def draw(self, surface):
        center_x, center_y = self.rect.center
        
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
    
    def draw_basic_enemy(self, surface, center_x, center_y, color):
        # Basic cyborg drone
        # Main body
        body_rect = pygame.Rect(center_x - 8, center_y - 8, 16, 16)
        pygame.draw.rect(surface, self.BLACK, body_rect)
        pygame.draw.rect(surface, color, body_rect, 2)
        
        # Central core/eye
        pygame.draw.circle(surface, color, (center_x, center_y), 4)
        pygame.draw.circle(surface, self.WHITE, (center_x, center_y), 2)
        
        # Antenna/sensors
        pygame.draw.line(surface, color, (center_x - 5, center_y - 8), (center_x - 5, center_y - 12), 2)
        pygame.draw.line(surface, color, (center_x + 5, center_y - 8), (center_x + 5, center_y - 12), 2)
        pygame.draw.circle(surface, color, (center_x - 5, center_y - 12), 2)
        pygame.draw.circle(surface, color, (center_x + 5, center_y - 12), 2)
        
        # Side thrusters
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 10, center_y - 2, 3, 4))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 7, center_y - 2, 3, 4))
    
    def draw_fast_enemy(self, surface, center_x, center_y, color):
        # Fast reconnaissance cyborg
        # Main body (sleek design)
        body_points = [
            (center_x, center_y - 8),
            (center_x + 6, center_y + 4),
            (center_x + 3, center_y + 8),
            (center_x - 3, center_y + 8),
            (center_x - 6, center_y + 4)
        ]
        pygame.draw.polygon(surface, self.BLACK, body_points)
        pygame.draw.polygon(surface, color, body_points, 2)
        
        # Head/scanner
        pygame.draw.circle(surface, self.BLACK, (center_x, center_y - 4), 4)
        pygame.draw.circle(surface, color, (center_x, center_y - 4), 4, 1)
        # Scanning eye
        pygame.draw.circle(surface, color, (center_x, center_y - 4), 2)
        pygame.draw.circle(surface, self.WHITE, (center_x, center_y - 4), 1)
        
        # Legs/thrusters
        pygame.draw.line(surface, color, (center_x - 4, center_y + 6), (center_x - 6, center_y + 12), 2)
        pygame.draw.line(surface, color, (center_x + 4, center_y + 6), (center_x + 6, center_y + 12), 2)
        
        # Speed boost indicators
        pygame.draw.circle(surface, color, (center_x - 2, center_y + 10), 1)
        pygame.draw.circle(surface, color, (center_x + 2, center_y + 10), 1)
    
    def draw_tank_enemy(self, surface, center_x, center_y, color):
        # Heavy assault cyborg
        # Main chassis
        main_body = pygame.Rect(center_x - 12, center_y - 10, 24, 20)
        pygame.draw.rect(surface, self.BLACK, main_body)
        pygame.draw.rect(surface, color, main_body, 3)
        
        # Armor plating
        armor_rects = [
            pygame.Rect(center_x - 10, center_y - 8, 8, 6),
            pygame.Rect(center_x + 2, center_y - 8, 8, 6),
            pygame.Rect(center_x - 10, center_y + 2, 8, 6),
            pygame.Rect(center_x + 2, center_y + 2, 8, 6)
        ]
        for armor in armor_rects:
            pygame.draw.rect(surface, color, armor, 1)
        
        # Head/turret
        head_rect = pygame.Rect(center_x - 6, center_y - 15, 12, 8)
        pygame.draw.rect(surface, self.BLACK, head_rect)
        pygame.draw.rect(surface, color, head_rect, 2)
        
        # Eyes/sensors
        pygame.draw.circle(surface, color, (center_x - 3, center_y - 11), 2)
        pygame.draw.circle(surface, color, (center_x + 3, center_y - 11), 2)
        pygame.draw.circle(surface, self.WHITE, (center_x - 3, center_y - 11), 1)
        pygame.draw.circle(surface, self.WHITE, (center_x + 3, center_y - 11), 1)
        
        # Weapon systems
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 15, center_y - 2, 4, 2))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 11, center_y - 2, 4, 2))
        
        # Treads/legs
        for i in range(-10, 11, 4):
            pygame.draw.circle(surface, color, (center_x + i, center_y + 12), 2, 1)
    
    def draw_sniper_enemy(self, surface, center_x, center_y, color):
        # Sniper cyborg
        # Main body (sleek design)
        body_points = [
            (center_x, center_y - 8),
            (center_x + 6, center_y + 4),
            (center_x + 3, center_y + 8),
            (center_x - 3, center_y + 8),
            (center_x - 6, center_y + 4)
        ]
        pygame.draw.polygon(surface, self.BLACK, body_points)
        pygame.draw.polygon(surface, color, body_points, 2)
        
        # Head/scanner
        pygame.draw.circle(surface, self.BLACK, (center_x, center_y - 4), 4)
        pygame.draw.circle(surface, color, (center_x, center_y - 4), 4, 1)
        # Scanning eye
        pygame.draw.circle(surface, color, (center_x, center_y - 4), 2)
        pygame.draw.circle(surface, self.WHITE, (center_x, center_y - 4), 1)
        
        # Legs/thrusters
        pygame.draw.line(surface, color, (center_x - 4, center_y + 6), (center_x - 6, center_y + 12), 2)
        pygame.draw.line(surface, color, (center_x + 4, center_y + 6), (center_x + 6, center_y + 12), 2)
        
        # Speed boost indicators
        pygame.draw.circle(surface, color, (center_x - 2, center_y + 10), 1)
        pygame.draw.circle(surface, color, (center_x + 2, center_y + 10), 1)
    
    def draw_swarm_enemy(self, surface, center_x, center_y, color):
        # Small, fast scout cyborg
        # Main body (smaller design)
        body_rect = pygame.Rect(center_x - 6, center_y - 6, 12, 12)
        pygame.draw.rect(surface, self.BLACK, body_rect)
        pygame.draw.rect(surface, color, body_rect, 1)
        
        # Central core/eye (smaller)
        pygame.draw.circle(surface, color, (center_x, center_y), 3)
        pygame.draw.circle(surface, self.WHITE, (center_x, center_y), 1)
        
        # Small thrusters
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 8, center_y - 1, 2, 2))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 6, center_y - 1, 2, 2))
    
    def draw_heavy_enemy(self, surface, center_x, center_y, color):
        # Heavy assault cyborg
        # Main chassis
        main_body = pygame.Rect(center_x - 12, center_y - 10, 24, 20)
        pygame.draw.rect(surface, self.BLACK, main_body)
        pygame.draw.rect(surface, color, main_body, 3)
        
        # Armor plating
        armor_rects = [
            pygame.Rect(center_x - 10, center_y - 8, 8, 6),
            pygame.Rect(center_x + 2, center_y - 8, 8, 6),
            pygame.Rect(center_x - 10, center_y + 2, 8, 6),
            pygame.Rect(center_x + 2, center_y + 2, 8, 6)
        ]
        for armor in armor_rects:
            pygame.draw.rect(surface, color, armor, 1)
        
        # Head/turret
        head_rect = pygame.Rect(center_x - 6, center_y - 15, 12, 8)
        pygame.draw.rect(surface, self.BLACK, head_rect)
        pygame.draw.rect(surface, color, head_rect, 2)
        
        # Eyes/sensors
        pygame.draw.circle(surface, color, (center_x - 3, center_y - 11), 2)
        pygame.draw.circle(surface, color, (center_x + 3, center_y - 11), 2)
        pygame.draw.circle(surface, self.WHITE, (center_x - 3, center_y - 11), 1)
        pygame.draw.circle(surface, self.WHITE, (center_x + 3, center_y - 11), 1)
        
        # Weapon systems
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 15, center_y - 2, 4, 2))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 11, center_y - 2, 4, 2))
        
        # Treads/legs
        for i in range(-10, 11, 4):
            pygame.draw.circle(surface, color, (center_x + i, center_y + 12), 2, 1)
    
    def draw_elite_enemy(self, surface, center_x, center_y, color):
        # Elite cyborg commander
        # Main torso
        torso_rect = pygame.Rect(center_x - 18, center_y - 15, 36, 30)
        pygame.draw.rect(surface, self.BLACK, torso_rect)
        pygame.draw.rect(surface, color, torso_rect, 3)
        
        # Head/command module
        head_rect = pygame.Rect(center_x - 12, center_y - 25, 24, 15)
        pygame.draw.rect(surface, self.BLACK, head_rect)
        pygame.draw.rect(surface, color, head_rect, 2)
        
        # Visor/face plate
        visor_rect = pygame.Rect(center_x - 10, center_y - 22, 20, 8)
        pygame.draw.rect(surface, color, visor_rect)
        pygame.draw.rect(surface, self.WHITE, visor_rect, 1)
        
        # Multiple eyes/sensors
        for i, x_offset in enumerate([-6, 0, 6]):
            eye_color = self.WHITE if i == 1 else color
            pygame.draw.circle(surface, eye_color, (center_x + x_offset, center_y - 18), 2)
            if i == 1:  # Main eye
                pygame.draw.circle(surface, color, (center_x + x_offset, center_y - 18), 1)
        
        # Shoulder weapons/arms
        # Left arm
        left_arm = pygame.Rect(center_x - 25, center_y - 8, 8, 16)
        pygame.draw.rect(surface, self.BLACK, left_arm)
        pygame.draw.rect(surface, color, left_arm, 2)
        # Right arm
        right_arm = pygame.Rect(center_x + 17, center_y - 8, 8, 16)
        pygame.draw.rect(surface, self.BLACK, right_arm)
        pygame.draw.rect(surface, color, right_arm, 2)
        
        # Weapon barrels
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 30, center_y - 2, 6, 2))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 24, center_y - 2, 6, 2))
        
        # Central power core
        pygame.draw.circle(surface, color, (center_x, center_y), 8, 2)
        pygame.draw.circle(surface, self.WHITE, (center_x, center_y), 4)
        pygame.draw.circle(surface, color, (center_x, center_y), 2)
        
        # Leg systems
        # Left leg
        pygame.draw.rect(surface, self.BLACK, pygame.Rect(center_x - 12, center_y + 15, 8, 12))
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 12, center_y + 15, 8, 12), 2)
        # Right leg
        pygame.draw.rect(surface, self.BLACK, pygame.Rect(center_x + 4, center_y + 15, 8, 12))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 4, center_y + 15, 8, 12), 2)
        
        # Antenna/communication arrays
        pygame.draw.line(surface, color, (center_x - 8, center_y - 25), (center_x - 8, center_y - 30), 2)
        pygame.draw.line(surface, color, (center_x + 8, center_y - 25), (center_x + 8, center_y - 30), 2)
        pygame.draw.circle(surface, color, (center_x - 8, center_y - 30), 2)
        pygame.draw.circle(surface, color, (center_x + 8, center_y - 30), 2)
    
    def draw_boss_enemy(self, surface, center_x, center_y, color):
        # Elite cyborg commander
        # Main torso
        torso_rect = pygame.Rect(center_x - 18, center_y - 15, 36, 30)
        pygame.draw.rect(surface, self.BLACK, torso_rect)
        pygame.draw.rect(surface, color, torso_rect, 3)
        
        # Head/command module
        head_rect = pygame.Rect(center_x - 12, center_y - 25, 24, 15)
        pygame.draw.rect(surface, self.BLACK, head_rect)
        pygame.draw.rect(surface, color, head_rect, 2)
        
        # Visor/face plate
        visor_rect = pygame.Rect(center_x - 10, center_y - 22, 20, 8)
        pygame.draw.rect(surface, color, visor_rect)
        pygame.draw.rect(surface, self.WHITE, visor_rect, 1)
        
        # Multiple eyes/sensors
        for i, x_offset in enumerate([-6, 0, 6]):
            eye_color = self.WHITE if i == 1 else color
            pygame.draw.circle(surface, eye_color, (center_x + x_offset, center_y - 18), 2)
            if i == 1:  # Main eye
                pygame.draw.circle(surface, color, (center_x + x_offset, center_y - 18), 1)
        
        # Shoulder weapons/arms
        # Left arm
        left_arm = pygame.Rect(center_x - 25, center_y - 8, 8, 16)
        pygame.draw.rect(surface, self.BLACK, left_arm)
        pygame.draw.rect(surface, color, left_arm, 2)
        # Right arm
        right_arm = pygame.Rect(center_x + 17, center_y - 8, 8, 16)
        pygame.draw.rect(surface, self.BLACK, right_arm)
        pygame.draw.rect(surface, color, right_arm, 2)
        
        # Weapon barrels
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 30, center_y - 2, 6, 2))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 24, center_y - 2, 6, 2))
        
        # Central power core
        pygame.draw.circle(surface, color, (center_x, center_y), 8, 2)
        pygame.draw.circle(surface, self.WHITE, (center_x, center_y), 4)
        pygame.draw.circle(surface, color, (center_x, center_y), 2)
        
        # Leg systems
        # Left leg
        pygame.draw.rect(surface, self.BLACK, pygame.Rect(center_x - 12, center_y + 15, 8, 12))
        pygame.draw.rect(surface, color, pygame.Rect(center_x - 12, center_y + 15, 8, 12), 2)
        # Right leg
        pygame.draw.rect(surface, self.BLACK, pygame.Rect(center_x + 4, center_y + 15, 8, 12))
        pygame.draw.rect(surface, color, pygame.Rect(center_x + 4, center_y + 15, 8, 12), 2)
        
        # Antenna/communication arrays
        pygame.draw.line(surface, color, (center_x - 8, center_y - 25), (center_x - 8, center_y - 30), 2)
        pygame.draw.line(surface, color, (center_x + 8, center_y - 25), (center_x + 8, center_y - 30), 2)
        pygame.draw.circle(surface, color, (center_x - 8, center_y - 30), 2)
        pygame.draw.circle(surface, color, (center_x + 8, center_y - 30), 2)
    
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