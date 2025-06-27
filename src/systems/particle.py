import pygame
import random
import math

class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, color, lifetime, particle_type="default", size=None):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.particle_type = particle_type
        self.size = size if size else random.randint(2, 5)
        self.original_size = self.size
        
        # Enhanced properties
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-0.1, 0.1)
        self.scale = 1.0
        self.gravity_modifier = 1.0
        
        # Type-specific properties
        if particle_type == "spark":
            self.size = random.randint(1, 3)
            self.gravity_modifier = 0.3
        elif particle_type == "ember":
            self.size = random.randint(3, 6)
            self.gravity_modifier = 0.8
        elif particle_type == "smoke":
            self.size = random.randint(8, 15)
            self.gravity_modifier = -0.2  # Rises up
        elif particle_type == "energy":
            self.size = random.randint(4, 8)
            self.gravity_modifier = 0.0
            self.rotation_speed = random.uniform(-0.3, 0.3)
        
    def update(self, dt):
        dt_factor = dt / 1000.0
        
        # Move particle
        self.x += self.velocity_x * dt_factor
        self.y += self.velocity_y * dt_factor
        
        # Apply gravity and friction based on type
        gravity_strength = 100 * self.gravity_modifier
        self.velocity_y += gravity_strength * dt_factor
        
        # Air resistance
        resistance = 0.995 if self.particle_type != "energy" else 0.98
        self.velocity_x *= resistance
        self.velocity_y *= resistance
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update scale for certain types
        if self.particle_type == "smoke":
            age_factor = 1 - (self.lifetime / self.max_lifetime)
            self.scale = 1.0 + age_factor * 2  # Smoke grows over time
        elif self.particle_type == "energy":
            self.scale = 1.0 + 0.3 * math.sin(self.rotation * 3)
        
        # Decrease lifetime
        self.lifetime -= dt
        
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.lifetime > 0:
            # Calculate alpha based on remaining lifetime
            alpha_factor = self.lifetime / self.max_lifetime
            
            # Adjust color with alpha
            color = (
                int(self.color[0] * alpha_factor),
                int(self.color[1] * alpha_factor),
                int(self.color[2] * alpha_factor)
            )
            
            # Calculate current size
            current_size = max(1, int(self.original_size * self.scale * alpha_factor))
            
            # Type-specific drawing
            if self.particle_type == "spark":
                # Draw as bright line
                end_x = self.x + math.cos(self.rotation) * current_size * 2
                end_y = self.y + math.sin(self.rotation) * current_size * 2
                pygame.draw.line(surface, color, (int(self.x), int(self.y)), (int(end_x), int(end_y)), max(1, current_size))
            elif self.particle_type == "ember":
                # Draw as glowing circle
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), current_size)
                # Inner bright core
                core_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
                pygame.draw.circle(surface, core_color, (int(self.x), int(self.y)), max(1, current_size // 2))
            elif self.particle_type == "smoke":
                # Draw as fading circle
                smoke_color = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.circle(surface, smoke_color, (int(self.x), int(self.y)), current_size)
            elif self.particle_type == "energy":
                # Draw as pulsating energy ball
                pulse_size = current_size + int(2 * math.sin(self.rotation * 4))
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), max(1, pulse_size))
                # Bright center
                pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), max(1, pulse_size // 3))
            else:
                # Default particle
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), current_size)


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color, particle_count):
        """Create an enhanced explosion effect at the given position"""
        for _ in range(particle_count):
            # Random velocity in all directions
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            # Random lifetime
            lifetime = random.uniform(300, 800)
            
            # Add some color variation
            color_variant = (
                min(255, max(0, color[0] + random.randint(-30, 30))),
                min(255, max(0, color[1] + random.randint(-30, 30))),
                min(255, max(0, color[2] + random.randint(-30, 30)))
            )
            
            # Mix of particle types for more interesting explosions
            particle_type = random.choice(["default", "spark", "ember"])
            
            particle = Particle(x, y, velocity_x, velocity_y, color_variant, lifetime, particle_type)
            self.particles.append(particle)
    
    def create_enhanced_explosion(self, x, y, color, intensity=1.0):
        """Create a more dramatic explosion with multiple particle types"""
        base_count = int(20 * intensity)
        
        # Main explosion particles
        self.create_explosion(x, y, color, base_count)
        
        # Add sparks
        for _ in range(int(8 * intensity)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(150, 300)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            lifetime = random.uniform(200, 400)
            
            spark_color = (min(255, color[0] + 50), min(255, color[1] + 50), 255)
            particle = Particle(x, y, velocity_x, velocity_y, spark_color, lifetime, "spark")
            self.particles.append(particle)
        
        # Add smoke
        for _ in range(int(5 * intensity)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 60)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            lifetime = random.uniform(800, 1200)
            
            smoke_color = (color[0] // 3, color[1] // 3, color[2] // 3)
            particle = Particle(x, y, velocity_x, velocity_y, smoke_color, lifetime, "smoke")
            self.particles.append(particle)
    
    def create_hit_effect(self, x, y, color, direction_angle):
        """Create a directional hit effect"""
        for _ in range(8):
            # Particles fly in a cone from the hit direction
            angle = direction_angle + random.uniform(-math.pi/4, math.pi/4)
            speed = random.uniform(80, 150)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            lifetime = random.uniform(200, 500)
            
            particle = Particle(x, y, velocity_x, velocity_y, color, lifetime, "spark")
            self.particles.append(particle)
    
    def create_muzzle_flash(self, x, y, direction_angle):
        """Create an enhanced muzzle flash effect for shooting"""
        for _ in range(8):
            # Particles fly forward from the gun
            angle = direction_angle + random.uniform(-math.pi/8, math.pi/8)
            speed = random.uniform(100, 200)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            lifetime = random.uniform(100, 300)
            color = (255, 255, 100)  # Yellow flash
            
            particle_type = random.choice(["spark", "energy"])
            particle = Particle(x, y, velocity_x, velocity_y, color, lifetime, particle_type)
            self.particles.append(particle)
    
    def create_energy_trail(self, x, y, color, direction_angle):
        """Create energy trail particles for special weapons"""
        for _ in range(3):
            # Small random offset
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            
            # Slight random velocity
            velocity_x = random.uniform(-20, 20)
            velocity_y = random.uniform(-20, 20)
            
            lifetime = random.uniform(150, 300)
            
            particle = Particle(x + offset_x, y + offset_y, velocity_x, velocity_y, color, lifetime, "energy")
            self.particles.append(particle)
    
    def create_death_explosion(self, x, y, enemy_type):
        """Create type-specific death explosions"""
        if enemy_type == "boss":
            # Massive explosion for bosses
            colors = [(255, 100, 255), (255, 150, 100), (150, 100, 255)]
            for color in colors:
                self.create_enhanced_explosion(x, y, color, 2.0)
        elif enemy_type == "tank" or enemy_type == "heavy":
            # Heavy explosion for tank enemies
            self.create_enhanced_explosion(x, y, (255, 100, 100), 1.5)
        else:
            # Standard explosion
            self.create_enhanced_explosion(x, y, (255, 100, 150), 1.0)
    
    def update(self, dt):
        """Update all particles and remove dead ones"""
        self.particles = [particle for particle in self.particles if particle.update(dt)]
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)
    
    def get_particle_count(self):
        """Get the current number of particles"""
        return len(self.particles) 