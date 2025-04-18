import pygame
import math
import numpy as np
from src.particle import ParticleSystem
import random

class SnakeSegment:
    def __init__(self, x, y, radius, settings):
        self.x = x
        self.y = y
        self.radius = radius
        self.settings = settings
        # For smooth animation
        self.target_x = x
        self.target_y = y
        # For realistic snake movement
        self.angle = 0
        # Snake texture and shading
        self.base_color = (40, 120, 10)
        self.highlight_color = (80, 180, 30)
        self.shadow_color = (20, 60, 5)
        
    def update(self, dt):
        # Smooth movement towards target position
        lerp_factor = 0.6
        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor
        
    def set_target(self, x, y):
        # Set target position for smooth movement
        self.target_x = x
        self.target_y = y
        
    def get_position(self):
        return (self.x, self.y)
        
    def get_grid_position(self):
        # Return the integer grid position for collision detection
        return (int(round(self.x)), int(round(self.y)))
        
    def get_pixel_position(self):
        # Convert grid coordinates to pixel coordinates
        pixel_x = self.x * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        pixel_y = self.y * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        return (pixel_x, pixel_y)
        
    def draw(self, screen, is_head=False, direction=None, eye_direction=None):
        # Convert grid position to pixel position
        pixel_x = self.x * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        pixel_y = self.y * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        
        if is_head:
            self._draw_head(screen, pixel_x, pixel_y, direction, eye_direction)
        else:
            self._draw_body(screen, pixel_x, pixel_y)
    
    def _draw_head(self, screen, x, y, direction, eye_direction):
        # Draw realistic snake head with shading
        base_color = (50, 150, 20)
        highlight_color = (100, 200, 50)
        shadow_color = (30, 80, 10)
        
        # Draw base head circle
        pygame.draw.circle(screen, base_color, (int(x), int(y)), self.radius)
        
        # Draw highlight
        highlight_offset = -2
        if direction == "UP":
            highlight_pos = (int(x) + highlight_offset, int(y) - highlight_offset)
        elif direction == "DOWN":
            highlight_pos = (int(x) + highlight_offset, int(y) + highlight_offset)
        elif direction == "LEFT":
            highlight_pos = (int(x) - highlight_offset, int(y) + highlight_offset)
        else:  # RIGHT
            highlight_pos = (int(x) + highlight_offset, int(y) + highlight_offset)
            
        pygame.draw.circle(screen, highlight_color, highlight_pos, self.radius // 2)
        
        # Draw eyes
        eye_radius = self.radius // 4
        eye_offset_x = self.radius // 2
        eye_offset_y = self.radius // 3
        
        if direction == "UP":
            left_eye_pos = (int(x) - eye_offset_x, int(y) - eye_offset_y)
            right_eye_pos = (int(x) + eye_offset_x, int(y) - eye_offset_y)
        elif direction == "DOWN":
            left_eye_pos = (int(x) + eye_offset_x, int(y) + eye_offset_y)
            right_eye_pos = (int(x) - eye_offset_x, int(y) + eye_offset_y)
        elif direction == "LEFT":
            left_eye_pos = (int(x) - eye_offset_y, int(y) - eye_offset_x)
            right_eye_pos = (int(x) - eye_offset_y, int(y) + eye_offset_x)
        else:  # RIGHT
            left_eye_pos = (int(x) + eye_offset_y, int(y) + eye_offset_x)
            right_eye_pos = (int(x) + eye_offset_y, int(y) - eye_offset_x)
            
        # Draw white of eyes
        pygame.draw.circle(screen, (240, 240, 240), left_eye_pos, eye_radius)
        pygame.draw.circle(screen, (240, 240, 240), right_eye_pos, eye_radius)
        
        # Draw pupils
        pupil_radius = eye_radius // 2
        pupil_offset = pupil_radius // 2
        
        # Adjust pupil position based on eye_direction
        if eye_direction:
            if eye_direction == "UP":
                pupil_offset_x, pupil_offset_y = 0, -pupil_offset
            elif eye_direction == "DOWN":
                pupil_offset_x, pupil_offset_y = 0, pupil_offset
            elif eye_direction == "LEFT":
                pupil_offset_x, pupil_offset_y = -pupil_offset, 0
            else:  # RIGHT
                pupil_offset_x, pupil_offset_y = pupil_offset, 0
                
            left_pupil_pos = (left_eye_pos[0] + pupil_offset_x, left_eye_pos[1] + pupil_offset_y)
            right_pupil_pos = (right_eye_pos[0] + pupil_offset_x, right_eye_pos[1] + pupil_offset_y)
        else:
            left_pupil_pos = left_eye_pos
            right_pupil_pos = right_eye_pos
            
        pygame.draw.circle(screen, (20, 20, 20), left_pupil_pos, pupil_radius)
        pygame.draw.circle(screen, (20, 20, 20), right_pupil_pos, pupil_radius)
        
    def _draw_body(self, screen, x, y):
        # Draw snake body segment with realistic shading
        # Base circle
        pygame.draw.circle(screen, self.base_color, (int(x), int(y)), self.radius)
        
        # Highlight
        highlight_radius = self.radius * 0.6
        highlight_offset = self.radius * 0.3
        highlight_pos = (int(x - highlight_offset), int(y - highlight_offset))
        pygame.draw.circle(screen, self.highlight_color, highlight_pos, highlight_radius)
        
        # Pattern spots (optional)
        spot_radius = self.radius * 0.25
        spot_offset = self.radius * 0.5
        spot_pos = (int(x + spot_offset), int(y + spot_offset))
        pygame.draw.circle(screen, self.shadow_color, spot_pos, spot_radius)


class Snake:
    def __init__(self, settings):
        self.settings = settings
        self.segments = []
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.speed = settings.INITIAL_SNAKE_SPEED
        self.growth_pending = 0
        self.time_since_last_move = 0
        self.ate_food = False
        self.eye_direction = "RIGHT"
        
        # Visual effects
        self.pulse_effect = 0
        self.pulse_direction = 1
        self.particle_system = ParticleSystem(settings)
        self.trail_particles = []
        
        # Initialize snake
        self.reset()
        
    def reset(self):
        """Reset the snake to its initial state."""
        # Clear existing segments
        self.segments = []
        
        # Calculate starting position
        start_x = self.settings.GRID_WIDTH // 4
        start_y = self.settings.GRID_HEIGHT // 2
        
        # Create head segment
        head = SnakeSegment(start_x, start_y, self.settings.SNAKE_HEAD_RADIUS, self.settings)
        self.segments.append(head)
        
        # Create initial body segments
        for i in range(1, self.settings.INITIAL_SNAKE_LENGTH):
            segment = SnakeSegment(start_x - i, start_y, self.settings.SNAKE_BODY_RADIUS, self.settings)
            self.segments.append(segment)
            
        # Reset other properties
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.speed = self.settings.INITIAL_SNAKE_SPEED
        self.growth_pending = 0
        self.time_since_last_move = 0
        self.ate_food = False
        self.eye_direction = "RIGHT"
        self.trail_particles = []
        
    def draw(self, screen):
        """Draw the snake on the screen with enhanced visual effects."""
        # Draw trail particles first (behind snake)
        if self.settings.SNAKE_TRAIL_EFFECT:
            for particle in self.trail_particles:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = (*particle['color'], alpha)
                pygame.draw.circle(screen, color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
        
        # Draw each segment of the snake
        for i, segment in enumerate(self.segments):
            # Special effects for head
            if i == 0:
                # Get head position
                x, y = segment.get_pixel_position()
                
                # Pulse effect for the head
                pulse_amount = math.sin(self.pulse_effect * 3) * 2
                radius = self.settings.SNAKE_HEAD_RADIUS + pulse_amount
                
                # Draw glow effect for the head if enabled
                if self.settings.GLOW_EFFECTS_ENABLED:
                    glow_surface = pygame.Surface((radius*3, radius*3), pygame.SRCALPHA)
                    glow_radius = radius * 1.5
                    glow_color = (*self.settings.SNAKE_HEAD_COLOR, 80)  # Semi-transparent
                    pygame.draw.circle(glow_surface, glow_color, 
                                    (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surface, 
                               (x - glow_radius + radius, y - glow_radius + radius),
                               special_flags=pygame.BLEND_ALPHA_SDL2)
                
                # Draw head with outline
                pygame.draw.circle(screen, self.settings.SNAKE_OUTLINE_COLOR, (x, y), radius + 2)
                pygame.draw.circle(screen, self.settings.SNAKE_HEAD_COLOR, (x, y), radius)
                
                # Draw eyes
                if self.settings.SNAKE_EYES_ENABLED:
                    self._draw_eyes(screen, x, y, radius)
                    
            # Draw body segments with slight gradient effect
            else:
                # Position
                x, y = segment.get_pixel_position()
                
                # Color gradient based on position in body
                color_shift = max(0, 1 - (i / len(self.segments)) * 0.5)
                color = (
                    int(self.settings.SNAKE_BODY_COLOR[0] * color_shift),
                    int(self.settings.SNAKE_BODY_COLOR[1] * color_shift),
                    int(self.settings.SNAKE_BODY_COLOR[2] * color_shift)
                )
                
                # Draw body segment with outline
                pygame.draw.circle(screen, self.settings.SNAKE_OUTLINE_COLOR, 
                                (x, y), self.settings.SNAKE_BODY_RADIUS + 1)
                pygame.draw.circle(screen, color, 
                                (x, y), self.settings.SNAKE_BODY_RADIUS)
                
                # Add connector between segments
                if i > 0:
                    prev_x, prev_y = self.segments[i-1].get_pixel_position()
                    pygame.draw.line(screen, color, (prev_x, prev_y), (x, y), 
                                    self.settings.SNAKE_BODY_RADIUS*2-2)
        
        # Draw particle effects
        self.particle_system.draw(screen)
        
    def _draw_eyes(self, screen, x, y, radius):
        """Draw the snake's eyes based on direction."""
        # Eye positions based on direction
        eye_offset = radius * 0.5
        
        # Base eye positions
        if self.direction in ["UP", "DOWN"]:
            left_eye_pos = (x - eye_offset, y)
            right_eye_pos = (x + eye_offset, y)
        else:  # LEFT or RIGHT
            left_eye_pos = (x, y - eye_offset)
            right_eye_pos = (x, y + eye_offset)
            
        # Adjust eye positions based on looking direction
        if self.eye_direction == "UP":
            pupil_offset_x, pupil_offset_y = 0, -2
        elif self.eye_direction == "DOWN":
            pupil_offset_x, pupil_offset_y = 0, 2
        elif self.eye_direction == "LEFT":
            pupil_offset_x, pupil_offset_y = -2, 0
        else:  # RIGHT
            pupil_offset_x, pupil_offset_y = 2, 0
            
        # Draw eye whites
        eye_radius = radius * 0.3
        pygame.draw.circle(screen, (255, 255, 255), left_eye_pos, eye_radius)
        pygame.draw.circle(screen, (255, 255, 255), right_eye_pos, eye_radius)
        
        # Draw pupils with directional offset
        pupil_radius = eye_radius * 0.6
        pygame.draw.circle(screen, (0, 0, 0), 
                          (left_eye_pos[0] + pupil_offset_x, 
                           left_eye_pos[1] + pupil_offset_y), 
                          pupil_radius)
        pygame.draw.circle(screen, (0, 0, 0), 
                          (right_eye_pos[0] + pupil_offset_x, 
                           right_eye_pos[1] + pupil_offset_y), 
                          pupil_radius)
                
    def update(self, dt, food_positions=None):
        # Update eye direction if food is present
        if food_positions and len(food_positions) > 0:
            closest_food = min(food_positions, key=lambda food: self._distance_to_food(food))
            self._update_eye_direction(closest_food)
            
        # Update animation effects
        self.pulse_effect += 0.1 * self.pulse_direction
        if self.pulse_effect > 1.0:
            self.pulse_effect = 1.0
            self.pulse_direction = -1
        elif self.pulse_effect < 0.0:
            self.pulse_effect = 0.0
            self.pulse_direction = 1
            
        # Update particle effects
        self.particle_system.update()
        
        # Update trail particles
        if self.settings.SNAKE_TRAIL_EFFECT:
            # Update existing trail particles
            for particle in self.trail_particles[:]:
                particle['life'] -= dt * 0.01
                if particle['life'] <= 0:
                    self.trail_particles.remove(particle)
                    
            # Add new trail particles behind the snake
            if len(self.segments) > 0 and random.random() < 0.3:
                tail = self.segments[-1]
                x, y = tail.get_pixel_position()
                self.trail_particles.append({
                    'x': x + random.uniform(-3, 3),
                    'y': y + random.uniform(-3, 3),
                    'size': random.uniform(2, 5),
                    'color': self.settings.SNAKE_BODY_COLOR,
                    'life': 1.0,
                    'max_life': 1.0
                })
            
        # Update all segments
        for segment in self.segments:
            segment.update(dt)
            
        # Move snake based on speed
        self.time_since_last_move += dt
        move_interval = 1000 / self.speed  # Convert speed (moves per second) to milliseconds
        
        if self.time_since_last_move >= move_interval:
            self.time_since_last_move = 0
            self._move()
            
            # Add particles when snake moves
            if self.ate_food and random.random() < 0.8:
                head_x, head_y = self.segments[0].get_pixel_position()
                self.particle_system.create_particles(
                    head_x, head_y, 
                    int(5 * self.settings.PARTICLE_DENSITY)
                )
                self.ate_food = False
            
    def _distance_to_food(self, food):
        head_x, head_y = self.get_head_position()
        food_x, food_y = food.position
        return math.sqrt((head_x - food_x) ** 2 + (head_y - food_y) ** 2)
        
    def _update_eye_direction(self, food):
        head_x, head_y = self.get_head_position()
        food_x, food_y = food.position
        
        dx = food_x - head_x
        dy = food_y - head_y
        
        # Determine predominant direction to food
        if abs(dx) > abs(dy):
            self.eye_direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            self.eye_direction = "DOWN" if dy > 0 else "UP"
            
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        opposites = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }
        
        # Only change direction if it's not opposite to current direction
        if new_direction != opposites[self.direction]:
            self.next_direction = new_direction
            
    def grow(self, amount=1):
        self.growth_pending += amount
        self.ate_food = True
        
    def increase_speed(self, amount):
        self.speed = min(self.settings.MAX_SNAKE_SPEED, self.speed + amount)
        
    def _move(self):
        # Update direction
        self.direction = self.next_direction
        
        # Get head position
        head_x, head_y = self.segments[0].get_position()
        
        # Calculate new head position based on direction
        if self.direction == "UP":
            new_head_y = head_y - 1
            new_head_x = head_x
        elif self.direction == "DOWN":
            new_head_y = head_y + 1
            new_head_x = head_x
        elif self.direction == "LEFT":
            new_head_x = head_x - 1
            new_head_y = head_y
        elif self.direction == "RIGHT":
            new_head_x = head_x + 1
            new_head_y = head_y
            
        # If growth pending, add new segment
        if self.growth_pending > 0:
            # Create a new head with the same position as the current head
            new_head = SnakeSegment(head_x, head_y, self.settings.SNAKE_HEAD_RADIUS, self.settings)
            # Set the new target position
            new_head.set_target(new_head_x, new_head_y)
            
            # Make old head a body segment
            self.segments[0].radius = self.settings.SNAKE_BODY_RADIUS
            
            # Add new head to the beginning of the list
            self.segments.insert(0, new_head)
            
            # Decrease growth counter
            self.growth_pending -= 1
            
            # Create particle effect at head position when growing
            if self.ate_food:
                pixel_x = head_x * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
                pixel_y = head_y * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
                self.particle_system.create_particles(pixel_x, pixel_y, self.settings.PARTICLE_COUNT)
                self.ate_food = False
        else:
            # Move segments from tail to head
            for i in range(len(self.segments) - 1, 0, -1):
                prev_x, prev_y = self.segments[i-1].get_position()
                self.segments[i].set_target(prev_x, prev_y)
                
            # Move head to new position
            self.segments[0].set_target(new_head_x, new_head_y)
            
        # Handle screen wrapping immediately for smoother animation when crossing borders
        if not self.settings.GAME_MODES.get(self.direction, {}).get('walls', False):
            # Check if head is outside grid and wrap around
            head = self.segments[0]
            if head.target_x < 0:
                head.set_target(self.settings.GRID_WIDTH - 1, head.target_y)
            elif head.target_x >= self.settings.GRID_WIDTH:
                head.set_target(0, head.target_y)
                
            if head.target_y < 0:
                head.set_target(head.target_x, self.settings.GRID_HEIGHT - 1)
            elif head.target_y >= self.settings.GRID_HEIGHT:
                head.set_target(head.target_x, 0)

    def check_collision_with_self(self):
        # Don't check collision with self if snake is too short
        if len(self.segments) <= 3:
            return False
        
        head_x, head_y = self.get_head_position()
        head_grid_pos = self.get_head_grid_position()
        
        # Check if head collides with any body segment (skip first few segments to prevent false collisions)
        for segment in self.segments[3:]:  # Skip first 3 segments (head + 2 neck segments)
            segment_grid_pos = segment.get_grid_position()
            # Use grid positions for more accurate collision detection
            if head_grid_pos == segment_grid_pos:
                return True
            
        return False
        
    def check_collision_with_walls(self, walls=True):
        head_x, head_y = self.get_head_position()
        
        if walls:
            # Check if head is outside the grid
            if (head_x < 0 or head_x >= self.settings.GRID_WIDTH or
                head_y < 0 or head_y >= self.settings.GRID_HEIGHT):
                return True
        else:
            # Wrap around the screen
            if head_x < 0:
                self.segments[0].target_x = self.settings.GRID_WIDTH - 1
            elif head_x >= self.settings.GRID_WIDTH:
                self.segments[0].target_x = 0
                
            if head_y < 0:
                self.segments[0].target_y = self.settings.GRID_HEIGHT - 1
            elif head_y >= self.settings.GRID_HEIGHT:
                self.segments[0].target_y = 0
                
        return False
        
    def check_collision_with_obstacles(self, obstacles):
        head_x, head_y = self.get_head_position()
        head_grid_pos = (int(round(head_x)), int(round(head_y)))
        
        for obstacle in obstacles:
            if obstacle.position == head_grid_pos:
                return True
                
        return False
        
    def get_head_position(self):
        return self.segments[0].get_position()
        
    def get_head_grid_position(self):
        return self.segments[0].get_grid_position()
        
    def get_segments_positions(self):
        return [segment.get_grid_position() for segment in self.segments]