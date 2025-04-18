import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, settings):
        self.x = x
        self.y = y
        self.color = color
        self.settings = settings
        self.lifetime = settings.PARTICLE_LIFETIME
        self.size = random.randint(2, 6)
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.uniform(0, math.pi * 2)
        self.velocity_x = math.cos(self.angle) * self.speed
        self.velocity_y = math.sin(self.angle) * self.speed
        self.alpha = 255
        self.alpha_decay = 255 / self.lifetime
        
    def update(self):
        # Move particle
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Add gravity effect
        self.velocity_y += 0.05
        
        # Slow down over time
        self.velocity_x *= 0.97
        self.velocity_y *= 0.97
        
        # Shrink particle over time
        if self.size > 0.5:
            self.size *= 0.95
            
        # Reduce opacity over time
        self.alpha -= self.alpha_decay
        if self.alpha < 0:
            self.alpha = 0
            
        # Reduce lifetime
        self.lifetime -= 1
        
    def is_alive(self):
        return self.lifetime > 0
        
    def draw(self, screen):
        # Create a surface with alpha transparency
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        # Draw the particle with appropriate alpha
        pygame.draw.circle(s, (*self.color, int(self.alpha)), (self.size, self.size), self.size)
        # Blit the surface onto the screen
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))
        

class ParticleSystem:
    def __init__(self, settings):
        self.settings = settings
        self.particles = []
        
    def create_particles(self, x, y, count, color=None):
        for _ in range(count):
            # If no color is provided, choose from the particle colors in settings
            if color is None:
                particle_color = random.choice(self.settings.PARTICLE_COLORS)
            else:
                particle_color = color
                
            self.particles.append(Particle(x, y, particle_color, self.settings))
            
    def update(self):
        # Update all particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen) 