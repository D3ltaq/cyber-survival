import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage=20, speed=500, size=6, color=None, weapon_type="default", max_range=600):
        super().__init__()
        self.size = size
        half_size = size // 2
        self.rect = pygame.Rect(x - half_size, y - half_size, size, size)
        self.image = pygame.Surface((size, size))  # Required for pygame sprite
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        self.damage = damage
        self.speed = speed
        self.weapon_type = weapon_type
        self.max_range = max_range
        self.distance_traveled = 0
        self.start_x = x
        self.start_y = y
        
        # Calculate velocity components
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        
        # Visual properties
        self.angle = angle
        self.trail_positions = []
        self.max_trail_length = self._get_trail_length()
        
        # Upgrade properties
        self.piercing = False
        self.explosive = False
        self.pierced_enemies = set()  # Track enemies already hit for piercing
        
        # Weapon-specific properties
        self.animation_timer = 0
        self.pulse_scale = 1.0
        
        # Default colors
        self.NEON_CYAN = (0, 255, 255)
        self.ELECTRIC_BLUE = (125, 249, 255)
        self.WHITE = (255, 255, 255)
        
        # Custom color override or weapon-specific color
        self.color = color if color else self._get_weapon_color()
    
    def _get_trail_length(self):
        """Get trail length based on weapon type"""
        trail_lengths = {
            "default": 8,
            "laser_rifle": 12,
            "plasma_cannon": 6,
            "shotgun": 4,
            "sniper_rifle": 15,
            "machine_gun": 6,
            "energy_beam": 20
        }
        return trail_lengths.get(self.weapon_type, 8)
    
    def _get_weapon_color(self):
        """Get default color based on weapon type"""
        weapon_colors = {
            "default": (0, 255, 255),  # Cyan
            "laser_rifle": (108, 178, 255),  # Electric Blue
            "plasma_cannon": (134, 108, 255),  # Purple
            "shotgun": (255, 108, 222),  # Hot Pink
            "sniper_rifle": (255, 255, 100),  # Yellow
            "machine_gun": (255, 150, 50),  # Orange
            "energy_beam": (200, 255, 200),  # Light Green
            "auto_targeting": (255, 200, 255)  # Light Purple
        }
        return weapon_colors.get(self.weapon_type, self.NEON_CYAN)
    
    def update(self, dt):
        # Store current position for trail
        self.trail_positions.append((self.rect.centerx, self.rect.centery))
        
        # Limit trail length
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Move projectile
        move_factor = dt / 1000.0
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += self.velocity_x * move_factor
        self.rect.y += self.velocity_y * move_factor
        
        # Calculate distance traveled
        dx = self.rect.x - old_x
        dy = self.rect.y - old_y
        self.distance_traveled += math.sqrt(dx * dx + dy * dy)
        
        # Update animation timer for weapon-specific effects
        self.animation_timer += dt
        self.pulse_scale = 1.0 + 0.2 * math.sin(self.animation_timer * 0.01)
        
        # Check if projectile exceeded its range
        if self.distance_traveled > self.max_range:
            # Mark for removal by moving off-screen
            self.rect.x = -1000
            self.rect.y = -1000
    
    def draw(self, surface):
        # Weapon-specific drawing
        if self.weapon_type == "laser_rifle":
            self._draw_laser_projectile(surface)
        elif self.weapon_type == "plasma_cannon":
            self._draw_plasma_projectile(surface)
        elif self.weapon_type == "shotgun":
            self._draw_shotgun_projectile(surface)
        elif self.weapon_type == "sniper_rifle":
            self._draw_sniper_projectile(surface)
        elif self.weapon_type == "machine_gun":
            self._draw_machine_gun_projectile(surface)
        elif self.weapon_type == "energy_beam":
            self._draw_energy_beam_projectile(surface)
        else:
            self._draw_default_projectile(surface)
    
    def _draw_laser_projectile(self, surface):
        """Draw a bright, fast laser beam"""
        # Long thin laser with bright core
        center = self.rect.center
        length = 15
        width = 2
        
        # Calculate end points
        front_x = center[0] + math.cos(self.angle) * length
        front_y = center[1] + math.sin(self.angle) * length
        back_x = center[0] - math.cos(self.angle) * length
        back_y = center[1] - math.sin(self.angle) * length
        
        # Outer glow
        pygame.draw.line(surface, (50, 50, 255), (back_x, back_y), (front_x, front_y), width + 4)
        # Inner beam
        pygame.draw.line(surface, self.color, (back_x, back_y), (front_x, front_y), width)
        # Core
        pygame.draw.line(surface, (255, 255, 255), (back_x, back_y), (front_x, front_y), 1)
    
    def _draw_plasma_projectile(self, surface):
        """Draw a large, pulsating plasma ball"""
        center = self.rect.center
        base_size = self.size
        current_size = int(base_size * self.pulse_scale)
        
        # Multiple layers for plasma effect
        # Outer glow
        pygame.draw.circle(surface, (80, 40, 180), center, current_size + 3)
        # Main plasma
        pygame.draw.circle(surface, self.color, center, current_size)
        # Inner core
        pygame.draw.circle(surface, (200, 150, 255), center, current_size // 2)
        # Center spark
        pygame.draw.circle(surface, (255, 255, 255), center, max(1, current_size // 4))
    
    def _draw_shotgun_projectile(self, surface):
        """Draw small, fast pellets"""
        center = self.rect.center
        
        # Small bright pellet
        pygame.draw.circle(surface, (255, 50, 150), center, self.size)
        pygame.draw.circle(surface, self.color, center, self.size - 1)
        pygame.draw.circle(surface, (255, 255, 255), center, max(1, self.size - 2))
    
    def _draw_sniper_projectile(self, surface):
        """Draw a precise, long-range bullet"""
        center = self.rect.center
        length = 20
        width = 1
        
        # Calculate end points
        front_x = center[0] + math.cos(self.angle) * length
        front_y = center[1] + math.sin(self.angle) * length
        back_x = center[0] - math.cos(self.angle) * length
        back_y = center[1] - math.sin(self.angle) * length
        
        # Tracer effect
        pygame.draw.line(surface, (255, 255, 50), (back_x, back_y), (front_x, front_y), width + 2)
        pygame.draw.line(surface, self.color, (back_x, back_y), (front_x, front_y), width)
        
        # Bright tip
        pygame.draw.circle(surface, (255, 255, 255), (int(front_x), int(front_y)), 2)
    
    def _draw_machine_gun_projectile(self, surface):
        """Draw rapid-fire bullets"""
        center = self.rect.center
        length = 8
        
        # Calculate end points
        front_x = center[0] + math.cos(self.angle) * length
        front_y = center[1] + math.sin(self.angle) * length
        back_x = center[0] - math.cos(self.angle) * length
        back_y = center[1] - math.sin(self.angle) * length
        
        # Simple bullet
        pygame.draw.line(surface, self.color, (back_x, back_y), (front_x, front_y), 3)
        pygame.draw.line(surface, (255, 200, 100), (back_x, back_y), (front_x, front_y), 1)
    
    def _draw_energy_beam_projectile(self, surface):
        """Draw continuous energy beam segments"""
        center = self.rect.center
        
        # Pulsating energy ball
        size = int(self.size * self.pulse_scale)
        pygame.draw.circle(surface, (100, 255, 100), center, size + 2)
        pygame.draw.circle(surface, self.color, center, size)
        pygame.draw.circle(surface, (255, 255, 255), center, max(1, size // 2))
    
    def _draw_default_projectile(self, surface):
        """Draw the original default projectile style"""
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