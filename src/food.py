import pygame
import random
import math
from src.particle import ParticleSystem

class Food:
    def __init__(self, settings, food_type="apple"):
        self.settings = settings
        self.food_type = food_type
        self.position = (0, 0)
        self.lifetime = None  # None for indefinite or milliseconds if timed
        self.spawn_time = pygame.time.get_ticks()
        
        # Set properties based on food type
        if food_type == "apple":
            self.points = 1
            self.color = self.settings.FOOD_COLORS['apple']
            self.radius = self.settings.CELL_SIZE // 2
            self.lifetime = None  # Permanent until eaten
        elif food_type == "bonus":
            self.points = 3
            self.color = self.settings.FOOD_COLORS['bonus']
            self.radius = self.settings.CELL_SIZE // 2 * 1.2
            self.lifetime = 8000  # 8 seconds
        elif food_type == "power":
            self.points = 2
            self.color = self.settings.FOOD_COLORS['power']
            self.radius = self.settings.CELL_SIZE // 2 * 1.1
            self.lifetime = 6000  # 6 seconds
            # Randomly choose a power-up type
            self.powerup_type = random.choice(["speed", "slow", "shrink", "ghost"])
            
        # For visual effects
        self.pulse_effect = random.random()
        self.pulse_direction = 1 if random.random() > 0.5 else -1
        self.angle = random.randint(0, 360)
        self.rotation_speed = random.uniform(0.5, 2.0) * self.pulse_direction
        
        self.particle_system = ParticleSystem(settings)
        self.despawn_time = None
        
        # Set food properties based on type
        if food_type == "apple":
            self.despawn_time = None  # Regular food never despawns
        elif food_type == "bonus":
            self.despawn_time = 8000  # Bonus food despawns after 8 seconds
        elif food_type == "power":
            self.despawn_time = 5000  # Power-ups despawn after 5 seconds
        
        # Place food in a valid position (initially random)
        self.respawn(None)
        
    def respawn(self, occupied_positions):
        """Place food in a random position that doesn't overlap with the snake or obstacles."""
        valid_position = False
        attempts = 0
        max_attempts = 100
        
        # Make sure occupied_positions is a list
        if occupied_positions is None:
            occupied_positions = []
        
        # Flatten the occupied_positions if it's a list of tuples
        occupied_positions_set = set(occupied_positions)
        
        while not valid_position and attempts < max_attempts:
            # Generate random position
            x = random.randint(1, self.settings.GRID_WIDTH - 2)
            y = random.randint(1, self.settings.GRID_HEIGHT - 2)
            
            # Check if position is valid (not on snake or obstacles)
            if (x, y) not in occupied_positions_set:
                valid_position = True
                self.position = (x, y)
                self.spawn_time = pygame.time.get_ticks()
                
            attempts += 1
            
        if not valid_position:
            # If we couldn't find a valid position after max attempts, try a more systematic approach
            for x in range(1, self.settings.GRID_WIDTH - 1):
                for y in range(1, self.settings.GRID_HEIGHT - 1):
                    if (x, y) not in occupied_positions_set:
                        self.position = (x, y)
                        self.spawn_time = pygame.time.get_ticks()
                        return
            
            # If still no valid position, place it in the center as a last resort
            self.position = (self.settings.GRID_WIDTH // 2, self.settings.GRID_HEIGHT // 2)
            self.spawn_time = pygame.time.get_ticks()
                        
    def update(self):
        """Update food state and animations. Return False if expired."""
        current_time = pygame.time.get_ticks()
        
        # Update animation effects
        self.pulse_effect += 0.05 * self.pulse_direction
        if self.pulse_effect > 1.0:
            self.pulse_effect = 1.0
            self.pulse_direction = -1
        elif self.pulse_effect < 0.0:
            self.pulse_effect = 0.0
            self.pulse_direction = 1
            
        # Update rotation
        self.angle = (self.angle + self.rotation_speed) % 360
        
        # Check if food has expired
        if self.lifetime and current_time - self.spawn_time > self.lifetime:
            return False
            
        return True
        
    def draw(self, screen):
        """Draw food with enhanced visual effects."""
        # Calculate screen position
        x = self.position[0] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        y = self.position[1] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        
        # Calculate animation effects
        pulse_amount = self.pulse_effect * 0.2
        radius = self.radius * (1 + pulse_amount)
        
        # Draw glow effect for all food types if enabled
        if self.settings.GLOW_EFFECTS_ENABLED:
            # Create larger glow for bonus and power-up foods
            glow_multiplier = 1.0
            if self.food_type == "bonus":
                glow_multiplier = 1.5
            elif self.food_type == "power":
                glow_multiplier = 1.3
                
            # Draw outer glow
            for i in range(3):
                glow_radius = radius * (1.5 - i * 0.2) * glow_multiplier
                alpha = 120 - i * 30
                glow_color = (*self.color, alpha)
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, 
                                  (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, 
                           (x - glow_radius, y - glow_radius),
                           special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw base food shape with subtle 3D effect
        pygame.draw.circle(screen, (0, 0, 0, 180), (x+2, y+2), radius)  # Shadow
        pygame.draw.circle(screen, self.color, (x, y), radius)
        
        # Add visual details based on food type
        if self.food_type == "apple":
            # Draw apple stem
            stem_color = (100, 50, 0)
            stem_pos1 = (x, y - radius * 0.8)
            stem_pos2 = (x + radius * 0.3, y - radius * 1.2)
            pygame.draw.line(screen, stem_color, stem_pos1, stem_pos2, 2)
            
            # Draw apple highlight
            highlight_pos = (x - radius * 0.3, y - radius * 0.3)
            highlight_radius = radius * 0.25
            pygame.draw.circle(screen, (255, 255, 255, 120), highlight_pos, highlight_radius)
            
        elif self.food_type == "bonus":
            # Draw star shape inside bonus food
            self._draw_star(screen, x, y, radius * 0.7, 5, self.angle)
            
            # Draw shimmer effect
            for i in range(2):
                shimmer_angle = (self.angle + i * 180) % 360
                shimmer_x = x + math.cos(math.radians(shimmer_angle)) * radius * 0.6
                shimmer_y = y + math.sin(math.radians(shimmer_angle)) * radius * 0.6
                shimmer_radius = radius * 0.15
                pygame.draw.circle(screen, (255, 255, 255, 150), 
                                  (shimmer_x, shimmer_y), shimmer_radius)
                
        elif self.food_type == "power":
            # Draw power-up icon
            if self.powerup_type == "speed":
                self._draw_lightning(screen, x, y, radius)
            elif self.powerup_type == "slow":
                self._draw_clock(screen, x, y, radius)
            elif self.powerup_type == "shrink":
                self._draw_shrink(screen, x, y, radius)
            elif self.powerup_type == "ghost":
                self._draw_ghost(screen, x, y, radius)
                
        # Create occasional particles for bonus and power-up food
        if self.food_type in ["bonus", "power"] and random.random() < 0.1:
            pixel_x = self.position[0] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
            pixel_y = self.position[1] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
            color = self.color
            self.particle_system.create_particles(pixel_x, pixel_y, 1, color)
            
        # Update particles
        self.particle_system.update()
        
        # Check if food should despawn
        if self.despawn_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.spawn_time >= self.despawn_time:
                return False  # Signal that food should be removed
                
        return True  # Food should stay
        
    def _draw_star(self, screen, x, y, radius, points, angle_offset=0):
        """Draw a star shape."""
        # Calculate points of the star
        outer_points = []
        inner_points = []
        
        for i in range(points * 2):
            angle = math.radians(i * 180 / points + angle_offset)
            # Alternate between outer and inner points
            if i % 2 == 0:
                px = x + math.cos(angle) * radius
                py = y + math.sin(angle) * radius
                outer_points.append((px, py))
            else:
                px = x + math.cos(angle) * radius * 0.4
                py = y + math.sin(angle) * radius * 0.4
                inner_points.append((px, py))
                
        # Combine points in correct order
        star_points = []
        for i in range(points):
            star_points.append(outer_points[i])
            star_points.append(inner_points[i])
            
        # Draw star
        pygame.draw.polygon(screen, (255, 255, 100), star_points)
        
    def _draw_lightning(self, screen, x, y, radius):
        """Draw lightning icon for speed power-up."""
        points = [
            (x - radius*0.3, y - radius*0.7),  # Top left
            (x + radius*0.1, y - radius*0.2),  # Middle upper right
            (x - radius*0.1, y - radius*0.2),  # Middle upper left
            (x + radius*0.3, y + radius*0.7),  # Bottom right
            (x - radius*0.1, y + radius*0.2),  # Middle lower left
            (x + radius*0.1, y + radius*0.2),  # Middle lower right
        ]
        pygame.draw.polygon(screen, (255, 255, 0), points)
        
    def _draw_clock(self, screen, x, y, radius):
        """Draw clock icon for slow power-up."""
        # Draw clock face
        pygame.draw.circle(screen, (220, 220, 220), (x, y), radius*0.6)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), radius*0.6, 2)
        
        # Draw clock hands
        hand_length = radius * 0.5
        minute_angle = math.radians(self.angle)
        hour_angle = math.radians(self.angle / 12)
        
        # Hour hand
        hour_x = x + math.sin(hour_angle) * hand_length * 0.6
        hour_y = y - math.cos(hour_angle) * hand_length * 0.6
        pygame.draw.line(screen, (0, 0, 0), (x, y), (hour_x, hour_y), 3)
        
        # Minute hand
        minute_x = x + math.sin(minute_angle) * hand_length
        minute_y = y - math.cos(minute_angle) * hand_length
        pygame.draw.line(screen, (0, 0, 0), (x, y), (minute_x, minute_y), 2)
        
    def _draw_shrink(self, screen, x, y, radius):
        """Draw shrink icon for shrink power-up."""
        arrow_size = radius * 0.7
        
        # Draw arrows pointing inward
        points1 = [
            (x - arrow_size, y),  # Left
            (x - arrow_size*0.3, y - arrow_size*0.3),  # Top left arrow
            (x - arrow_size*0.3, y + arrow_size*0.3),  # Bottom left arrow
        ]
        
        points2 = [
            (x + arrow_size, y),  # Right
            (x + arrow_size*0.3, y - arrow_size*0.3),  # Top right arrow
            (x + arrow_size*0.3, y + arrow_size*0.3),  # Bottom right arrow
        ]
        
        pygame.draw.polygon(screen, (255, 255, 255), points1)
        pygame.draw.polygon(screen, (255, 255, 255), points2)
        
    def _draw_ghost(self, screen, x, y, radius):
        """Draw ghost icon for ghost power-up."""
        # Ghost body
        ghost_points = []
        for i in range(180):
            angle = math.radians(i)
            px = x + math.cos(angle) * radius * 0.6
            py = y - math.sin(angle) * radius * 0.6
            ghost_points.append((px, py))
            
        # Add bottom wavy edge
        wave_height = radius * 0.15
        for i in range(3):
            wave_x = x - radius*0.6 + i * radius*0.6
            ghost_points.append((wave_x, y + radius*0.6))
            ghost_points.append((wave_x + radius*0.3, y + radius*0.6 - wave_height))
            
        pygame.draw.polygon(screen, (200, 200, 255), ghost_points)
        
        # Draw eyes
        eye_radius = radius * 0.15
        eye_pos1 = (x - radius*0.25, y - radius*0.1)
        eye_pos2 = (x + radius*0.25, y - radius*0.1)
        
        pygame.draw.circle(screen, (0, 0, 0), eye_pos1, eye_radius)
        pygame.draw.circle(screen, (0, 0, 0), eye_pos2, eye_radius)


