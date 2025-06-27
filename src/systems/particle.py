import pygame
import random
import math

class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, color, lifetime):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
        
    def update(self, dt):
        # Move particle
        self.x += self.velocity_x * (dt / 1000.0)
        self.y += self.velocity_y * (dt / 1000.0)
        
        # Apply gravity and friction
        self.velocity_y += 100 * (dt / 1000.0)  # Gravity
        self.velocity_x *= 0.995  # Friction
        self.velocity_y *= 0.995
        
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
            
            # Draw particle
            size = max(1, int(self.size * alpha_factor))
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color, particle_count):
        """Create an explosion effect at the given position"""
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
            
            particle = Particle(x, y, velocity_x, velocity_y, color_variant, lifetime)
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
            
            particle = Particle(x, y, velocity_x, velocity_y, color, lifetime)
            self.particles.append(particle)
    
    def create_muzzle_flash(self, x, y, direction_angle):
        """Create a muzzle flash effect for shooting"""
        for _ in range(5):
            # Particles fly forward from the gun
            angle = direction_angle + random.uniform(-math.pi/8, math.pi/8)
            speed = random.uniform(100, 200)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            lifetime = random.uniform(100, 300)
            color = (255, 255, 100)  # Yellow flash
            
            particle = Particle(x, y, velocity_x, velocity_y, color, lifetime)
            self.particles.append(particle)
    
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