import pygame
import random
import os
import math
from src.snake import Snake
from src.food import Food, Obstacle
from src.particle import ParticleSystem

class Game:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.game_over = False
        self.paused = False
        self.score = 0
        self.high_score = 0
        self.current_mode = "classic"
        self.mode_data = settings.GAME_MODES[self.current_mode]
        
        # Initialize game objects
        self.snake = Snake(settings)
        self.foods = []
        self.obstacles = []
        self.particle_system = ParticleSystem(settings)
        
        # Load sounds
        self.sounds = self._load_sounds()
        
        # Power-up effects
        self.active_powerups = {
            "speed": {"active": False, "end_time": 0},
            "slow": {"active": False, "end_time": 0},
            "shrink": {"active": False, "end_time": 0},
            "ghost": {"active": False, "end_time": 0}
        }
        
        # Touch controls
        self.touch_enabled = True
        self._init_touch_controls()
        
        # Initialize game state
        self.reset()
        
    def _load_sounds(self):
        sounds = {}
        sounds_dir = os.path.join('assets', 'sounds')
        
        # Check if sounds directory exists
        if not os.path.exists(sounds_dir):
            print(f"Sounds directory not found: {sounds_dir}")
            return sounds
        
        # Define sound files to load
        sound_files = {
            'eat': os.path.join(sounds_dir, 'eat.wav'),
            'game_over': os.path.join(sounds_dir, 'game_over.wav'), 
            'powerup': os.path.join(sounds_dir, 'powerup.wav')
        }
        
        # Try to load each sound
        for sound_name, sound_path in sound_files.items():
            try:
                if os.path.exists(sound_path):
                    sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    sounds[sound_name].set_volume(self.settings.SFX_VOLUME)
                else:
                    print(f"Sound file not found: {sound_path}")
            except Exception as e:
                print(f"Error loading sound {sound_name}: {e}")
            
        return sounds
        
    def reset(self):
        # Reset game state
        self.game_over = False
        self.paused = False
        self.score = 0
        self.time_remaining = self.mode_data.get('time_limit', None)
        self.start_time = pygame.time.get_ticks()
        self.last_speed_increase_time = self.start_time
        
        # Reset snake
        self.snake.reset()
        
        # Clear food and obstacles
        self.foods.clear()
        self.obstacles.clear()
        
        # Create initial food
        self.spawn_food()
        
        # Create obstacles for obstacle mode
        if self.mode_data.get('obstacles', False):
            self._create_obstacles()
            
        # Create walls for walled modes
        if self.mode_data.get('walls', False):
            self._create_walls()
            
        # Reset power-ups
        for powerup in self.active_powerups.values():
            powerup['active'] = False
            powerup['end_time'] = 0
            
    def set_mode(self, mode):
        """Change the game mode."""
        if mode in self.settings.GAME_MODES:
            self.current_mode = mode
            self.mode_data = self.settings.GAME_MODES[mode]
            self.reset()
            
    def _create_obstacles(self):
        """Create obstacles for the obstacle mode."""
        num_obstacles = self.mode_data.get('num_obstacles', 10)
        
        # Get snake positions to avoid placing obstacles on the snake
        snake_positions = self.snake.get_segments_positions()
        
        # Create specified number of obstacles in valid positions
        for _ in range(num_obstacles):
            valid_position = False
            attempts = 0
            max_attempts = 100
            
            while not valid_position and attempts < max_attempts:
                # Generate random position (avoid edges)
                x = random.randint(2, self.settings.GRID_WIDTH - 3)
                y = random.randint(2, self.settings.GRID_HEIGHT - 3)
                
                # Check if position is valid (not on snake or other obstacles)
                if (x, y) not in snake_positions and not any(o.position == (x, y) for o in self.obstacles):
                    valid_position = True
                    
                attempts += 1
                
            if valid_position:
                self.obstacles.append(Obstacle(x, y, self.settings))
                
    def _create_walls(self):
        """Create walls around the edge of the screen."""
        # Create walls along the borders
        for x in range(self.settings.GRID_WIDTH):
            # Top wall
            self.obstacles.append(Obstacle(x, 0, self.settings))
            # Bottom wall
            self.obstacles.append(Obstacle(x, self.settings.GRID_HEIGHT - 1, self.settings))
            
        for y in range(1, self.settings.GRID_HEIGHT - 1):
            # Left wall
            self.obstacles.append(Obstacle(0, y, self.settings))
            # Right wall
            self.obstacles.append(Obstacle(self.settings.GRID_WIDTH - 1, y, self.settings))
            
    def spawn_food(self):
        """Spawn food at a random position."""
        # Get current snake positions
        snake_positions = self.snake.get_segments_positions()
        
        # Add obstacle positions as well
        obstacle_positions = [o.position for o in self.obstacles]
        all_occupied = snake_positions + obstacle_positions
        
        # Add existing food positions to avoid food overlap
        food_positions = [f.position for f in self.foods]
        all_occupied.extend(food_positions)
        
        # Determine what type of food to spawn
        food_type = "apple"  # Default food type
        
        # Always make sure there's at least one apple
        if not any(f.food_type == "apple" for f in self.foods):
            food_type = "apple"
        # Otherwise, apply spawn chances for special foods
        elif random.random() < self.settings.BONUS_FOOD_SPAWN_CHANCE:
            food_type = "bonus"
        elif random.random() < self.settings.POWERUP_SPAWN_CHANCE:
            food_type = "power"
        
        # Create and add the food
        food = Food(self.settings, food_type)
        food.respawn(all_occupied)
        self.foods.append(food)
        
        # Add extra particles when food spawns
        x = food.position[0] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        y = food.position[1] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        self.particle_system.create_particles(x, y, 10, food.color)
        
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Get elapsed time since last frame
        dt = pygame.time.get_ticks() - (self.last_frame_time if hasattr(self, 'last_frame_time') else pygame.time.get_ticks())
        self.last_frame_time = pygame.time.get_ticks()
        
        # Update time remaining for timed modes
        if self.time_remaining is not None:
            self.time_remaining = max(0, self.time_remaining - dt)
            if self.time_remaining <= 0:
                self.game_over = True
                
        # Update power-up timers and check for expiration
        current_time = pygame.time.get_ticks()
        for powerup_type, powerup_data in self.active_powerups.items():
            if powerup_data['active'] and current_time >= powerup_data['end_time']:
                powerup_data['active'] = False
                
                # Revert effects when power-up expires
                if powerup_type == "speed":
                    self.snake.speed = max(self.settings.INITIAL_SNAKE_SPEED, self.snake.speed - 5)
                elif powerup_type == "slow":
                    self.snake.speed = min(self.settings.MAX_SNAKE_SPEED, self.snake.speed + 3)
                    
        # Check if we should increase speed (for survival mode)
        if self.mode_data.get('time_speed_increase', 0) > 0:
            time_since_last_increase = current_time - self.last_speed_increase_time
            if time_since_last_increase > 10000:  # 10 seconds
                self.snake.increase_speed(self.mode_data['time_speed_increase'])
                self.last_speed_increase_time = current_time
                
        # Update snake with food positions for eye tracking
        self.snake.update(dt, self.foods)
        
        # Check for collisions - do this AFTER the snake has been updated
        self._check_collisions()
        
        # Update foods and check for expired foods
        self.foods = [food for food in self.foods if food.update()]
        
        # Ensure there's always at least one food item
        if not self.foods or not any(f.food_type == "apple" for f in self.foods):
            self.spawn_food()
        
        # Update particle system
        self.particle_system.update()
        
    def _check_collisions(self):
        # Get head position for collision checking
        head_x, head_y = self.snake.get_head_position()
        head_grid_pos = self.snake.get_head_grid_position()
        
        # Add a small tolerance for food collision (to make eating easier)
        head_pos_tolerance = 0.5
        
        # First, check food collisions
        food_eaten = None
        
        for food in self.foods:
            food_x, food_y = food.position
            
            # Use both grid position and distance check for more reliable food detection
            is_grid_match = head_grid_pos == food.position
            distance = math.sqrt((head_x - food_x)**2 + (head_y - food_y)**2)
            
            # If either the grid positions match or we're really close to the food
            if is_grid_match or distance < head_pos_tolerance:
                food_eaten = food
                break
        
        # If food was found to be eaten
        if food_eaten:
            self._handle_food_eaten(food_eaten)
            self.foods.remove(food_eaten)
            
            # Spawn new food if there are no apples left
            if not any(f.food_type == "apple" for f in self.foods):
                self.spawn_food()
            return  # Skip other collision checks when food is eaten
        
        # Only check for fatal collisions if no food was eaten
        # Check if snake collides with itself
        if self.snake.check_collision_with_self():
            if not self.active_powerups["ghost"]["active"]:
                self._handle_game_over()
            return
            
        # Check if snake collides with walls
        if self.snake.check_collision_with_walls(self.mode_data.get('walls', False)):
            if not self.active_powerups["ghost"]["active"]:
                self._handle_game_over()
            return
        
        # Check if snake collides with obstacles
        for obstacle in self.obstacles:
            if head_grid_pos == obstacle.position:
                if not self.active_powerups["ghost"]["active"]:
                    self._handle_game_over()
                return
        
    def _handle_food_eaten(self, food):
        # Increase score
        self.score += food.points
        self.high_score = max(self.score, self.high_score)
        
        # Grow snake
        growth_amount = food.points
        self.snake.grow(growth_amount)
        
        # Increase snake speed based on mode and food type
        if food.food_type == "apple" and self.mode_data.get('speed_increase', 0) > 0:
            self.snake.increase_speed(self.mode_data['speed_increase'])
        elif food.food_type == "bonus":
            # Bonus food gives a small speed boost in all modes
            self.snake.increase_speed(0.2)
        
        # Apply power-up effects
        if food.food_type == "power":
            self._apply_powerup(food.powerup_type)
            
        # Play sound
        if 'eat' in self.sounds and self.settings.SOUND_ENABLED:
            self.sounds['eat'].play()
            
        # Create extra particle effect for more visual feedback
        x = food.position[0] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        y = food.position[1] * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        particles_to_create = self.settings.PARTICLE_COUNT * 2
        if food.food_type == "bonus":
            particles_to_create *= 2  # More particles for bonus food
        self.particle_system.create_particles(x, y, particles_to_create, food.color)
        
        # Chance to spawn a new food item immediately (to have more food on screen)
        if random.random() < 0.3:  # 30% chance
            self.spawn_food()
        
    def _apply_powerup(self, powerup_type):
        current_time = pygame.time.get_ticks()
        duration = self.settings.POWERUP_DURATION
        
        # Mark power-up as active and set end time
        self.active_powerups[powerup_type]["active"] = True
        self.active_powerups[powerup_type]["end_time"] = current_time + duration
        
        # Apply power-up effect
        if powerup_type == "speed":
            # Speed boost
            self.snake.increase_speed(5)
        elif powerup_type == "slow":
            # Slow down
            self.snake.speed = max(self.settings.INITIAL_SNAKE_SPEED // 2, self.snake.speed - 3)
        elif powerup_type == "shrink":
            # Shrink snake to minimum size
            excess_segments = len(self.snake.segments) - self.settings.INITIAL_SNAKE_LENGTH
            if excess_segments > 0:
                self.snake.segments = self.snake.segments[:-excess_segments]
        # Ghost mode is handled in collision detection
        
        # Play powerup sound
        if 'powerup' in self.sounds and self.settings.SOUND_ENABLED:
            self.sounds['powerup'].play()
            
    def _handle_game_over(self):
        self.game_over = True
        
        # Play game over sound
        if 'game_over' in self.sounds and self.settings.SOUND_ENABLED:
            self.sounds['game_over'].play()
            
        # Large particle explosion at head position
        head_x, head_y = self.snake.get_head_position()
        pixel_x = head_x * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        pixel_y = head_y * self.settings.CELL_SIZE + self.settings.CELL_SIZE // 2
        self.particle_system.create_particles(pixel_x, pixel_y, self.settings.PARTICLE_COUNT * 5)
        
    def render(self):
        # Draw background grid
        self._draw_background_grid()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Draw food items
        for food in self.foods:
            food.draw(self.screen)
            
        # Draw snake
        self.snake.draw(self.screen)
        
        # Draw particle effects
        self.particle_system.draw(self.screen)
        
        # Draw score and other UI elements
        self._draw_ui()
        
        # Draw touch controls if enabled
        if self.touch_enabled:
            self._draw_touch_controls()
        
        # Draw pause screen if paused
        if self.paused:
            self._draw_pause_screen()
            
        # Draw game over screen if game is over
        if self.game_over:
            self._draw_game_over_screen()
        
    def _draw_background_grid(self):
        # Draw subtle grid pattern for background
        for x in range(0, self.settings.WIDTH, self.settings.CELL_SIZE):
            pygame.draw.line(self.screen, self.settings.GRID_COLOR, 
                            (x, 0), (x, self.settings.HEIGHT), 1)
                            
        for y in range(0, self.settings.HEIGHT, self.settings.CELL_SIZE):
            pygame.draw.line(self.screen, self.settings.GRID_COLOR, 
                            (0, y), (self.settings.WIDTH, y), 1)
            
    def _draw_ui(self):
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, self.settings.TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        
        # Draw high score
        high_score_text = font.render(f"High Score: {self.high_score}", True, self.settings.TEXT_COLOR)
        high_score_rect = high_score_text.get_rect(topright=(self.settings.WIDTH - 20, 20))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Draw game mode
        mode_text = font.render(f"Mode: {self.mode_data['name']}", True, self.settings.TEXT_COLOR)
        mode_rect = mode_text.get_rect(midtop=(self.settings.WIDTH // 2, 20))
        self.screen.blit(mode_text, mode_rect)
        
        # Draw time remaining for timed modes
        if self.time_remaining is not None:
            seconds = self.time_remaining // 1000
            time_text = font.render(f"Time: {seconds}s", True, self.settings.TEXT_COLOR)
            time_rect = time_text.get_rect(midtop=(self.settings.WIDTH // 2, 60))
            self.screen.blit(time_text, time_rect)
            
        # Draw active power-ups
        powerup_y = 70
        small_font = pygame.font.Font(None, 24)
        for powerup_type, powerup_data in self.active_powerups.items():
            if powerup_data['active']:
                # Calculate remaining time
                remaining = (powerup_data['end_time'] - pygame.time.get_ticks()) // 1000
                powerup_text = small_font.render(f"{powerup_type.capitalize()}: {remaining}s", 
                                              True, self.settings.TEXT_COLOR)
                self.screen.blit(powerup_text, (20, powerup_y))
                powerup_y += 30
                
    def _draw_pause_screen(self):
        # Translucent overlay
        overlay = pygame.Surface((self.settings.WIDTH, self.settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, self.settings.TEXT_COLOR)
        pause_rect = pause_text.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        font = pygame.font.Font(None, 36)
        instr_text = font.render("Press P to resume or ESC to quit", True, self.settings.TEXT_COLOR)
        instr_rect = instr_text.get_rect(midtop=(self.settings.WIDTH // 2, pause_rect.bottom + 20))
        self.screen.blit(instr_text, instr_rect)
        
    def _draw_game_over_screen(self):
        """Draw the game over screen with visual effects."""
        # Translucent overlay with pulsing effect
        overlay = pygame.Surface((self.settings.WIDTH, self.settings.HEIGHT), pygame.SRCALPHA)
        
        # Create a pulsing red tint effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2  # Value between 0-1
        overlay_color = (180, 30, 30, 150 + int(pulse * 50))  # Pulsing red with transparency
        overlay.fill(overlay_color)  
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text with shadow effect
        large_font = pygame.font.Font(None, 120)
        
        # Draw drop shadow
        game_over_shadow = large_font.render("GAME OVER", True, (0, 0, 0))
        shadow_rect = game_over_shadow.get_rect(center=(self.settings.WIDTH // 2 + 4, self.settings.HEIGHT // 2 - 50 + 4))
        self.screen.blit(game_over_shadow, shadow_rect)
        
        # Main text with slight pulsing color
        pulse_color = (255, 200 + int(pulse * 55), 200 + int(pulse * 55))
        game_over_text = large_font.render("GAME OVER", True, pulse_color)
        game_over_rect = game_over_text.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score display
        medium_font = pygame.font.Font(None, 60)
        final_score_text = medium_font.render(f"Score: {self.score}", True, self.settings.TEXT_COLOR)
        final_score_rect = final_score_text.get_rect(midtop=(self.settings.WIDTH // 2, game_over_rect.bottom + 30))
        self.screen.blit(final_score_text, final_score_rect)
        
        # High score display with highlight if player beat the high score
        if self.score >= self.high_score:
            high_score_text = medium_font.render(f"NEW HIGH SCORE!", True, (255, 215, 0))  # Gold color
            high_score_rect = high_score_text.get_rect(midtop=(self.settings.WIDTH // 2, final_score_rect.bottom + 20))
            
            # Draw glow effect behind high score text
            glow_surf = pygame.Surface((high_score_rect.width + 20, high_score_rect.height + 20), pygame.SRCALPHA)
            glow_color = (255, 215, 0, 100 + int(pulse * 100))  # Pulsing gold glow
            pygame.draw.rect(glow_surf, glow_color, (0, 0, high_score_rect.width + 20, high_score_rect.height + 20), 
                           border_radius=10)
            self.screen.blit(glow_surf, (high_score_rect.x - 10, high_score_rect.y - 10))
            
            self.screen.blit(high_score_text, high_score_rect)
            instruction_y_offset = high_score_rect.bottom + 30
        else:
            high_score_text = medium_font.render(f"High Score: {self.high_score}", True, self.settings.TEXT_COLOR)
            high_score_rect = high_score_text.get_rect(midtop=(self.settings.WIDTH // 2, final_score_rect.bottom + 20))
            self.screen.blit(high_score_text, high_score_rect)
            instruction_y_offset = high_score_rect.bottom + 30
        
        # Instructions
        font = pygame.font.Font(None, 36)
        
        # Create a subtle pulsing effect for the instruction text
        instruction_alpha = 200 + int(pulse * 55)
        instruction_color = (*self.settings.TEXT_COLOR[:3], instruction_alpha)
        
        instruction_text = font.render("Press SPACE to restart or ESC to quit", True, instruction_color)
        instruction_rect = instruction_text.get_rect(midtop=(self.settings.WIDTH // 2, instruction_y_offset))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Add restart button for touch screens
        if self.settings.HAS_TOUCHSCREEN:
            btn_size = 180
            restart_btn_rect = pygame.Rect(
                self.settings.WIDTH // 2 - btn_size // 2,
                instruction_rect.bottom + 40,
                btn_size, btn_size // 2
            )
            
            # Store the button rectangle for touch detection
            self.restart_button = restart_btn_rect
            
            # Draw button with pulsing effect
            button_color = (100, 200, 100)
            glow_factor = 0.7 + pulse * 0.3
            glow_color = (
                min(255, int(button_color[0] * glow_factor)),
                min(255, int(button_color[1] * glow_factor)), 
                min(255, int(button_color[2] * glow_factor))
            )
            
            # Draw button with rounded corners and glow effect
            pygame.draw.rect(self.screen, (*glow_color, 200), restart_btn_rect, border_radius=15)
            pygame.draw.rect(self.screen, (*button_color, 230), restart_btn_rect, border_radius=15, width=3)
            
            # Button text
            btn_font = pygame.font.Font(None, 40)
            btn_text = btn_font.render("RESTART", True, (255, 255, 255))
            btn_text_rect = btn_text.get_rect(center=restart_btn_rect.center)
            self.screen.blit(btn_text, btn_text_rect)

    def _draw_touch_controls(self):
        """Draw the touch control buttons with enhanced visual style."""
        for direction, rect in self.touch_buttons.items():
            # Determine color based on touch state
            if direction == self.btn_touched:
                color = self.btn_active_color
                glow_factor = 1.3  # Make active buttons brighter
            else:
                color = self.btn_color
                glow_factor = 1.0
                
            # Create glowing effect for buttons
            glow_color = (
                min(255, int(color[0] * glow_factor)),
                min(255, int(color[1] * glow_factor)), 
                min(255, int(color[2] * glow_factor))
            )
            
            # Draw the button background with semi-transparency
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            
            # Draw outer glow for visibility
            outer_rect = rect.inflate(12, 12)
            pygame.draw.rect(self.screen, (*glow_color, 80), 
                            (outer_rect.x - 6, outer_rect.y - 6, outer_rect.width, outer_rect.height), 
                            border_radius=15)
            
            # Draw main button with semi-transparency
            pygame.draw.rect(button_surface, (*color, self.settings.TOUCH_BUTTON_OPACITY), 
                             (0, 0, rect.width, rect.height), border_radius=12)
                             
            # Add a gradient/highlight effect at the top
            highlight_height = rect.height // 3
            highlight_surface = pygame.Surface((rect.width, highlight_height), pygame.SRCALPHA)
            highlight_color = (255, 255, 255, 40)  # White with low opacity
            pygame.draw.rect(highlight_surface, highlight_color, 
                            (0, 0, rect.width, highlight_height), 
                            border_radius=10)
            button_surface.blit(highlight_surface, (0, 0))
            
            # Draw direction arrows or pause icon with enhanced look
            if direction in self.btn_icons:
                # Adjust points to button position
                adjusted_points = [(p[0] + rect.x, p[1] + rect.y) for p in self.btn_icons[direction]]
                
                # Draw arrow outline for better visibility
                if direction == self.btn_touched:
                    # Draw larger glow outline for active button
                    pygame.draw.polygon(self.screen, (*self.settings.TEXT_COLOR, 100), 
                                      [(p[0]+2, p[1]+2) for p in adjusted_points], width=4)
                
                # Draw the actual arrow
                pygame.draw.polygon(self.screen, self.settings.TEXT_COLOR, adjusted_points)
                
            elif direction == "PAUSE":
                # Enhanced pause icon (two vertical bars)
                bar_width = rect.width // 5
                gap = rect.width // 4
                
                # Draw pause button with fancier style
                for offset in [-1, 1]:
                    pygame.draw.rect(self.screen, self.settings.TEXT_COLOR, 
                                    (rect.x + rect.width//2 - gap//2 - bar_width + (offset * gap//2), 
                                     rect.y + rect.height//4, 
                                     bar_width, rect.height//2),
                                    border_radius=bar_width//3)
            
            # Apply the button to the screen
            self.screen.blit(button_surface, rect)
            
            # Add a label for each button
            if self.settings.SHOW_BUTTON_LABELS:
                small_font = pygame.font.Font(None, 18)
                if direction == "PAUSE":
                    label = small_font.render("PAUSE", True, self.settings.TEXT_COLOR)
                    label_pos = (rect.centerx - label.get_width()//2, rect.bottom + 5)
                    self.screen.blit(label, label_pos)

    def _init_touch_controls(self):
        """Initialize touch control buttons."""
        btn_size = self.settings.TOUCH_BUTTON_SIZE
        btn_margin = self.settings.TOUCH_BUTTON_SPACING
        
        # Calculate positions for the directional buttons (bottom of the screen)
        bottom_y = self.settings.HEIGHT - btn_size - btn_margin
        center_x = self.settings.WIDTH // 2
        
        # Create directional buttons - ensure there's enough space between them
        self.touch_buttons = {
            "UP": pygame.Rect(center_x - btn_size // 2, 
                              bottom_y - btn_size - btn_margin*2, 
                              btn_size, btn_size),
                              
            "DOWN": pygame.Rect(center_x - btn_size // 2, 
                                bottom_y, 
                                btn_size, btn_size),
                                
            "LEFT": pygame.Rect(center_x - btn_size*1.5 - btn_margin, 
                                bottom_y - btn_size//2, 
                                btn_size, btn_size),
                                
            "RIGHT": pygame.Rect(center_x + btn_size//2 + btn_margin, 
                                 bottom_y - btn_size//2, 
                                 btn_size, btn_size),
                                 
            "PAUSE": pygame.Rect(self.settings.WIDTH - btn_size - btn_margin, 
                                 btn_margin, 
                                 btn_size//1.5, btn_size//1.5)
        }
        
        # Button colors
        self.btn_color = self.settings.BUTTON_COLOR
        self.btn_hover_color = self.settings.BUTTON_HOVER_COLOR
        self.btn_active_color = self.settings.BUTTON_ACTIVE_COLOR
        self.btn_touched = None
        
        # Button icons (arrows) - scale with button size
        arrow_size = btn_size // 2
        self.btn_icons = {
            "UP": [
                (btn_size//2, btn_size//4),  # Top point
                (btn_size//4, btn_size*3//4),  # Bottom-left point
                (btn_size*3//4, btn_size*3//4)  # Bottom-right point
            ],
            "DOWN": [
                (btn_size//2, btn_size*3//4),  # Bottom point
                (btn_size//4, btn_size//4),  # Top-left point 
                (btn_size*3//4, btn_size//4)  # Top-right point
            ],
            "LEFT": [
                (btn_size//4, btn_size//2),  # Left point
                (btn_size*3//4, btn_size//4),  # Top-right point
                (btn_size*3//4, btn_size*3//4)  # Bottom-right point
            ],
            "RIGHT": [
                (btn_size*3//4, btn_size//2),  # Right point
                (btn_size//4, btn_size//4),  # Top-left point
                (btn_size//4, btn_size*3//4)  # Bottom-left point
            ]
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Handle key presses
            if not self.game_over:
                # Game controls
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.snake.change_direction("UP")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.snake.change_direction("DOWN")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.snake.change_direction("LEFT")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.snake.change_direction("RIGHT")
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    # Play a sound when pausing/unpausing
                    if 'powerup' in self.sounds and self.settings.SOUND_ENABLED:
                        self.sounds['powerup'].play()
                elif event.key == pygame.K_m:
                    self.settings.SOUND_ENABLED = not self.settings.SOUND_ENABLED
                elif event.key == pygame.K_ESCAPE:
                    return 0  # Return to menu
            else:
                # Game over controls
                if event.key == pygame.K_SPACE:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return 0  # Return to menu
                    
        # Handle touch events
        elif self.touch_enabled:
            # Determine touch/click position
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                self._handle_touch(pos)
            elif event.type == pygame.FINGERDOWN:
                # Convert normalized finger position to screen coordinates
                # Finger positions are normalized (0-1), multiply by screen dimensions
                pos = (int(event.x * self.settings.WIDTH), 
                       int(event.y * self.settings.HEIGHT))
                self._handle_touch(pos)
                # Flag that touch is being used
                self.settings.HAS_TOUCHSCREEN = True
            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                self.btn_touched = None

        return None
        
    def _handle_touch(self, pos):
        """Handle touch/click at the given position."""
        # Only check touch controls if not game over
        if self.game_over:
            # Check if restart button was touched
            if hasattr(self, 'restart_button') and self.restart_button.collidepoint(pos):
                self.reset()
            return
            
        # Check for touch controls
        for direction, rect in self.touch_buttons.items():
            if rect.collidepoint(pos):
                if direction == "PAUSE":
                    self.paused = not self.paused
                    # Play a sound when pausing/unpausing
                    if 'powerup' in self.sounds and self.settings.SOUND_ENABLED:
                        self.sounds['powerup'].play()
                else:
                    self.snake.change_direction(direction)
                self.btn_touched = direction
                break

    def _draw_touch_controls(self):
        """Draw the touch control buttons."""
        for direction, rect in self.touch_buttons.items():
            # Determine color based on touch state
            if direction == self.btn_touched:
                color = self.btn_active_color
            else:
                color = self.btn_color
            
            # Draw the button background with semi-transparency
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, (*color, self.settings.TOUCH_BUTTON_OPACITY), 
                             (0, 0, rect.width, rect.height), border_radius=10)
            
            # Draw direction arrows or pause icon
            if direction in self.btn_icons:
                # Adjust points to button position
                adjusted_points = [(p[0] + rect.x, p[1] + rect.y) for p in self.btn_icons[direction]]
                pygame.draw.polygon(self.screen, self.settings.TEXT_COLOR, adjusted_points)
            elif direction == "PAUSE":
                # Draw pause symbol (two vertical bars)
                bar_width = rect.width // 5
                gap = rect.width // 5
                pygame.draw.rect(self.screen, self.settings.TEXT_COLOR, 
                                 (rect.x + rect.width//2 - gap//2 - bar_width, rect.y + rect.height//4, 
                                  bar_width, rect.height//2))
                pygame.draw.rect(self.screen, self.settings.TEXT_COLOR, 
                                 (rect.x + rect.width//2 + gap//2, rect.y + rect.height//4, 
                                  bar_width, rect.height//2))
            
            # Apply the button to the screen
            self.screen.blit(button_surface, rect) 