class Obstacle:
    def __init__(self, x, y, settings):
        self.position = (x, y)
        self.settings = settings
        self.color = (100, 100, 100)
        self.shadow_color = (70, 70, 70)
        self.highlight_color = (130, 130, 130)
        
    def draw(self, screen):
        # Convert grid position to pixel position
        cell_size = self.settings.CELL_SIZE
        x, y = self.position
        rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
        
        # Draw base rect
        pygame.draw.rect(screen, self.color, rect)
        
        # Draw 3D effect
        edge_size = max(2, cell_size // 8)
        
        # Top highlight
        pygame.draw.rect(screen, self.highlight_color, 
                        (rect.left, rect.top, rect.width, edge_size))
        pygame.draw.rect(screen, self.highlight_color, 
                        (rect.left, rect.top, edge_size, rect.height))
                        
        # Bottom shadow
        pygame.draw.rect(screen, self.shadow_color, 
                        (rect.left, rect.bottom - edge_size, rect.width, edge_size))
        pygame.draw.rect(screen, self.shadow_color, 
                        (rect.right - edge_size, rect.top, edge_size, rect.height))
                        
        # Crack details for variety
        crack_color = (50, 50, 50)
        
        # Add unique cracks based on position to ensure they're always the same for a given obstacle
        seed = hash(str(x) + str(y)) % 10000
        random.seed(seed)
        
        # Draw 2-3 random cracks
        for _ in range(random.randint(2, 3)):
            start_x = random.randint(rect.left + edge_size, rect.right - edge_size)
            start_y = random.randint(rect.top + edge_size, rect.bottom - edge_size)
            length = random.randint(cell_size // 4, cell_size // 2)
            angle = random.uniform(0, 2 * math.pi)
            
            end_x = start_x + int(math.cos(angle) * length)
            end_y = start_y + int(math.sin(angle) * length)
            
            # Ensure crack ends within obstacle
            end_x = max(rect.left + 1, min(rect.right - 1, end_x))
            end_y = max(rect.top + 1, min(rect.bottom - 1, end_y))
            
            # Draw the crack with a branch
            pygame.draw.line(screen, crack_color, (start_x, start_y), (end_x, end_y), 1)
            
            # Maybe add a branch to the crack
            if random.random() < 0.7:
                branch_angle = angle + random.uniform(-math.pi/4, math.pi/4)
                branch_length = length // 2
                branch_x = end_x + int(math.cos(branch_angle) * branch_length)
                branch_y = end_y + int(math.sin(branch_angle) * branch_length)
                
                # Ensure branch ends within obstacle
                branch_x = max(rect.left + 1, min(rect.right - 1, branch_x))
                branch_y = max(rect.top + 1, min(rect.bottom - 1, branch_y))
                
                pygame.draw.line(screen, crack_color, (end_x, end_y), (branch_x, branch_y), 1)
                
        # Reset random seed after use
        random.seed() 