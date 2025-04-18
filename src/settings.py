import pygame

class Settings:
    def __init__(self):
        # Window settings
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.FPS = 60
        
        # Touch settings
        self.HAS_TOUCHSCREEN = True  # Default to true for better compatibility
        self.TOUCH_BUTTON_OPACITY = 180  # 0-255, controls transparency of touch buttons
        self.TOUCH_BUTTON_SIZE = 120  # Increased size for better touch targets
        self.TOUCH_BUTTON_SPACING = 20
        self.TOUCH_FEEDBACK_ENABLED = True
        self.SHOW_BUTTON_LABELS = True  # Whether to show text labels on buttons
        
        # Colors - Enhanced with brighter, more visible colors
        self.BG_COLOR = (15, 40, 30)
        self.GRID_COLOR = (25, 60, 50)
        self.TEXT_COLOR = (230, 230, 230)
        self.MENU_BG_COLOR = (10, 30, 25)
        self.BUTTON_COLOR = (60, 140, 120)
        self.BUTTON_HOVER_COLOR = (80, 180, 150)
        self.BUTTON_ACTIVE_COLOR = (100, 200, 170)
        
        # Enhanced food colors for better visibility
        self.FOOD_COLORS = {
            'apple': (255, 70, 70),      # Brighter red
            'bonus': (255, 230, 50),     # Bright gold/yellow
            'power': (100, 200, 255)     # Brighter blue
        }
        
        # Enhanced snake colors
        self.SNAKE_HEAD_COLOR = (120, 255, 120)  # Brighter green
        self.SNAKE_BODY_COLOR = (80, 220, 80)    # Slightly darker green
        self.SNAKE_OUTLINE_COLOR = (10, 40, 10)  # Dark green outline for better visibility
        
        # Animation settings
        self.ANIMATION_ENABLED = True
        self.PARTICLE_DENSITY = 1.5      # Multiplier for particle effects
        self.GLOW_EFFECTS_ENABLED = True
        
        # Game settings
        self.CELL_SIZE = 20
        self.GRID_WIDTH = self.WIDTH // self.CELL_SIZE
        self.GRID_HEIGHT = self.HEIGHT // self.CELL_SIZE
        self.INITIAL_SNAKE_LENGTH = 3
        self.INITIAL_SNAKE_SPEED = 8  # Moves per second
        self.MAX_SNAKE_SPEED = 20
        
        # Power-up settings
        self.POWERUP_DURATION = 5000  # milliseconds
        self.POWERUP_SPAWN_CHANCE = 0.1  # 10% chance for power-up to spawn
        self.BONUS_FOOD_SPAWN_CHANCE = 0.2  # 20% chance for bonus food
        
        # Game modes
        self.GAME_MODES = {
            'classic': {
                'name': 'Classic',
                'description': 'Classic snake gameplay.',
                'walls': False,
                'obstacles': False,
                'speed_increase': 0.5  # Increase speed by 0.5 for each food eaten
            },
            'time_trial': {
                'name': 'Time Trial',
                'description': 'Collect as much food as possible in 60 seconds.',
                'walls': False,
                'obstacles': False,
                'time_limit': 60000,  # 60 seconds in milliseconds
                'speed_increase': 0
            },
            'obstacle': {
                'name': 'Obstacle Course',
                'description': 'Navigate through obstacles.',
                'walls': True,
                'obstacles': True,
                'num_obstacles': 15,
                'speed_increase': 0.3
            },
            'survival': {
                'name': 'Survival',
                'description': 'Snake speeds up over time. Survive as long as possible.',
                'walls': True,
                'obstacles': False,
                'speed_increase': 1.0,
                'time_speed_increase': 0.5  # Increase speed by 0.5 every 10 seconds
            }
        }
        
        # Snake textures and animations
        self.SNAKE_HEAD_RADIUS = int(self.CELL_SIZE * 0.6)
        self.SNAKE_BODY_RADIUS = int(self.CELL_SIZE * 0.5)
        self.SNAKE_EYES_ENABLED = True
        self.SNAKE_TRAIL_EFFECT = True
        
        # Particle settings
        self.PARTICLE_COUNT = 30  # Increased from 20
        self.PARTICLE_LIFETIME = 30  # frames
        self.PARTICLE_COLORS = [
            (255, 255, 50), (255, 220, 50), (255, 180, 50),
            (255, 140, 50), (255, 100, 50)
        ]
        
        # Sound settings
        self.SOUND_ENABLED = True
        self.MUSIC_VOLUME = 0.3
        self.SFX_VOLUME = 0.5
        
    def is_touch_device(self):
        """Helper method to check if device has touch capabilities"""
        # Check for touch events in pygame event queue
        for event in pygame.event.get():
            if event.type == pygame.FINGERDOWN:
                self.HAS_TOUCHSCREEN = True
                return True
        
        # Also check platform if possible
        try:
            import platform
            system = platform.system().lower()
            if 'android' in system or 'ios' in system:
                self.HAS_TOUCHSCREEN = True
                return True
        except:
            pass
            
        return self.HAS_TOUCHSCREEN 