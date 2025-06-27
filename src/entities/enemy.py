import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic"):
        super().__init__()
        self.enemy_type = enemy_type
        
        # Basic properties
        if enemy_type == "basic":
            self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
            self.max_health = 30
            self.speed = 60  # Reduced from 80
            self.damage = 15
            self.score_value = 10
            self.color = (255, 100, 100)  # Red
        elif enemy_type == "fast":
            self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
            self.max_health = 15
            self.speed = 90  # Reduced from 150
            self.damage = 10
            self.score_value = 15
            self.color = (255, 255, 100)  # Yellow
        elif enemy_type == "tank":
            self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
            self.max_health = 80
            self.speed = 30  # Reduced from 40
            self.damage = 25
            self.score_value = 30
            self.color = (100, 255, 100)  # Green
        elif enemy_type == "boss":
            self.rect = pygame.Rect(x - 25, y - 25, 50, 50)
            self.max_health = 200
            self.speed = 45  # Reduced from 60
            self.damage = 40
            self.score_value = 100
            self.color = (255, 100, 255)  # Magenta
        
        self.health = self.max_health
        
        # Required for pygame sprite
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        
        # AI behavior
        self.ai_timer = 0
        self.ai_state = "chase"  # chase, circle, retreat
        self.circle_angle = random.uniform(0, 2 * math.pi)
        
        # Visual effects
        self.damage_flash = 0
        
        # Colors (New palette)
        self.CORAL = (255, 134, 178)          # For red enemies
        self.CYAN = (108, 222, 255)           # For yellow enemies  
        self.MINT_GREEN = (108, 255, 222)     # For green enemies
        self.MAGENTA = (222, 108, 255)        # For purple enemies
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
    
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
        self.spawn_delay = 1000  # Start with 1 second between spawns
        self.min_spawn_delay = 200  # Minimum spawn delay
        
        # Enemy type probabilities (will change with waves)
        self.enemy_probabilities = {
            "basic": 0.7,
            "fast": 0.2,
            "tank": 0.1,
            "boss": 0.0
        }
    
    def should_spawn(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            return True
        return False
    
    def spawn_enemy(self, wave, player_pos):
        # Choose spawn position (off-screen)
        spawn_x, spawn_y = self.get_spawn_position(player_pos)
        
        # Choose enemy type based on probabilities
        enemy_type = self.choose_enemy_type(wave)
        
        return Enemy(spawn_x, spawn_y, enemy_type)
    
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
    
    def choose_enemy_type(self, wave):
        # Adjust probabilities based on wave
        if wave >= 5:
            self.enemy_probabilities["boss"] = 0.05
            self.enemy_probabilities["tank"] = 0.2
            self.enemy_probabilities["fast"] = 0.35
            self.enemy_probabilities["basic"] = 0.4
        elif wave >= 3:
            self.enemy_probabilities["tank"] = 0.15
            self.enemy_probabilities["fast"] = 0.3
            self.enemy_probabilities["basic"] = 0.55
        
        # Weighted random selection
        rand = random.random()
        cumulative = 0
        
        for enemy_type, probability in self.enemy_probabilities.items():
            cumulative += probability
            if rand <= cumulative:
                return enemy_type
        
        return "basic"  # Fallback
    
    def increase_difficulty(self):
        # Decrease spawn delay (faster spawning)
        self.spawn_delay = max(self.min_spawn_delay, self.spawn_delay - 50) 