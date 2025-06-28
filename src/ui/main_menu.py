import pygame
import math

# Fix linter errors for pygame constants
if not hasattr(pygame, 'KEYDOWN'):
    pygame.KEYDOWN = 768
    pygame.MOUSEBUTTONDOWN = 1025
    pygame.MOUSEMOTION = 1024
    pygame.K_UP = 273
    pygame.K_DOWN = 274
    pygame.K_LEFT = 276
    pygame.K_RIGHT = 275
    pygame.K_RETURN = 13
    pygame.K_SPACE = 32
    pygame.K_ESCAPE = 27
    pygame.K_w = 119
    pygame.K_s = 115
    pygame.K_a = 97
    pygame.K_d = 100

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Cyberpunk color palette (from provided image)
        self.BLACK = (0, 0, 0)
        self.DARK_BG = (15, 20, 25)
        self.PANEL_BG = (25, 35, 45)
        self.BORDER_DARK = (40, 55, 70)
        self.BORDER_LIGHT = (60, 85, 110)
        
        # Cyan/Teal spectrum
        self.CYAN_BRIGHT = (0, 255, 255)
        self.CYAN_MID = (0, 200, 220)
        self.CYAN_DARK = (0, 150, 180)
        self.TEAL_LIGHT = (64, 224, 208)
        
        # Blue spectrum
        self.BLUE_BRIGHT = (100, 200, 255)
        self.BLUE_MID = (80, 160, 220)
        self.BLUE_DARK = (60, 120, 180)
        
        # Purple/Magenta spectrum
        self.PURPLE_BRIGHT = (200, 100, 255)
        self.PURPLE_MID = (160, 80, 220)
        self.MAGENTA = (255, 0, 255)
        
        # Orange accent (for highlights)
        self.ORANGE = (255, 165, 0)
        self.ORANGE_DARK = (200, 130, 0)
        
        self.WHITE = (255, 255, 255)
        self.GRAY_LIGHT = (180, 180, 180)
        self.GRAY_MID = (120, 120, 120)
        
        # Fonts
        try:
            self.font_title = pygame.font.Font(None, 84)
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_title = pygame.font.SysFont("arial", 84, bold=True)
            self.font_large = pygame.font.SysFont("arial", 48, bold=True)
            self.font_medium = pygame.font.SysFont("arial", 36)
            self.font_small = pygame.font.SysFont("arial", 24)
        
        # Animation
        self.pulse_timer = 0
        self.selected_index = 0
        self.menu_items = ["START GAME", "CONTROLS", "QUIT"]
        
    def update(self, dt):
        """Update animations"""
        self.pulse_timer += dt * 0.002
    
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
                start_y = self.screen_height // 2 + 50
                item_height = 80
                
                for i, item in enumerate(self.menu_items):
                    item_y = start_y + i * item_height
                    item_rect = pygame.Rect(self.screen_width // 2 - 200, item_y - 30, 400, 60)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        return item
        elif event.type == pygame.MOUSEMOTION:
            # Highlight menu item under mouse
            mouse_x, mouse_y = event.pos
            start_y = self.screen_height // 2 + 50
            item_height = 80
            
            for i, item in enumerate(self.menu_items):
                item_y = start_y + i * item_height
                item_rect = pygame.Rect(self.screen_width // 2 - 200, item_y - 30, 400, 60)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_index = i
                    break
        
        return None
    
    def draw(self, surface):
        """Draw the main menu"""
        # Background
        surface.fill(self.DARK_BG)
        
        # Draw hexagonal frame for title
        self.draw_hex_frame(surface, self.screen_width // 2, 200, 350, 120)
        
        # Title with glow effect
        title_text = "CYBER SURVIVAL"
        title_surface = self.font_title.render(title_text, True, self.CYAN_BRIGHT)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 180))
        
        # Glow effect
        glow_surface = self.font_title.render(title_text, True, self.CYAN_DARK)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            surface.blit(glow_surface, glow_rect)
        
        surface.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "WAVE-BASED CYBERPUNK ACTION"
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.ORANGE)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 220))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Menu items with cyberpunk panels
        start_y = self.screen_height // 2 + 50
        item_height = 80
        
        for i, item in enumerate(self.menu_items):
            is_selected = (i == self.selected_index)
            item_y = start_y + i * item_height
            self.draw_menu_panel(surface, item, self.screen_width // 2, item_y, is_selected)
        
        # Corner decorative elements
        self.draw_corner_elements(surface)
        
        # Controls hint with panel
        hint_panel_rect = pygame.Rect(50, self.screen_height - 100, self.screen_width - 100, 60)
        self.draw_panel_border(surface, hint_panel_rect, self.BORDER_DARK, self.PANEL_BG)
        
        hint_text = "↑↓ / WS: Navigate    Enter / Space / Click: Select    ESC: Quit"
        hint_surface = self.font_small.render(hint_text, True, self.GRAY_LIGHT)
        hint_rect = hint_surface.get_rect(center=hint_panel_rect.center)
        surface.blit(hint_surface, hint_rect)
        
        # Version info
        version_text = "v1.0 - NEURAL INTERFACE ACTIVE"
        version_surface = self.font_small.render(version_text, True, self.CYAN_DARK)
        version_rect = version_surface.get_rect(bottomright=(self.screen_width - 20, self.screen_height - 20))
        surface.blit(version_surface, version_rect)
    
    def draw_menu_panel(self, surface, text, center_x, center_y, is_selected):
        """Draw a cyberpunk-style menu panel"""
        panel_width = 400
        panel_height = 60
        
        # Panel rectangle
        panel_rect = pygame.Rect(center_x - panel_width // 2, center_y - panel_height // 2, panel_width, panel_height)
        
        # Colors based on selection
        if is_selected:
            bg_color = self.PANEL_BG
            border_color = self.CYAN_BRIGHT
            text_color = self.CYAN_BRIGHT
            accent_color = self.ORANGE
        else:
            bg_color = (self.PANEL_BG[0] - 10, self.PANEL_BG[1] - 10, self.PANEL_BG[2] - 10)
            border_color = self.BORDER_LIGHT
            text_color = self.WHITE
            accent_color = self.GRAY_MID
        
        # Draw panel with angled corners
        self.draw_angled_panel(surface, panel_rect, bg_color, border_color)
        
        # Selection indicators
        if is_selected:
            # Left indicator
            left_points = [
                (panel_rect.left - 20, center_y),
                (panel_rect.left - 5, center_y - 8),
                (panel_rect.left - 5, center_y + 8)
            ]
            pygame.draw.polygon(surface, accent_color, left_points)
            
            # Right indicator
            right_points = [
                (panel_rect.right + 20, center_y),
                (panel_rect.right + 5, center_y - 8),
                (panel_rect.right + 5, center_y + 8)
            ]
            pygame.draw.polygon(surface, accent_color, right_points)
        
        # Text
        text_surface = self.font_large.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=panel_rect.center)
        surface.blit(text_surface, text_rect)
    
    def draw_angled_panel(self, surface, rect, bg_color, border_color):
        """Draw a panel with angled corners using proper clipping"""
        corner_size = 15
        
        # Create the angled panel shape (octagon)
        points = [
            (rect.left + corner_size, rect.top),                    # Top-left angled
            (rect.right - corner_size, rect.top),                  # Top-right angled
            (rect.right, rect.top + corner_size),                  # Right-top angled
            (rect.right, rect.bottom - corner_size),               # Right-bottom angled
            (rect.right - corner_size, rect.bottom),               # Bottom-right angled
            (rect.left + corner_size, rect.bottom),                # Bottom-left angled
            (rect.left, rect.bottom - corner_size),                # Left-bottom angled
            (rect.left, rect.top + corner_size)                    # Left-top angled
        ]
        
        # Draw the filled panel
        pygame.draw.polygon(surface, bg_color, points)
        
        # Draw the border
        pygame.draw.polygon(surface, border_color, points, 2)
    
    def draw_hex_frame(self, surface, center_x, center_y, width, height):
        """Draw a hexagonal frame around the title"""
        # Hexagon points
        w2, h2 = width // 2, height // 2
        hex_points = [
            (center_x - w2 + 30, center_y - h2),
            (center_x + w2 - 30, center_y - h2),
            (center_x + w2, center_y),
            (center_x + w2 - 30, center_y + h2),
            (center_x - w2 + 30, center_y + h2),
            (center_x - w2, center_y)
        ]
        
        # Draw hexagon border
        pygame.draw.polygon(surface, self.PANEL_BG, hex_points)
        pygame.draw.polygon(surface, self.CYAN_MID, hex_points, 3)
        
        # Corner accents
        for i, point in enumerate(hex_points):
            pygame.draw.circle(surface, self.ORANGE, point, 4)
    
    def draw_corner_elements(self, surface):
        """Draw decorative corner elements"""
        corner_size = 60
        
        # Top-left corner
        tl_points = [
            (20, 20), (corner_size, 20), (corner_size - 15, 35),
            (35, 35), (35, corner_size - 15), (20, corner_size)
        ]
        pygame.draw.polygon(surface, self.BORDER_LIGHT, tl_points, 2)
        
        # Top-right corner
        tr_points = [
            (self.screen_width - 20, 20), (self.screen_width - corner_size, 20),
            (self.screen_width - corner_size + 15, 35), (self.screen_width - 35, 35),
            (self.screen_width - 35, corner_size - 15), (self.screen_width - 20, corner_size)
        ]
        pygame.draw.polygon(surface, self.BORDER_LIGHT, tr_points, 2)
        
        # Bottom-left corner
        bl_points = [
            (20, self.screen_height - 20), (corner_size, self.screen_height - 20),
            (corner_size - 15, self.screen_height - 35), (35, self.screen_height - 35),
            (35, self.screen_height - corner_size + 15), (20, self.screen_height - corner_size)
        ]
        pygame.draw.polygon(surface, self.BORDER_LIGHT, bl_points, 2)
        
        # Bottom-right corner
        br_points = [
            (self.screen_width - 20, self.screen_height - 20),
            (self.screen_width - corner_size, self.screen_height - 20),
            (self.screen_width - corner_size + 15, self.screen_height - 35),
            (self.screen_width - 35, self.screen_height - 35),
            (self.screen_width - 35, self.screen_height - corner_size + 15),
            (self.screen_width - 20, self.screen_height - corner_size)
        ]
        pygame.draw.polygon(surface, self.BORDER_LIGHT, br_points, 2)
    
    def draw_panel_border(self, surface, rect, border_color, bg_color):
        """Draw a simple panel with border"""
        pygame.draw.rect(surface, bg_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)
    
    def draw_controls_screen(self, surface):
        """Draw the controls/help screen"""
        # Background
        surface.fill(self.DARK_BG)
        
        # Title frame
        self.draw_hex_frame(surface, self.screen_width // 2, 120, 300, 80)
        
        title_text = "NEURAL INTERFACE"
        title_surface = self.font_title.render(title_text, True, self.CYAN_BRIGHT)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 120))
        surface.blit(title_surface, title_rect)
        
        # Controls panels
        left_panel = pygame.Rect(50, 200, self.screen_width // 2 - 75, 400)
        right_panel = pygame.Rect(self.screen_width // 2 + 25, 200, self.screen_width // 2 - 75, 400)
        
        self.draw_angled_panel(surface, left_panel, self.PANEL_BG, self.CYAN_MID)
        self.draw_angled_panel(surface, right_panel, self.PANEL_BG, self.CYAN_MID)
        
        # Left panel - Controls
        controls_title = self.font_large.render("CONTROLS", True, self.ORANGE)
        surface.blit(controls_title, (left_panel.x + 20, left_panel.y + 20))
        
        controls = [
            ("MOVEMENT", "WASD / Arrow Keys", self.BLUE_BRIGHT),
            ("SHOOTING", "Mouse / Spacebar", self.PURPLE_BRIGHT),
            ("PAUSE", "ESC", self.CYAN_BRIGHT),
        ]
        
        y_offset = 80
        for label, desc, color in controls:
            label_surface = self.font_medium.render(label + ":", True, color)
            desc_surface = self.font_small.render(desc, True, self.WHITE)
            
            surface.blit(label_surface, (left_panel.x + 20, left_panel.y + y_offset))
            surface.blit(desc_surface, (left_panel.x + 20, left_panel.y + y_offset + 25))
            y_offset += 60
        
        # Right panel - Game Info
        info_title = self.font_large.render("MISSION BRIEF", True, self.ORANGE)
        surface.blit(info_title, (right_panel.x + 20, right_panel.y + 20))
        
        info_lines = [
            ("OBJECTIVE", "Survive endless cyber waves", self.CYAN_BRIGHT),
            ("XP SYSTEM", "Eliminate targets for experience", self.BLUE_BRIGHT),
            ("UPGRADES", "Neural enhancement every level", self.PURPLE_BRIGHT),
            ("", "", self.WHITE),
            ("TARGET TYPES", "", self.ORANGE),
            ("Red Cyborgs", "Basic units - 7 XP", self.WHITE),
            ("Yellow Cyborgs", "Fast assault - 9 XP", self.WHITE),
            ("Green Cyborgs", "Heavy armor - 11 XP", self.WHITE),
            ("Purple Cyborgs", "Elite class - 15 XP", self.WHITE),
        ]
        
        y_offset = 80
        for label, desc, color in info_lines:
            if label:
                if desc:
                    label_surface = self.font_small.render(label + ":", True, color)
                    desc_surface = self.font_small.render(desc, True, self.GRAY_LIGHT)
                    surface.blit(label_surface, (right_panel.x + 20, right_panel.y + y_offset))
                    surface.blit(desc_surface, (right_panel.x + 140, right_panel.y + y_offset))
                else:
                    label_surface = self.font_medium.render(label, True, color)
                    surface.blit(label_surface, (right_panel.x + 20, right_panel.y + y_offset))
            y_offset += 30
        
        # Back instruction
        back_panel = pygame.Rect(self.screen_width // 2 - 200, self.screen_height - 80, 400, 40)
        self.draw_panel_border(surface, back_panel, self.BORDER_LIGHT, self.PANEL_BG)
        
        back_text = "Press ESC or click anywhere to return"
        back_surface = self.font_small.render(back_text, True, self.CYAN_BRIGHT)
        back_rect = back_surface.get_rect(center=back_panel.center)
        surface.blit(back_surface, back_rect) 