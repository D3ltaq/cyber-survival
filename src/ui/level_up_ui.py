import pygame
import math

# Fix linter errors for pygame constants
if not hasattr(pygame, 'K_UP'):
    pygame.K_UP = 273
    pygame.K_DOWN = 274
    pygame.K_w = 119
    pygame.K_s = 115
    pygame.K_RETURN = 13
    pygame.K_SPACE = 32
    pygame.KEYDOWN = 768
    pygame.MOUSEBUTTONDOWN = 1025
    pygame.MOUSEMOTION = 1024

class LevelUpUI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Cyberpunk color palette (matching main menu)
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
        
        # Orange accent
        self.ORANGE = (255, 165, 0)
        self.ORANGE_DARK = (200, 130, 0)
        
        self.WHITE = (255, 255, 255)
        self.GRAY_LIGHT = (180, 180, 180)
        self.GRAY_MID = (120, 120, 120)
        
        # Fonts
        try:
            self.font_title = pygame.font.Font(None, 72)
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_title = pygame.font.SysFont("arial", 72, bold=True)
            self.font_large = pygame.font.SysFont("arial", 48, bold=True)
            self.font_medium = pygame.font.SysFont("arial", 32)
            self.font_small = pygame.font.SysFont("arial", 24)
        
        # Animation
        self.pulse_timer = 0
        self.selected_index = 0
    
    def update(self, dt):
        """Update animations"""
        self.pulse_timer += dt * 0.003
    
    def handle_input(self, event, choices):
        """Handle input for level up screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(choices)
                return None
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(choices)
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return choices[self.selected_index]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check which upgrade was clicked
                mouse_x, mouse_y = event.pos
                choice_height = 140
                start_y = 200
                
                for i, choice in enumerate(choices):
                    choice_y = start_y + i * choice_height
                    choice_rect = pygame.Rect(self.screen_width // 2 - 300, choice_y, 600, 120)
                    if choice_rect.collidepoint(mouse_x, mouse_y):
                        return choice
        elif event.type == pygame.MOUSEMOTION:
            # Highlight upgrade under mouse
            mouse_x, mouse_y = event.pos
            choice_height = 140
            start_y = 200
            
            for i, choice in enumerate(choices):
                choice_y = start_y + i * choice_height
                choice_rect = pygame.Rect(self.screen_width // 2 - 300, choice_y, 600, 120)
                if choice_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_index = i
                    break
        
        return None
    
    def draw(self, surface, level_system, choices):
        """Draw the level up screen"""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(220)
        overlay.fill(self.DARK_BG)
        surface.blit(overlay, (0, 0))
        
        # Title frame
        self.draw_hex_frame(surface, self.screen_width // 2, 100, 400, 80)
        
        # Title with glow effect
        title_text = f"NEURAL ENHANCEMENT - LEVEL {level_system.level}"
        title_surface = self.font_title.render(title_text, True, self.CYAN_BRIGHT)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        
        # Glow effect
        glow_surface = self.font_title.render(title_text, True, self.CYAN_DARK)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            surface.blit(glow_surface, glow_rect)
        
        surface.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "SELECT ENHANCEMENT MODULE"
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.ORANGE)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 120))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Upgrade choices with cyberpunk panels
        choice_height = 140
        start_y = 200
        
        for i, choice_id in enumerate(choices):
            upgrade_info = level_system.get_upgrade_info(choice_id)
            if not upgrade_info:
                continue
            
            choice_y = start_y + i * choice_height
            is_selected = (i == self.selected_index)
            
            self.draw_upgrade_panel(surface, upgrade_info, choice_y, is_selected)
        
        # Instructions panel
        inst_panel = pygame.Rect(self.screen_width // 2 - 200, self.screen_height - 100, 400, 60)
        self.draw_angled_panel(surface, inst_panel, self.PANEL_BG, self.BORDER_LIGHT)
        
        instructions = [
            "↑↓ / WS: Navigate    Enter / Space / Click: Select"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.font_small.render(instruction, True, self.GRAY_LIGHT)
            inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, 
                                                     self.screen_height - 70 + i * 25))
            surface.blit(inst_surface, inst_rect)
    
    def draw_upgrade_panel(self, surface, upgrade_info, y, is_selected):
        """Draw a cyberpunk-style upgrade choice panel"""
        panel_width = 600
        panel_height = 120
        panel_x = self.screen_width // 2 - panel_width // 2
        
        # Panel rectangle
        panel_rect = pygame.Rect(panel_x, y, panel_width, panel_height)
        
        # Colors based on selection and type
        upgrade_type = upgrade_info["type"]
        
        if upgrade_type == "passive":
            type_color = self.CYAN_BRIGHT
        elif upgrade_type == "weapon_upgrade" or upgrade_type == "weapon_new":
            type_color = self.PURPLE_BRIGHT
        else:
            type_color = self.BLUE_BRIGHT
        
        if is_selected:
            bg_color = self.PANEL_BG
            border_color = type_color
            text_color = self.WHITE
            accent_color = self.ORANGE
        else:
            bg_color = (self.PANEL_BG[0] - 15, self.PANEL_BG[1] - 15, self.PANEL_BG[2] - 15)
            border_color = self.BORDER_LIGHT
            text_color = self.GRAY_LIGHT
            accent_color = self.GRAY_MID
        
        # Draw panel with angled corners
        self.draw_angled_panel(surface, panel_rect, bg_color, border_color)
        
        # Selection indicators
        if is_selected:
            # Left indicator
            left_points = [
                (panel_rect.left - 25, y + panel_height // 2),
                (panel_rect.left - 10, y + panel_height // 2 - 10),
                (panel_rect.left - 10, y + panel_height // 2 + 10)
            ]
            pygame.draw.polygon(surface, accent_color, left_points)
            
            # Right indicator
            right_points = [
                (panel_rect.right + 25, y + panel_height // 2),
                (panel_rect.right + 10, y + panel_height // 2 - 10),
                (panel_rect.right + 10, y + panel_height // 2 + 10)
            ]
            pygame.draw.polygon(surface, accent_color, right_points)
        
        # Icon panel
        icon_size = 80
        icon_x = panel_x + 20
        icon_y = y + 20
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        
        self.draw_angled_panel(surface, icon_rect, self.BLACK, type_color)
        self.draw_upgrade_icon(surface, upgrade_info, icon_x + icon_size // 2, icon_y + icon_size // 2, 30)
        
        # Text content
        text_x = icon_x + icon_size + 20
        text_y = y + 15
        
        # Name with type color
        name_surface = self.font_large.render(upgrade_info["name"], True, type_color)
        surface.blit(name_surface, (text_x, text_y))
        
        # Description
        desc_surface = self.font_medium.render(upgrade_info["description"], True, text_color)
        surface.blit(desc_surface, (text_x, text_y + 35))
        
        # Level indicator
        current_level = upgrade_info["current_level"]
        max_level = upgrade_info["max_level"]
        if max_level > 1:
            level_text = f"Enhancement Level {current_level + 1}/{max_level}"
            level_surface = self.font_small.render(level_text, True, self.CYAN_MID)
            surface.blit(level_surface, (text_x, text_y + 70))
        
        # Type indicator
        type_text = upgrade_info["type"].replace("_", " ").upper()
        type_surface = self.font_small.render(f"[{type_text}]", True, type_color)
        type_rect = type_surface.get_rect(right=panel_rect.right - 20, top=text_y)
        surface.blit(type_surface, type_rect)
    
    def draw_upgrade_icon(self, surface, upgrade_info, center_x, center_y, size):
        """Draw an icon representing the upgrade type"""
        upgrade_type = upgrade_info["type"]
        upgrade_id = upgrade_info["upgrade_id"]
        
        # Color based on type
        if upgrade_type == "weapon_upgrade" or upgrade_type == "weapon_new":
            color = self.PURPLE_BRIGHT
        elif upgrade_type == "passive":
            color = self.CYAN_BRIGHT
        else:
            color = self.BLUE_BRIGHT
        
        # Draw different icons based on upgrade type
        if upgrade_type == "weapon_upgrade" or upgrade_type == "weapon_new":
            if "rapid" in upgrade_id:
                # Clock/speed symbol
                pygame.draw.circle(surface, color, (center_x, center_y), size // 2, 3)
                pygame.draw.line(surface, color, (center_x, center_y), 
                               (center_x, center_y - size // 3), 3)
                pygame.draw.line(surface, color, (center_x, center_y), 
                               (center_x + size // 4, center_y), 2)
            elif "double" in upgrade_id or "spread" in upgrade_id:
                # Multiple projectiles
                for i in range(3):
                    offset = (i - 1) * 8
                    pygame.draw.circle(surface, color, (center_x + offset, center_y), 5)
            elif "piercing" in upgrade_id:
                # Arrow through target
                pygame.draw.line(surface, color, 
                               (center_x - size // 2, center_y), 
                               (center_x + size // 2, center_y), 4)
                pygame.draw.polygon(surface, color, [
                    (center_x + size // 2, center_y),
                    (center_x + size // 3, center_y - 6),
                    (center_x + size // 3, center_y + 6)
                ])
            elif "explosive" in upgrade_id:
                # Explosion symbol
                for angle in range(0, 360, 45):
                    end_x = center_x + math.cos(math.radians(angle)) * size // 3
                    end_y = center_y + math.sin(math.radians(angle)) * size // 3
                    pygame.draw.line(surface, color, (center_x, center_y), 
                                   (end_x, end_y), 3)
            else:
                # Generic weapon icon
                pygame.draw.circle(surface, color, (center_x, center_y), size // 3, 3)
        
        elif upgrade_type == "passive":
            if "health" in upgrade_id:
                # Cross symbol
                pygame.draw.line(surface, color, 
                               (center_x - size // 3, center_y), 
                               (center_x + size // 3, center_y), 4)
                pygame.draw.line(surface, color, 
                               (center_x, center_y - size // 3), 
                               (center_x, center_y + size // 3), 4)
            elif "speed" in upgrade_id:
                # Speed lines
                for i in range(3):
                    y_offset = (i - 1) * 8
                    pygame.draw.line(surface, color, 
                                   (center_x - size // 2, center_y + y_offset), 
                                   (center_x + size // 3, center_y + y_offset), 3)
            elif "damage" in upgrade_id:
                # Sword/blade
                pygame.draw.polygon(surface, color, [
                    (center_x, center_y - size // 2),
                    (center_x + 6, center_y + size // 3),
                    (center_x - 6, center_y + size // 3)
                ])
            elif "regen" in upgrade_id:
                # Heart
                pygame.draw.circle(surface, color, (center_x - 6, center_y - 4), 8)
                pygame.draw.circle(surface, color, (center_x + 6, center_y - 4), 8)
                pygame.draw.polygon(surface, color, [
                    (center_x - 12, center_y + 4),
                    (center_x, center_y + 16),
                    (center_x + 12, center_y + 4)
                ])
            elif "shield" in upgrade_id:
                # Shield
                pygame.draw.arc(surface, color, 
                              pygame.Rect(center_x - size//2, center_y - size//2, 
                                         size, size), 
                              0, math.pi, 4)
                pygame.draw.line(surface, color, 
                               (center_x - size//2, center_y), 
                               (center_x + size//2, center_y), 4)
            else:
                # Generic passive icon
                pygame.draw.circle(surface, color, (center_x, center_y), size // 3, 3)
        
        else:
            # Generic utility icon
            pygame.draw.circle(surface, color, (center_x, center_y), size // 3, 3)
            for angle in range(0, 360, 90):
                end_x = center_x + math.cos(math.radians(angle)) * size // 4
                end_y = center_y + math.sin(math.radians(angle)) * size // 4
                pygame.draw.circle(surface, color, (int(end_x), int(end_y)), 3)
    
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
        """Draw a hexagonal frame"""
        # Hexagon points
        w2, h2 = width // 2, height // 2
        hex_points = [
            (center_x - w2 + 20, center_y - h2),
            (center_x + w2 - 20, center_y - h2),
            (center_x + w2, center_y),
            (center_x + w2 - 20, center_y + h2),
            (center_x - w2 + 20, center_y + h2),
            (center_x - w2, center_y)
        ]
        
        # Draw hexagon border
        pygame.draw.polygon(surface, self.PANEL_BG, hex_points)
        pygame.draw.polygon(surface, self.CYAN_MID, hex_points, 3)
        
        # Corner accents
        for i, point in enumerate(hex_points):
            pygame.draw.circle(surface, self.ORANGE, point, 4) 