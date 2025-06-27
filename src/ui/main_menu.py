import pygame
import math

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Colors (New palette)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.MINT_GREEN = (108, 255, 222)
        self.CYAN = (108, 222, 255)
        self.ELECTRIC_BLUE = (108, 178, 255)
        self.ROYAL_BLUE = (108, 134, 255)
        self.DEEP_BLUE = (56, 89, 178)
        self.PURPLE = (134, 108, 255)
        self.VIOLET = (178, 108, 255)
        self.MAGENTA = (222, 108, 255)
        self.HOT_PINK = (255, 108, 222)
        self.CORAL = (255, 134, 178)
        self.DARK_PURPLE = (44, 26, 89)
        
        # Fonts
        try:
            self.font_title = pygame.font.Font(None, 72)
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_title = pygame.font.SysFont("arial", 72, bold=True)
            self.font_large = pygame.font.SysFont("arial", 48)
            self.font_medium = pygame.font.SysFont("arial", 36)
            self.font_small = pygame.font.SysFont("arial", 24)
        
        # Animation
        self.pulse_timer = 0
        self.selected_index = 0
        self.menu_items = ["START GAME", "CONTROLS", "QUIT"]
        
    def update(self, dt):
        """Update animations"""
        self.pulse_timer += dt * 0.003
    
    def handle_input(self, event):
        """Handle input for main menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                return None
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.menu_items[self.selected_index]
            elif event.key == pygame.K_ESCAPE:
                return "QUIT"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check which menu item was clicked
                start_y = self.screen_height // 2 - 50
                item_height = 60
                
                for i, item in enumerate(self.menu_items):
                    item_y = start_y + i * item_height
                    item_rect = pygame.Rect(self.screen_width // 2 - 150, item_y - 25, 300, 50)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        return item
        elif event.type == pygame.MOUSEMOTION:
            # Highlight menu item under mouse
            mouse_x, mouse_y = event.pos
            start_y = self.screen_height // 2 - 50
            item_height = 60
            
            for i, item in enumerate(self.menu_items):
                item_y = start_y + i * item_height
                item_rect = pygame.Rect(self.screen_width // 2 - 150, item_y - 25, 300, 50)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_index = i
                    break
        
        return None
    
    def draw(self, surface):
        """Draw the main menu"""
        # Background
        surface.fill(self.DARK_PURPLE)
        
        # Draw grid background
        self.draw_grid(surface)
        
        # Title with pulsing effect
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003)
        title_color = (int(self.ELECTRIC_BLUE[0] * pulse),
                      int(self.ELECTRIC_BLUE[1] * pulse),
                      int(self.ELECTRIC_BLUE[2] * pulse))
        
        # Main title with pulsing effect
        title_text = "CYBER SURVIVAL"
        title_surface = self.font_title.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 200))
        surface.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Wave-Based Cyberpunk Action"
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.HOT_PINK)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 150))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Menu items
        start_y = self.screen_height // 2 - 50
        item_height = 60
        
        for i, item in enumerate(self.menu_items):
            is_selected = (i == self.selected_index)
            self.draw_menu_item(surface, item, start_y + i * item_height, is_selected)
        
        # Controls hint
        hint_text = "↑↓ / WS: Navigate    Enter / Space / Click: Select    ESC: Quit"
        hint_surface = self.font_small.render(hint_text, True, self.CYAN)
        hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        surface.blit(hint_surface, hint_rect)
        
        # Version/credits
        version_text = "v1.0 - Made with Python & Pygame"
        version_surface = self.font_small.render(version_text, True, self.CYAN)
        version_rect = version_surface.get_rect(bottomright=(self.screen_width - 10, self.screen_height - 10))
        surface.blit(version_surface, version_rect)
    
    def draw_menu_item(self, surface, text, y, is_selected):
        """Draw a single menu item"""
        # Colors
        if is_selected:
            text_color = self.BLACK
            bg_color = self.CYAN
            border_color = self.MINT_GREEN
        else:
            text_color = self.WHITE
            bg_color = (20, 20, 40)  # Semi-transparent dark background
            border_color = self.CYAN
        
        # Background
        item_rect = pygame.Rect(self.screen_width // 2 - 150, y - 25, 300, 50)
        pygame.draw.rect(surface, bg_color, item_rect)
        pygame.draw.rect(surface, border_color, item_rect, 2)
        
        # Text - center it within the rectangle
        text_surface = self.font_large.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=item_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Selection indicator
        if is_selected:
            # Left arrow
            arrow_color = self.CYAN
            pygame.draw.polygon(surface, arrow_color, [
                (self.screen_width // 2 - 180, y),
                (self.screen_width // 2 - 165, y - 8),
                (self.screen_width // 2 - 165, y + 8)
            ])
            # Right arrow
            pygame.draw.polygon(surface, arrow_color, [
                (self.screen_width // 2 + 180, y),
                (self.screen_width // 2 + 165, y - 8),
                (self.screen_width // 2 + 165, y + 8)
            ])
    
    def draw_grid(self, surface):
        """Draw cyberpunk grid background"""
        grid_size = 50
        grid_color = (self.CYAN[0]//8, self.CYAN[1]//8, self.CYAN[2]//8)
        
        for x in range(0, self.screen_width, grid_size):
            pygame.draw.line(surface, grid_color, (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_size):
            pygame.draw.line(surface, grid_color, (0, y), (self.screen_width, y), 1)
    
    def draw_controls_screen(self, surface):
        """Draw the controls/help screen"""
        # Background
        surface.fill(self.DARK_PURPLE)
        self.draw_grid(surface)
        
        # Title
        title_text = "CONTROLS"
        title_surface = self.font_title.render(title_text, True, self.MINT_GREEN)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title_surface, title_rect)
        
        # Controls list
        controls = [
            ("MOVEMENT", "WASD / Arrow Keys", self.ELECTRIC_BLUE),
            ("SHOOTING", "Mouse / Spacebar", self.HOT_PINK),
            ("PAUSE", "ESC", self.CYAN),
            ("", "", self.WHITE),  # Spacer
            ("OBJECTIVE", "Survive waves of enemies", self.MINT_GREEN),
            ("XP SYSTEM", "Kill enemies to gain XP and level up", self.MINT_GREEN),
            ("UPGRADES", "Choose from 3 upgrades each level", self.MINT_GREEN),
            ("", "", self.WHITE),  # Spacer
            ("ENEMY TYPES", "", self.HOT_PINK),
            ("Red Cyborgs", "Basic enemies - 7 XP", self.WHITE),
            ("Yellow Cyborgs", "Fast & agile - 9 XP", self.WHITE),
            ("Green Cyborgs", "Heavy tanks - 11 XP", self.WHITE),
            ("Purple Cyborgs", "Elite bosses - 15 XP", self.WHITE),
        ]
        
        start_y = 180
        line_height = 35
        
        for i, (label, description, color) in enumerate(controls):
            y = start_y + i * line_height
            
            if label:  # Skip empty lines
                if description:
                    # Two-column layout
                    label_surface = self.font_medium.render(label + ":", True, color)
                    desc_surface = self.font_medium.render(description, True, self.WHITE)
                    
                    surface.blit(label_surface, (self.screen_width // 2 - 200, y))
                    surface.blit(desc_surface, (self.screen_width // 2 - 50, y))
                else:
                    # Centered text (section headers)
                    text_surface = self.font_medium.render(label, True, color)
                    text_rect = text_surface.get_rect(center=(self.screen_width // 2, y))
                    surface.blit(text_surface, text_rect)
        
        # Back instruction
        back_text = "Press ESC or click anywhere to return"
        back_surface = self.font_small.render(back_text, True, self.CYAN)
        back_rect = back_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        surface.blit(back_surface, back_rect) 