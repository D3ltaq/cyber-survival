import pygame
import math
import random

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
    
    def draw(self, surface, custom_center=None, camera_offset=(0, 0)):
        # Use custom center if provided, otherwise use rect center
        center = custom_center if custom_center else self.rect.center
        
        # Draw trail first (behind projectile) with camera offset
        self._draw_trail(surface, center, camera_offset)
        
        # Weapon-specific drawing
        if self.weapon_type == "laser_rifle":
            self._draw_laser_projectile(surface, center)
        elif self.weapon_type == "plasma_cannon":
            self._draw_plasma_projectile(surface, center)
        elif self.weapon_type == "shotgun":
            self._draw_shotgun_projectile(surface, center)
        elif self.weapon_type == "sniper_rifle":
            self._draw_sniper_projectile(surface, center)
        elif self.weapon_type == "machine_gun":
            self._draw_machine_gun_projectile(surface, center)
        elif self.weapon_type == "energy_beam":
            self._draw_energy_beam_projectile(surface, center)
        else:
            self._draw_default_projectile(surface, center)
    
    def _draw_trail(self, surface, center, camera_offset=(0, 0)):
        """Draw an enhanced trail behind the projectile"""
        if len(self.trail_positions) < 2:
            return
        
        camera_x, camera_y = camera_offset
        
        # Draw trail with fading alpha and width
        for i, (trail_x, trail_y) in enumerate(self.trail_positions[:-1]):
            if i < len(self.trail_positions) - 1:
                next_x, next_y = self.trail_positions[i + 1]
                
                # Apply camera offset to trail positions
                screen_trail_x = trail_x + camera_x
                screen_trail_y = trail_y + camera_y
                screen_next_x = next_x + camera_x
                screen_next_y = next_y + camera_y
                
                # Calculate alpha and width based on position in trail
                alpha_factor = (i + 1) / len(self.trail_positions)
                trail_width = max(1, int(self.size * alpha_factor * 0.8))
                
                # Color with alpha
                trail_color = (
                    int(self.color[0] * alpha_factor * 0.6),
                    int(self.color[1] * alpha_factor * 0.6),
                    int(self.color[2] * alpha_factor * 0.6)
                )
                
                # Draw trail segment
                if trail_width > 0:
                    pygame.draw.line(surface, trail_color, 
                                   (int(screen_trail_x), int(screen_trail_y)), 
                                   (int(screen_next_x), int(screen_next_y)), trail_width)
    
    def _draw_laser_projectile(self, surface, center):
        """Draw an enhanced bright, fast laser beam"""
        # Long thin laser with bright core
        length = 20
        width = 3
        
        # Calculate end points
        front_x = center[0] + math.cos(self.angle) * length
        front_y = center[1] + math.sin(self.angle) * length
        back_x = center[0] - math.cos(self.angle) * length
        back_y = center[1] - math.sin(self.angle) * length
        
        # Outer glow (multiple layers for better effect)
        for glow_width in [width + 8, width + 6, width + 4]:
            glow_intensity = 30 + (width + 8 - glow_width) * 10
            glow_color = (glow_intensity, glow_intensity, min(255, glow_intensity + 50))
            pygame.draw.line(surface, glow_color, (back_x, back_y), (front_x, front_y), glow_width)
        
        # Main beam
        pygame.draw.line(surface, self.color, (back_x, back_y), (front_x, front_y), width)
        # Bright core
        pygame.draw.line(surface, (255, 255, 255), (back_x, back_y), (front_x, front_y), 1)
        
        # Add lens flare effect at tip
        flare_size = 8
        pygame.draw.circle(surface, (255, 255, 255), (int(front_x), int(front_y)), flare_size, 1)
        pygame.draw.circle(surface, self.color, (int(front_x), int(front_y)), flare_size // 2, 1)
    
    def _draw_plasma_projectile(self, surface, center):
        """Draw an enhanced large, pulsating plasma ball"""
        base_size = self.size + 4
        current_size = int(base_size * self.pulse_scale)
        
        # Multiple layers for enhanced plasma effect
        # Outer energy field
        for layer in range(3, 0, -1):
            layer_size = current_size + layer * 3
            layer_alpha = 50 + layer * 30
            layer_color = (
                min(255, int(self.color[0] * 0.3 + layer_alpha)),
                min(255, int(self.color[1] * 0.3 + layer_alpha // 2)),
                min(255, int(self.color[2] * 0.8 + layer_alpha))
            )
            pygame.draw.circle(surface, layer_color, center, layer_size, 2)
        
        # Main plasma core
        pygame.draw.circle(surface, self.color, center, current_size)
        # Inner bright core
        inner_size = max(1, current_size // 2)
        pygame.draw.circle(surface, (200, 150, 255), center, inner_size)
        # Center spark
        spark_size = max(1, current_size // 4)
        pygame.draw.circle(surface, (255, 255, 255), center, spark_size)
        
        # Add energy arcs
        for i in range(4):
            arc_angle = self.animation_timer * 0.01 + i * math.pi / 2
            arc_end_x = center[0] + math.cos(arc_angle) * current_size
            arc_end_y = center[1] + math.sin(arc_angle) * current_size
            pygame.draw.line(surface, (150, 100, 255), center, (int(arc_end_x), int(arc_end_y)), 1)
    
    def _draw_shotgun_projectile(self, surface, center):
        """Draw enhanced small, fast pellets"""
        # Outer glow
        glow_size = self.size + 2
        pygame.draw.circle(surface, (255, 50, 150), center, glow_size)
        
        # Main pellet
        pygame.draw.circle(surface, self.color, center, self.size)
        
        # Bright center
        center_size = max(1, self.size - 1)
        pygame.draw.circle(surface, (255, 255, 255), center, center_size)
        
        # Add spark effect
        spark_length = 6
        spark_angle = self.angle + random.uniform(-0.2, 0.2)
        spark_end_x = center[0] - math.cos(spark_angle) * spark_length
        spark_end_y = center[1] - math.sin(spark_angle) * spark_length
        pygame.draw.line(surface, (255, 200, 100), center, (int(spark_end_x), int(spark_end_y)), 1)
    
    def _draw_sniper_projectile(self, surface, center):
        """Draw an enhanced precise, long-range bullet with vapor trail"""
        length = 25
        width = 2
        
        # Calculate end points
        front_x = center[0] + math.cos(self.angle) * length
        front_y = center[1] + math.sin(self.angle) * length
        back_x = center[0] - math.cos(self.angle) * length * 0.8
        back_y = center[1] - math.sin(self.angle) * length * 0.8
        
        # Vapor trail effect
        for i in range(5):
            trail_offset = i * 3
            trail_x = back_x - math.cos(self.angle) * trail_offset
            trail_y = back_y - math.sin(self.angle) * trail_offset
            trail_alpha = 255 - i * 40
            trail_color = (trail_alpha, trail_alpha, 50)
            pygame.draw.circle(surface, trail_color, (int(trail_x), int(trail_y)), max(1, 3 - i))
        
        # Main tracer beam
        pygame.draw.line(surface, (255, 255, 50), (back_x, back_y), (front_x, front_y), width + 2)
        pygame.draw.line(surface, self.color, (back_x, back_y), (front_x, front_y), width)
        
        # Bright bullet tip
        pygame.draw.circle(surface, (255, 255, 255), (int(front_x), int(front_y)), 3)
        pygame.draw.circle(surface, self.color, (int(front_x), int(front_y)), 2)
    
    def _draw_machine_gun_projectile(self, surface, center):
        """Draw enhanced rapid-fire bullets with muzzle flash residue"""
        length = 10
        
        # Calculate end points
        front_x = center[0] + math.cos(self.angle) * length
        front_y = center[1] + math.sin(self.angle) * length
        back_x = center[0] - math.cos(self.angle) * length
        back_y = center[1] - math.sin(self.angle) * length
        
        # Bullet trail with heat distortion
        for width in [4, 3, 2]:
            heat_color = (255 - width * 30, 150 + width * 20, 50)
            pygame.draw.line(surface, heat_color, (back_x, back_y), (front_x, front_y), width)
        
        # Core bullet
        pygame.draw.line(surface, self.color, (back_x, back_y), (front_x, front_y), 1)
        
        # Hot tip
        pygame.draw.circle(surface, (255, 255, 100), (int(front_x), int(front_y)), 2)
    
    def _draw_energy_beam_projectile(self, surface, center):
        """Draw enhanced continuous energy beam segments"""
        # Pulsating energy ball with electric arcs
        size = int(self.size * self.pulse_scale)
        
        # Energy field
        for layer in range(3):
            layer_size = size + (3 - layer) * 2
            layer_intensity = 100 + layer * 50
            field_color = (100, layer_intensity, 100)
            pygame.draw.circle(surface, field_color, center, layer_size, 1)
        
        # Main energy core
        pygame.draw.circle(surface, self.color, center, size)
        
        # Electric arcs
        for i in range(6):
            arc_angle = self.animation_timer * 0.02 + i * math.pi / 3
            arc_length = size + 5
            arc_end_x = center[0] + math.cos(arc_angle) * arc_length
            arc_end_y = center[1] + math.sin(arc_angle) * arc_length
            arc_color = (150, 255, 150)
            pygame.draw.line(surface, arc_color, center, (int(arc_end_x), int(arc_end_y)), 1)
        
        # Bright center
        pygame.draw.circle(surface, (255, 255, 255), center, max(1, size // 2))
    
    def _draw_default_projectile(self, surface, center):
        """Draw an enhanced default projectile with glow"""
        # Outer glow
        for glow_layer in range(3, 0, -1):
            glow_size = self.size + glow_layer * 2
            glow_alpha = 60 - glow_layer * 15
            glow_color = (
                min(255, int(self.color[0] * 0.4 + glow_alpha)),
                min(255, int(self.color[1] * 0.4 + glow_alpha)),
                min(255, int(self.color[2] * 0.8 + glow_alpha))
            )
            pygame.draw.circle(surface, glow_color, center, glow_size, 1)
        
        # Main projectile
        pygame.draw.circle(surface, self.color, center, self.size)
        
        # Bright core
        core_size = max(1, self.size - 2)
        pygame.draw.circle(surface, (255, 255, 255), center, core_size)
        
        # Energy sparkle
        sparkle_size = max(1, self.size // 2)
        sparkle_brightness = int(200 + 55 * math.sin(self.animation_timer * 0.02))
        sparkle_color = (sparkle_brightness, sparkle_brightness, 255)
        pygame.draw.circle(surface, sparkle_color, center, sparkle_size) 