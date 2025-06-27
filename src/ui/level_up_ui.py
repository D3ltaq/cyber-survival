import pygame
import math

class LevelUpUI:
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
        self.MED_GRAY = (60, 60, 70)
        
        # Fonts
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont("arial", 48)
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
                choice_height = 120
                start_y = (self.screen_height - len(choices) * choice_height) // 2
                
                for i, choice in enumerate(choices):
                    choice_y = start_y + i * choice_height
                    choice_rect = pygame.Rect(self.screen_width // 2 - 250, choice_y, 500, 100)
                    if choice_rect.collidepoint(mouse_x, mouse_y):
                        return choice
        elif event.type == pygame.MOUSEMOTION:
            # Highlight upgrade under mouse
            mouse_x, mouse_y = event.pos
            choice_height = 120
            start_y = (self.screen_height - len(choices) * choice_height) // 2
            
            for i, choice in enumerate(choices):
                choice_y = start_y + i * choice_height
                choice_rect = pygame.Rect(self.screen_width // 2 - 250, choice_y, 500, 100)
                if choice_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_index = i
                    break
        
        return None
    
    def draw(self, surface, level_system, choices):
        """Draw the level up screen"""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(self.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Title
        pulse = math.sin(self.pulse_timer) * 0.3 + 0.7
        title_color = (int(self.CYAN[0] * pulse),
                      int(self.CYAN[1] * pulse),
                      int(self.CYAN[2] * pulse))
        
        title_text = f"LEVEL {level_system.level}!"
        title_surface = self.font_large.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Choose an upgrade:"
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 150))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Upgrade choices
        choice_height = 120
        start_y = (self.screen_height - len(choices) * choice_height) // 2
        
        for i, choice_id in enumerate(choices):
            upgrade_info = level_system.get_upgrade_info(choice_id)
            if not upgrade_info:
                continue
            
            choice_y = start_y + i * choice_height
            is_selected = (i == self.selected_index)
            
            self.draw_upgrade_choice(surface, upgrade_info, choice_y, is_selected)
        
        # Instructions
        instructions = [
            "↑↓ / WS: Navigate",
            "Enter / Space / Click: Select"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.font_small.render(instruction, True, self.MED_GRAY)
            inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, 
                                                     self.screen_height - 80 + i * 25))
            surface.blit(inst_surface, inst_rect)
    
    def draw_upgrade_choice(self, surface, upgrade_info, y, is_selected):
        """Draw a single upgrade choice"""
        choice_width = 500
        choice_height = 100
        choice_x = self.screen_width // 2 - choice_width // 2
        
        # Background
        bg_color = self.MED_GRAY if is_selected else self.DARK_PURPLE
        border_color = self.ELECTRIC_BLUE if is_selected else self.MED_GRAY
        border_width = 3 if is_selected else 1
        
        choice_rect = pygame.Rect(choice_x, y, choice_width, choice_height)
        pygame.draw.rect(surface, bg_color, choice_rect)
        pygame.draw.rect(surface, border_color, choice_rect, border_width)
        
        # Type icon
        icon_x = choice_x + 20
        icon_y = y + 20
        icon_size = 60
        
        self.draw_upgrade_icon(surface, upgrade_info, icon_x, icon_y, icon_size)
        
        # Text content
        text_x = icon_x + icon_size + 15
        text_y = y + 15
        
        # Name
        name_color = self.MINT_GREEN if upgrade_info["type"] == "passive" else \
                    self.HOT_PINK if upgrade_info["type"] == "weapon_upgrade" or upgrade_info["type"] == "weapon_new" else \
                    self.ELECTRIC_BLUE
        
        name_surface = self.font_medium.render(upgrade_info["name"], True, name_color)
        surface.blit(name_surface, (text_x, text_y))
        
        # Description
        desc_surface = self.font_small.render(upgrade_info["description"], True, self.WHITE)
        surface.blit(desc_surface, (text_x, text_y + 30))
        
        # Level indicator
        current_level = upgrade_info["current_level"]
        max_level = upgrade_info["max_level"]
        if max_level > 1:
            level_text = f"Level {current_level + 1}/{max_level}"
            level_surface = self.font_small.render(level_text, True, self.CYAN)
            surface.blit(level_surface, (text_x, text_y + 55))
    
    def draw_upgrade_icon(self, surface, upgrade_info, x, y, size):
        """Draw an icon representing the upgrade type"""
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Background circle
        pygame.draw.circle(surface, self.BLACK, (center_x, center_y), size // 2)
        
        upgrade_type = upgrade_info["type"]
        upgrade_id = upgrade_info["upgrade_id"]
        
        if upgrade_type == "weapon_upgrade" or upgrade_type == "weapon_new":
            color = self.HOT_PINK
            if "rapid" in upgrade_id:
                # Clock/speed symbol
                pygame.draw.circle(surface, color, (center_x, center_y), size // 3, 3)
                pygame.draw.line(surface, color, (center_x, center_y), 
                               (center_x, center_y - size // 4), 3)
                pygame.draw.line(surface, color, (center_x, center_y), 
                               (center_x + size // 6, center_y), 2)
            elif "double" in upgrade_id or "spread" in upgrade_id:
                # Multiple projectiles
                for i in range(3):
                    offset = (i - 1) * 8
                    pygame.draw.circle(surface, color, (center_x + offset, center_y), 4)
            elif "piercing" in upgrade_id:
                # Arrow through target
                pygame.draw.line(surface, color, 
                               (center_x - size // 3, center_y), 
                               (center_x + size // 3, center_y), 4)
                pygame.draw.polygon(surface, color, [
                    (center_x + size // 3, center_y),
                    (center_x + size // 4, center_y - 6),
                    (center_x + size // 4, center_y + 6)
                ])
            elif "explosive" in upgrade_id:
                # Explosion symbol
                for angle in range(0, 360, 45):
                    end_x = center_x + math.cos(math.radians(angle)) * size // 4
                    end_y = center_y + math.sin(math.radians(angle)) * size // 4
                    pygame.draw.line(surface, color, (center_x, center_y), 
                                   (end_x, end_y), 2)
        
        elif upgrade_type == "passive":
            color = self.MINT_GREEN
            if "health" in upgrade_id:
                # Cross symbol
                pygame.draw.line(surface, color, 
                               (center_x - size // 4, center_y), 
                               (center_x + size // 4, center_y), 4)
                pygame.draw.line(surface, color, 
                               (center_x, center_y - size // 4), 
                               (center_x, center_y + size // 4), 4)
            elif "speed" in upgrade_id:
                # Speed lines
                for i in range(3):
                    y_offset = (i - 1) * 6
                    pygame.draw.line(surface, color, 
                                   (center_x - size // 3, center_y + y_offset), 
                                   (center_x + size // 4, center_y + y_offset), 3)
            elif "damage" in upgrade_id:
                # Sword/blade
                pygame.draw.polygon(surface, color, [
                    (center_x, center_y - size // 3),
                    (center_x + 4, center_y + size // 4),
                    (center_x - 4, center_y + size // 4)
                ])
            elif "regen" in upgrade_id:
                # Heart
                pygame.draw.circle(surface, color, (center_x - 4, center_y - 2), 6)
                pygame.draw.circle(surface, color, (center_x + 4, center_y - 2), 6)
                pygame.draw.polygon(surface, color, [
                    (center_x - 10, center_y + 2),
                    (center_x, center_y + 12),
                    (center_x + 10, center_y + 2)
                ])
            elif "shield" in upgrade_id:
                # Shield
                pygame.draw.arc(surface, color, 
                              pygame.Rect(center_x - size//3, center_y - size//3, 
                                         size//1.5, size//1.5), 
                              0, math.pi, 4)
                pygame.draw.line(surface, color, 
                               (center_x - size//3, center_y), 
                               (center_x + size//3, center_y), 4)
        
        elif upgrade_type == "utility":
            color = self.ELECTRIC_BLUE
            if "area" in upgrade_id:
                # Explosion/area effect
                pygame.draw.circle(surface, color, (center_x, center_y), size // 3, 3)
                pygame.draw.circle(surface, color, (center_x, center_y), size // 5, 2)
            elif "time" in upgrade_id:
                # Clock with emphasis
                pygame.draw.circle(surface, color, (center_x, center_y), size // 3, 3)
                for angle in range(0, 360, 90):
                    end_x = center_x + math.cos(math.radians(angle)) * size // 4
                    end_y = center_y + math.sin(math.radians(angle)) * size // 4
                    pygame.draw.circle(surface, color, (int(end_x), int(end_y)), 2)
        
        # Border
        pygame.draw.circle(surface, color, (center_x, center_y), size // 2, 2) 