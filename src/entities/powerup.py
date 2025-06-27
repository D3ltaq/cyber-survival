import pygame
import random
import math

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.powerup_types = ["health", "damage", "speed"]
        self.powerup_type = random.choice(self.powerup_types)
        
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.image = pygame.Surface((30, 30))  # Required for pygame sprite
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        self.original_x = x
        self.original_y = y
        
        # Animation
        self.float_offset = 0
        self.rotation = 0
        self.pulse = 0
        
        # Lifetime
        self.lifetime = 15000  # 15 seconds
        self.timer = 0
        
        # Colors based on type
        if self.powerup_type == "health":
            self.color = (57, 255, 20)  # Neon green
            self.glow_color = (30, 150, 10)
        elif self.powerup_type == "damage":
            self.color = (255, 20, 147)  # Neon pink
            self.glow_color = (150, 10, 80)
        elif self.powerup_type == "speed":
            self.color = (255, 255, 20)  # Neon yellow
            self.glow_color = (150, 150, 10)
        
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
    
    def update(self, dt):
        self.timer += dt
        
        # Float animation
        self.float_offset = math.sin(self.timer * 0.003) * 5
        
        # Rotation animation
        self.rotation += dt * 0.1
        
        # Pulse animation
        self.pulse = math.sin(self.timer * 0.005) * 0.3 + 0.7
        
        # Update position
        self.rect.centery = self.original_y + self.float_offset
        
        # Check if expired
        return self.timer < self.lifetime
    
    def apply_effect(self, player):
        if self.powerup_type == "health":
            player.heal(50)
        elif self.powerup_type == "damage":
            player.apply_powerup("damage", 10000)  # 10 seconds
        elif self.powerup_type == "speed":
            player.apply_powerup("speed", 8000)  # 8 seconds
    
    def draw(self, surface):
        center_x, center_y = self.rect.center
        
        # Draw glow effect
        glow_radius = int(20 * self.pulse)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2))
        glow_surface.set_alpha(50)
        pygame.draw.circle(glow_surface, self.glow_color, 
                          (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, 
                    (center_x - glow_radius, center_y - glow_radius))
        
        # Draw main powerup based on type
        if self.powerup_type == "health":
            self.draw_health_powerup(surface, center_x, center_y)
        elif self.powerup_type == "damage":
            self.draw_damage_powerup(surface, center_x, center_y)
        elif self.powerup_type == "speed":
            self.draw_speed_powerup(surface, center_x, center_y)
    
    def draw_health_powerup(self, surface, center_x, center_y):
        # Cross shape for health
        size = int(12 * self.pulse)
        thickness = max(2, int(3 * self.pulse))
        
        # Horizontal bar
        pygame.draw.rect(surface, self.color,
                        pygame.Rect(center_x - size, center_y - thickness//2, 
                                   size * 2, thickness))
        # Vertical bar
        pygame.draw.rect(surface, self.color,
                        pygame.Rect(center_x - thickness//2, center_y - size, 
                                   thickness, size * 2))
        
        # Border
        pygame.draw.rect(surface, self.WHITE,
                        pygame.Rect(center_x - size, center_y - thickness//2, 
                                   size * 2, thickness), 1)
        pygame.draw.rect(surface, self.WHITE,
                        pygame.Rect(center_x - thickness//2, center_y - size, 
                                   thickness, size * 2), 1)
    
    def draw_damage_powerup(self, surface, center_x, center_y):
        # Star/spike shape for damage
        num_spikes = 8
        outer_radius = int(12 * self.pulse)
        inner_radius = int(6 * self.pulse)
        
        points = []
        for i in range(num_spikes * 2):
            angle = self.rotation + (i * math.pi / num_spikes)
            if i % 2 == 0:  # Outer point
                radius = outer_radius
            else:  # Inner point
                radius = inner_radius
            
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            points.append((x, y))
        
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, self.WHITE, points, 2)
    
    def draw_speed_powerup(self, surface, center_x, center_y):
        # Lightning bolt shape for speed
        size = int(10 * self.pulse)
        
        # Lightning bolt points
        points = [
            (center_x - size//2, center_y - size),
            (center_x + size//4, center_y - size//4),
            (center_x - size//4, center_y - size//4),
            (center_x + size//2, center_y + size),
            (center_x - size//4, center_y + size//4),
            (center_x + size//4, center_y + size//4)
        ]
        
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, self.WHITE, points, 2) 