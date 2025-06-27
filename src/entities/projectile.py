import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage=20, speed=500, size=6, color=None):
        super().__init__()
        self.size = size
        half_size = size // 2
        self.rect = pygame.Rect(x - half_size, y - half_size, size, size)
        self.image = pygame.Surface((size, size))  # Required for pygame sprite
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        self.damage = damage
        self.speed = speed
        
        # Calculate velocity components
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        
        # Visual properties
        self.angle = angle
        self.trail_positions = []
        self.max_trail_length = 8
        
        # Upgrade properties
        self.piercing = False
        self.explosive = False
        self.pierced_enemies = set()  # Track enemies already hit for piercing
        
        # Default colors
        self.NEON_CYAN = (0, 255, 255)
        self.ELECTRIC_BLUE = (125, 249, 255)
        self.WHITE = (255, 255, 255)
        
        # Custom color override
        self.color = color if color else self.NEON_CYAN
    
    def update(self, dt):
        # Store current position for trail
        self.trail_positions.append((self.rect.centerx, self.rect.centery))
        
        # Limit trail length
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Move projectile
        move_factor = dt / 1000.0
        self.rect.x += self.velocity_x * move_factor
        self.rect.y += self.velocity_y * move_factor
    
    def draw(self, surface):
        # Draw trail
        for i, pos in enumerate(self.trail_positions):
            alpha_factor = i / len(self.trail_positions)
            trail_color = (
                int(self.color[0] * alpha_factor),
                int(self.color[1] * alpha_factor),
                int(self.color[2] * alpha_factor)
            )
            trail_size = max(1, int((self.size // 2) * alpha_factor))
            pygame.draw.circle(surface, trail_color, pos, trail_size)
        
        # Draw main projectile as energy bolt
        center = self.rect.center
        
        # Scale projectile length based on size
        proj_length = max(6, self.size + 2)
        half_length = proj_length // 2
        
        # Front and back points of the bolt
        front_x = center[0] + math.cos(self.angle) * half_length
        front_y = center[1] + math.sin(self.angle) * half_length
        back_x = center[0] - math.cos(self.angle) * half_length
        back_y = center[1] - math.sin(self.angle) * half_length
        
        # Perpendicular direction for width
        perp_angle = self.angle + math.pi / 2
        width = max(2, self.size // 2)
        
        # Create diamond/bolt shape
        bolt_points = [
            (front_x, front_y),  # Front tip
            (center[0] + math.cos(perp_angle) * width, center[1] + math.sin(perp_angle) * width),  # Side
            (back_x, back_y),    # Back
            (center[0] - math.cos(perp_angle) * width, center[1] - math.sin(perp_angle) * width)   # Other side
        ]
        
        # Draw outer glow (lighter version of custom color)
        glow_color = tuple(min(255, int(c * 1.2)) for c in self.color)
        pygame.draw.circle(surface, glow_color, center, max(3, self.size // 2))
        
        # Draw the energy bolt
        pygame.draw.polygon(surface, self.color, bolt_points)
        
        # Inner core line
        pygame.draw.line(surface, self.WHITE, (back_x, back_y), (front_x, front_y), max(1, self.size // 4))
        
        # Energy sparks (small additional effects)
        spark_offset = max(1, self.size // 4)
        pygame.draw.circle(surface, self.WHITE, 
                          (int(front_x), int(front_y)), 1)
        pygame.draw.circle(surface, self.color, 
                          (int(center[0] + math.cos(self.angle + 0.5) * spark_offset), 
                           int(center[1] + math.sin(self.angle + 0.5) * spark_offset)), 1) 