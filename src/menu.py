import pygame
import math
import os
from src.particle import ParticleSystem

class Button:
    def __init__(self, x, y, width, height, text, settings, action=None, hover_text=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hover_text = hover_text
        self.settings = settings
        self.action = action
        self.color = settings.BUTTON_COLOR
        self.hover_color = settings.BUTTON_HOVER_COLOR
        self.text_color = settings.TEXT_COLOR
        self.hovered = False
        self.touched = False  # Track touch state
        self.particle_system = ParticleSystem(settings)
        # Make buttons larger for touch screens
        if settings.HAS_TOUCHSCREEN and width < 300:
            # Increase button size for touch
            expand = 20
            self.rect.inflate_ip(expand, expand)
            
        # For animation effects
        self.pulse_effect = 0
        self.pulse_direction = 1
        self.angle = 0  # For rotation effect
        
    def update(self, mouse_pos):
        prev_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Create particles when button is first hovered
        if not prev_hovered and self.hovered:
            for _ in range(15):  # More particles
                x = random.randint(self.rect.left, self.rect.right)
                y = random.randint(self.rect.top, self.rect.bottom)
                self.particle_system.create_particles(x, y, 5)
                
        # Update animation effects
        self.pulse_effect += 0.05 * self.pulse_direction
        if self.pulse_effect > 1.0:
            self.pulse_effect = 1.0
            self.pulse_direction = -1
        elif self.pulse_effect < 0.0:
            self.pulse_effect = 0.0
            self.pulse_direction = 1
            
        # Slow rotation for hover text
        self.angle = (self.angle + 0.5) % 360
                
        # Update particles
        self.particle_system.update()
        
    def draw(self, screen):
        # Calculate animation effects
        pulse_amt = 0
        if self.hovered or self.touched:
            pulse_amt = int(self.pulse_effect * 5)  # Subtle pulsing
            
        # Draw button with hovering/touched effect
        if self.touched:
            color = (min(255, self.hover_color[0] + 30), 
                     min(255, self.hover_color[1] + 30), 
                     min(255, self.hover_color[2] + 30))
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.color
            
        # Draw a glow effect for the active button
        if self.hovered or self.touched:
            glow_rect = self.rect.inflate(12 + pulse_amt, 12 + pulse_amt)
            self._draw_rounded_rect(screen, glow_rect, (*color, 100), 12)
        
        # Draw button background with rounded corners
        button_rect = self.rect.inflate(pulse_amt, pulse_amt)
        self._draw_rounded_rect(screen, button_rect, color, 8)
        
        # Draw button text
        font = pygame.font.Font(None, 32)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        
        # Add subtle text animation
        if self.hovered or self.touched:
            # Make text pulse slightly to give feedback
            scale = 1.0 + (0.05 * self.pulse_effect)
            text_surf = pygame.transform.scale(
                text_surf, 
                (int(text_surf.get_width() * scale), 
                 int(text_surf.get_height() * scale))
            )
            text_rect = text_surf.get_rect(center=button_rect.center)
        
        screen.blit(text_surf, text_rect)
        
        # Draw hover text if provided and hovered
        if self.hover_text and (self.hovered or self.touched):
            hover_font = pygame.font.Font(None, 24)
            hover_surf = hover_font.render(self.hover_text, True, self.text_color)
            
            # Make hover text appear with animated effect
            hover_rect = hover_surf.get_rect(midtop=(button_rect.centerx, button_rect.bottom + 5))
            
            # Draw fancier background for hover text
            padding = 10
            bg_rect = hover_rect.inflate(padding * 2, padding * 2)
            self._draw_rounded_rect(screen, bg_rect, (*color, 200), 8)
            
            # Add a subtle border
            pygame.draw.rect(screen, self.text_color, bg_rect, width=1, border_radius=8)
            
            screen.blit(hover_surf, hover_rect)
            
        # Draw particles
        self.particle_system.draw(screen)
        
    def _draw_rounded_rect(self, surface, rect, color, corner_radius):
        """Draw a rectangle with rounded corners."""
        if corner_radius < 1:
            pygame.draw.rect(surface, color, rect)
            return
            
        # Draw the main rectangle without corners
        pygame.draw.rect(surface, color, rect.inflate(-corner_radius * 2, 0))
        pygame.draw.rect(surface, color, rect.inflate(0, -corner_radius * 2))
        
        # Draw the four corners
        corner_rect = pygame.Rect(0, 0, corner_radius * 2, corner_radius * 2)
        
        corner_rect.topleft = rect.topleft
        pygame.draw.arc(surface, color, corner_rect, math.pi, 3 * math.pi / 2, corner_radius)
        
        corner_rect.topright = rect.topright
        pygame.draw.arc(surface, color, corner_rect, 3 * math.pi / 2, 2 * math.pi, corner_radius)
        
        corner_rect.bottomright = rect.bottomright
        pygame.draw.arc(surface, color, corner_rect, 0, math.pi / 2, corner_radius)
        
        corner_rect.bottomleft = rect.bottomleft
        pygame.draw.arc(surface, color, corner_rect, math.pi / 2, math.pi, corner_radius)
        
    def handle_event(self, event):
        # For mouse down events - handle both clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.rect.collidepoint(pos):
                self.touched = True
                # Special handling for quit button
                if self.action == "quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return None
                elif self.action:
                    return self.action
                
        # For touch events
        elif event.type == pygame.FINGERDOWN:
            # Convert normalized finger position to screen coordinates
            pos = (int(event.x * self.settings.WIDTH), 
                   int(event.y * self.settings.HEIGHT))
            if self.rect.collidepoint(pos):
                self.touched = True
                # Special handling for quit button
                if self.action == "quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return None
                elif self.action:
                    return self.action
                
        # Reset touched state on up events
        elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            self.touched = False
                
        return None


class MainMenu:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.particle_system = ParticleSystem(settings)
        
        # Load logo/image if available
        self.logo_img = None
        try:
            logo_path = os.path.join('assets', 'images', 'snake_logo.png')
            if os.path.exists(logo_path):
                self.logo_img = pygame.image.load(logo_path)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Initialize buttons
        self._init_buttons()
        
        # For animated background
        self.animation_timer = 0
        
        # For additional animation effects
        self.star_particles = []
        self._create_star_field()
        
    def _create_star_field(self):
        """Create a star field for background animation"""
        for _ in range(100):
            x = random.randint(0, self.settings.WIDTH)
            y = random.randint(0, self.settings.HEIGHT)
            size = random.uniform(0.5, 2.5)
            speed = random.uniform(0.1, 0.5)
            brightness = random.uniform(0.3, 1.0)
            self.star_particles.append({
                'x': x, 'y': y, 'size': size, 'speed': speed, 
                'brightness': brightness, 'color': (255, 255, 255)
            })
            
    def _update_star_field(self):
        """Update the star field animation"""
        for star in self.star_particles:
            # Make stars twinkle
            star['brightness'] += random.uniform(-0.05, 0.05)
            star['brightness'] = max(0.3, min(1.0, star['brightness']))
            
            # Move stars slowly downward
            star['y'] += star['speed']
            if star['y'] > self.settings.HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, self.settings.WIDTH)
                
    def _draw_star_field(self):
        """Draw the animated star field"""
        for star in self.star_particles:
            # Draw star with current brightness
            color = tuple(int(c * star['brightness']) for c in star['color'])
            pygame.draw.circle(self.screen, color, 
                              (int(star['x']), int(star['y'])), 
                              star['size'])
            
    def _init_buttons(self):
        self.buttons = []
        
        # Get game modes from settings
        game_modes = self.settings.GAME_MODES
        
        # Calculate button positions - make buttons larger for touch screens
        btn_width = 300 if self.settings.HAS_TOUCHSCREEN else 250
        btn_height = 80 if self.settings.HAS_TOUCHSCREEN else 60
        btn_margin = 25 if self.settings.HAS_TOUCHSCREEN else 20
        
        # Calculate starting position - center buttons vertically
        start_y = self.settings.HEIGHT // 2 - (len(game_modes) * (btn_height + btn_margin)) // 2
        
        # Create a button for each game mode
        for i, (mode_key, mode_info) in enumerate(game_modes.items()):
            y_pos = start_y + i * (btn_height + btn_margin)
            x_pos = self.settings.WIDTH // 2 - btn_width // 2
            
            # Create button with mode name and description as hover text
            btn = Button(x_pos, y_pos, btn_width, btn_height, 
                        mode_info['name'], self.settings, 
                        action=mode_key, hover_text=mode_info['description'])
            self.buttons.append(btn)
            
        # Add quit button
        quit_y = start_y + len(game_modes) * (btn_height + btn_margin) + btn_margin
        quit_btn = Button(x_pos, quit_y, btn_width, btn_height, 
                         "Quit", self.settings, action="quit")
        self.buttons.append(quit_btn)
        
        # Create occasional particles for visual effect
        for _ in range(30):
            x = random.randint(0, self.settings.WIDTH)
            y = random.randint(0, self.settings.HEIGHT)
            self.particle_system.create_particles(x, y, 1)
        
    def update(self):
        # Update animation timer
        self.animation_timer += 0.01
        
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Update buttons with current mouse position
        for button in self.buttons:
            button.update(mouse_pos)
            
        # Update particles
        self.particle_system.update()
        
        # Update star field
        self._update_star_field()
        
        # Add occasional new particles for visual effect
        if random.random() < 0.05:
            x = random.randint(0, self.settings.WIDTH)
            y = random.randint(0, self.settings.HEIGHT)
            self.particle_system.create_particles(x, y, 3)
        
    def render(self):
        # Draw animated background
        self._draw_background()
        
        # Draw star field
        self._draw_star_field()
        
        # Draw logo if available, otherwise draw title text
        if self.logo_img:
            logo_rect = self.logo_img.get_rect(centerx=self.settings.WIDTH // 2, 
                                              y=self.settings.HEIGHT // 6)
            self.screen.blit(self.logo_img, logo_rect)
        else:
            # Draw title with pulsating effect
            pulse = (math.sin(self.animation_timer * 3) + 1) * 0.1
            title_size = 80 + int(pulse * 10)
            font = pygame.font.Font(None, title_size)
            
            # Create glowing title effect
            glow_color = (100, 200, 150)
            for offset in range(3, 0, -1):
                shadow_color = (*glow_color, 50 + offset * 30)
                title_text = font.render("Realistic Snake", True, shadow_color)
                title_rect = title_text.get_rect(centerx=self.settings.WIDTH // 2 + offset, 
                                               y=self.settings.HEIGHT // 6 + offset)
                self.screen.blit(title_text, title_rect)
            
            # Draw main title text
            title_text = font.render("Realistic Snake", True, self.settings.TEXT_COLOR)
            title_rect = title_text.get_rect(centerx=self.settings.WIDTH // 2, 
                                           y=self.settings.HEIGHT // 6)
            self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
            
        # Draw particles
        self.particle_system.draw(self.screen)
        
        # Draw footer text - updated for touch controls
        font = pygame.font.Font(None, 24)
        if self.settings.HAS_TOUCHSCREEN:
            footer_text = font.render("Use the on-screen directional buttons to control the snake", 
                                   True, self.settings.TEXT_COLOR)
        else:
            footer_text = font.render("Use arrow keys/WASD or touch controls to play", 
                                   True, self.settings.TEXT_COLOR)
        footer_rect = footer_text.get_rect(centerx=self.settings.WIDTH // 2, 
                                         bottom=self.settings.HEIGHT - 20)
        self.screen.blit(footer_text, footer_rect)
        
    def _draw_background(self):
        # Draw animated background pattern
        for x in range(0, self.settings.WIDTH, self.settings.CELL_SIZE):
            for y in range(0, self.settings.HEIGHT, self.settings.CELL_SIZE):
                # Calculate distance from center for radial effect
                center_x = self.settings.WIDTH // 2
                center_y = self.settings.HEIGHT // 2
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Use distance and time for color oscillation
                color_value = (math.sin(distance * 0.01 + self.animation_timer) + 1) * 0.5
                color_value = max(0.1, min(0.3, color_value))  # Limit range
                
                # Create slightly varied color based on position
                color = (
                    int(self.settings.BG_COLOR[0] * color_value),
                    int(self.settings.BG_COLOR[1] * color_value),
                    int(self.settings.BG_COLOR[2] * color_value)
                )
                
                # Draw grid cell
                pygame.draw.rect(self.screen, color, (x, y, self.settings.CELL_SIZE, self.settings.CELL_SIZE))
                
    def handle_event(self, event):
        """Handle menu events, including button presses."""
        # Check each button
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                if action == "quit":
                    return None  # Signal to quit game
                else:
                    # Return game mode action which will become game state
                    return 1  # Return state 1 (game) with mode as extra info
                
        return None
        

# Import at the end to avoid circular imports
import random 