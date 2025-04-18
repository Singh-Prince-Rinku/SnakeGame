#!/usr/bin/env python3
import pygame
import sys
import os
from src.game import Game
from src.menu import MainMenu
from src.settings import Settings

def main():
    # Initialize pygame and mixer
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()
    
    # Set up the game window
    settings = Settings()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Realistic Snake")
    
    # Set icon for the game window
    try:
        icon_path = os.path.join('assets', 'images', 'snake_icon.png')
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Could not load icon: {e}")
        # Create a simple surface as icon instead
        icon_size = 32
        icon = pygame.Surface((icon_size, icon_size))
        icon.fill((40, 120, 10))  # Green background
        pygame.draw.circle(icon, (80, 180, 30), (icon_size//2, icon_size//2), icon_size//3)  # Snake head
        pygame.display.set_icon(icon)
    
    # Initialize clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create game states
    game = Game(screen, settings)
    main_menu = MainMenu(screen, settings)
    
    # Game state (0: Menu, 1: Game, 2: Game Over)
    state = 0
    selected_mode = None
    
    # Detect if this is likely a touch device - try to detect at launch
    try:
        # Use a dummy event check to try to detect touch capability
        touch_events = [e for e in pygame.event.get() if e.type == pygame.FINGERDOWN]
        settings.HAS_TOUCHSCREEN = len(touch_events) > 0 or hasattr(pygame, 'FINGERDOWN')
    except:
        # Default to False if detection fails
        settings.HAS_TOUCHSCREEN = False
    
    # Game over buttons for touch screen
    restart_button = pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 + 100, 100, 50)
    menu_button = pygame.Rect(settings.WIDTH // 2 + 20, settings.HEIGHT // 2 + 100, 100, 50)
    
    # Main game loop
    running = True
    while running:
        # Process pygame events - get all events at the start of the frame
        current_events = list(pygame.event.get())
        
        # Update mouse position for hover effects regardless of events
        mouse_pos = pygame.mouse.get_pos()
        if state == 0:
            # Update menu button hover states
            for button in main_menu.buttons:
                button.update(mouse_pos)
                
        # Process all events
        for event in current_events:
            if event.type == pygame.QUIT:
                running = False
                continue
            
            # Detect touch events at any point
            if event.type == pygame.FINGERDOWN:
                settings.HAS_TOUCHSCREEN = True
            
            # Pass events to current game state
            if state == 0:  # Menu
                new_state = main_menu.handle_event(event)
                if new_state is not None:
                    if new_state == 1:  # Selected a game mode
                        # Find which game mode was selected
                        for button in main_menu.buttons:
                            if button.touched and button.action and button.action != "quit":
                                selected_mode = button.action
                                break
                        
                        if selected_mode:
                            game.set_mode(selected_mode)
                        else:
                            # Default to classic if no mode was selected
                            selected_mode = "classic"
                            game.set_mode(selected_mode)
                        
                        state = new_state  # Start game
                    else:
                        running = False  # Quit selected
                        
            elif state == 1:  # Game
                new_state = game.handle_event(event)
                if new_state is not None:
                    state = new_state  # Return to menu
                    
            elif state == 2:  # Game Over
                # Game over touch/mouse controls
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                    else:  # FINGERDOWN
                        pos = (int(event.x * settings.WIDTH), int(event.y * settings.HEIGHT))
                        
                    if restart_button.collidepoint(pos):
                        game.reset()
                        state = 1  # Start new game
                    elif menu_button.collidepoint(pos):
                        state = 0  # Return to menu
                
                # Keyboard controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.reset()
                        state = 1  # Start new game
                    elif event.key == pygame.K_ESCAPE:
                        state = 0  # Return to menu
        
        # Update and render current game state
        screen.fill(settings.BG_COLOR)
        
        if state == 0:  # Menu
            main_menu.update()
            main_menu.render()
            
        elif state == 1:  # Game
            game.update()
            game.render()
            if game.game_over:
                state = 2  # Go to game over screen
                
        elif state == 2:  # Game Over
            # Game over screen
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, settings.TEXT_COLOR)
            text_rect = text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 50))
            screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render(f"Score: {game.score}", True, settings.TEXT_COLOR)
            text_rect = text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20))
            screen.blit(text, text_rect)
            
            # Draw touch-friendly buttons for game over screen with hover effect
            # Check if mouse is over buttons for hover effect
            mouse_pos = pygame.mouse.get_pos()
            restart_hover = restart_button.collidepoint(mouse_pos)
            menu_hover = menu_button.collidepoint(mouse_pos)
            
            # Draw buttons with hover effect
            restart_color = settings.BUTTON_HOVER_COLOR if restart_hover else settings.BUTTON_COLOR
            menu_color = settings.BUTTON_HOVER_COLOR if menu_hover else settings.BUTTON_COLOR
            
            pygame.draw.rect(screen, restart_color, restart_button, border_radius=8)
            pygame.draw.rect(screen, menu_color, menu_button, border_radius=8)
            
            font = pygame.font.Font(None, 28)
            restart_text = font.render("Restart", True, settings.TEXT_COLOR)
            menu_text = font.render("Menu", True, settings.TEXT_COLOR)
            
            screen.blit(restart_text, restart_text.get_rect(center=restart_button.center))
            screen.blit(menu_text, menu_text.get_rect(center=menu_button.center))
            
            # Show keyboard instructions if not using touch
            if not settings.HAS_TOUCHSCREEN:
                text = font.render("Press SPACE to restart or ESC for menu", True, settings.TEXT_COLOR)
                text_rect = text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 70))
                screen.blit(text, text_rect)
        
        # Update display and cap framerate
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 