import pygame
import math

# Fix linter errors for pygame constants
if not hasattr(pygame, 'KEYDOWN'):
    pygame.KEYDOWN = 768
    pygame.MOUSEBUTTONDOWN = 1025
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

class CheatMenu:
    """Debug/testing menu for quickly accessing all game features"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_index = 0
        self.category_index = 0
        self.scroll_offset = 0
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.MINT_GREEN = (108, 255, 222)
        self.CYAN = (108, 222, 255)
        self.ELECTRIC_BLUE = (108, 178, 255)
        self.ROYAL_BLUE = (108, 134, 255)
        self.PURPLE = (134, 108, 255)
        self.HOT_PINK = (255, 108, 222)
        self.CORAL = (255, 134, 178)
        self.DARK_PURPLE = (44, 26, 89)
        
        # Font setup
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont("arial", 48)
            self.font_medium = pygame.font.SysFont("arial", 36)
            self.font_small = pygame.font.SysFont("arial", 24)
        
        # Cheat categories
        self.categories = {
            "Weapons": [
                ("Default Blaster", "weapon", "default"),
                ("Laser Rifle", "weapon", "laser_rifle"),
                ("Plasma Cannon", "weapon", "plasma_cannon"),
                ("Shotgun", "weapon", "shotgun"),
                ("Sniper Rifle", "weapon", "sniper_rifle"),
                ("Machine Gun", "weapon", "machine_gun"),
                ("Energy Beam", "weapon", "energy_beam"),
            ],
            "Upgrades": [
                ("Rapid Fire", "upgrade", "rapid_fire"),
                ("Double Shot", "upgrade", "double_shot"),
                ("Spread Shot", "upgrade", "spread_shot"),
                ("Piercing Rounds", "upgrade", "piercing_rounds"),
                ("Explosive Rounds", "upgrade", "explosive_rounds"),
                ("Auto-Targeting", "upgrade", "auto_targeting"),
                ("Damage Boost", "upgrade", "damage_boost"),
                ("Speed Boost", "upgrade", "speed_boost"),
                ("Health Boost", "upgrade", "health_boost"),
                ("Regeneration", "upgrade", "regeneration"),
                ("Energy Shield", "upgrade", "shield"),
            ],
            "Passive Weapons": [
                ("Orbital Missiles", "upgrade", "orbital_missiles"),
                ("Energy Shuriken", "upgrade", "energy_shuriken"),
                ("Laser Turret", "upgrade", "laser_turret"),
                ("Combat Drone", "upgrade", "drone_companion"),
                ("Area Damage", "upgrade", "area_damage"),
            ],
            "Powerups": [
                ("Damage Powerup", "powerup", "damage"),
                ("Speed Powerup", "powerup", "speed"),
                ("Health Powerup", "powerup", "health"),
            ],
            "Player Cheats": [
                ("Full Health", "cheat", "full_health"),
                ("God Mode (Toggle)", "cheat", "god_mode"),
                ("Max All Upgrades", "cheat", "max_upgrades"),
                ("Add 1000 XP", "cheat", "add_xp"),
                ("Level Up", "cheat", "level_up"),
                ("Add 10000 Score", "cheat", "add_score"),
            ],
            "Wave Control": [
                ("Skip to Wave 5", "cheat", "wave_5"),
                ("Skip to Wave 10", "cheat", "wave_10"),
                ("Clear All Enemies", "cheat", "clear_enemies"),
                ("Spawn 10 Basic", "cheat", "spawn_basic"),
                ("Spawn 5 Fast", "cheat", "spawn_fast"),
                ("Spawn 3 Tank", "cheat", "spawn_tank"),
                ("Spawn 1 Boss", "cheat", "spawn_boss"),
                ("Spawn Mixed Wave", "cheat", "spawn_mixed"),
            ],
            "Misc": [
                ("Spawn Powerup", "cheat", "spawn_powerup"),
                ("Clear Powerups", "cheat", "clear_powerups"),
                ("Reset Player", "cheat", "reset_player"),
                ("Toggle Particles", "cheat", "toggle_particles"),
                ("Big Camera Shake", "cheat", "camera_shake"),
            ]
        }
        
        self.category_names = list(self.categories.keys())
        self.current_category = self.category_names[0]
        self.god_mode_active = False
        
    def handle_input(self, event):
        """Handle input events and return cheat action if any"""
        if event.type == pygame.KEYDOWN:
            current_items = self.categories[self.current_category]
            
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(current_items)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(current_items)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.category_index = (self.category_index - 1) % len(self.category_names)
                self.current_category = self.category_names[self.category_index]
                self.selected_index = 0
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.category_index = (self.category_index + 1) % len(self.category_names)
                self.current_category = self.category_names[self.category_index]
                self.selected_index = 0
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if current_items:
                    return current_items[self.selected_index]
            elif event.key == pygame.K_ESCAPE:
                return ("Exit Cheats", "action", "exit")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on category tabs
            tab_y = 100
            tab_height = 40
            tab_width = self.screen_width // len(self.category_names)
            
            if 50 <= event.pos[1] <= tab_y + tab_height:
                clicked_category = event.pos[0] // tab_width
                if 0 <= clicked_category < len(self.category_names):
                    self.category_index = clicked_category
                    self.current_category = self.category_names[self.category_index]
                    self.selected_index = 0
            
            # Check if clicking on items
            else:
                start_y = 160
                item_height = 35
                current_items = self.categories[self.current_category]
                
                for i, item in enumerate(current_items):
                    item_y = start_y + i * item_height
                    if item_y <= event.pos[1] <= item_y + item_height:
                        if 50 <= event.pos[0] <= self.screen_width - 50:
                            return item
        
        return None
    
    def draw(self, surface):
        """Draw the cheat menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(self.DARK_PURPLE)
        surface.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("CHEAT MENU / TESTING PAGE", True, self.HOT_PINK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 30))
        surface.blit(title, title_rect)
        
        # Category tabs
        tab_width = self.screen_width // len(self.category_names)
        tab_height = 40
        tab_y = 70
        
        for i, category in enumerate(self.category_names):
            is_selected = (i == self.category_index)
            tab_x = i * tab_width
            
            # Tab background
            tab_color = self.ELECTRIC_BLUE if is_selected else self.ROYAL_BLUE
            border_color = self.CYAN if is_selected else self.WHITE
            
            tab_rect = pygame.Rect(tab_x + 2, tab_y, tab_width - 4, tab_height)
            pygame.draw.rect(surface, tab_color, tab_rect)
            pygame.draw.rect(surface, border_color, tab_rect, 2)
            
            # Tab text
            text_color = self.WHITE if is_selected else self.CYAN
            tab_text = self.font_small.render(category, True, text_color)
            text_rect = tab_text.get_rect(center=(tab_x + tab_width // 2, tab_y + tab_height // 2))
            surface.blit(tab_text, text_rect)
        
        # Current category items
        current_items = self.categories[self.current_category]
        start_y = 130
        item_height = 35
        
        # Category description
        descriptions = {
            "Weapons": "Switch between different weapon types",
            "Upgrades": "Apply permanent upgrades to your character",
            "Passive Weapons": "Activate passive weapon systems",
            "Powerups": "Apply temporary powerup effects",
            "Player Cheats": "Modify player stats and abilities",
            "Wave Control": "Control enemy waves and spawning",
            "Misc": "Various testing and debug functions"
        }
        
        desc_text = self.font_small.render(descriptions.get(self.current_category, ""), True, self.MINT_GREEN)
        desc_rect = desc_text.get_rect(center=(self.screen_width // 2, start_y))
        surface.blit(desc_text, desc_rect)
        
        # Items list
        list_start_y = start_y + 30
        for i, (name, action_type, action_value) in enumerate(current_items):
            is_selected = (i == self.selected_index)
            item_y = list_start_y + i * item_height
            
            # Skip items that would be off-screen
            if item_y > self.screen_height - 100:
                break
            
            # Item background
            item_rect = pygame.Rect(50, item_y, self.screen_width - 100, item_height - 2)
            
            if is_selected:
                pygame.draw.rect(surface, self.CYAN, item_rect)
                text_color = self.BLACK
            else:
                pygame.draw.rect(surface, (40, 40, 60), item_rect)
                text_color = self.WHITE
            
            pygame.draw.rect(surface, self.WHITE, item_rect, 1)
            
            # Item text
            item_text = self.font_medium.render(name, True, text_color)
            text_rect = item_text.get_rect(left=item_rect.left + 10, centery=item_rect.centery)
            surface.blit(item_text, text_rect)
            
            # Action type indicator
            type_colors = {
                "weapon": self.HOT_PINK,
                "upgrade": self.ELECTRIC_BLUE,
                "powerup": self.MINT_GREEN,
                "cheat": self.PURPLE,
                "action": self.CORAL
            }
            
            type_color = type_colors.get(action_type, self.WHITE)
            type_text = self.font_small.render(f"[{action_type.upper()}]", True, type_color)
            type_rect = type_text.get_rect(right=item_rect.right - 10, centery=item_rect.centery)
            surface.blit(type_text, type_rect)
        
        # Status indicators
        status_y = self.screen_height - 120
        
        # God mode indicator
        if self.god_mode_active:
            god_text = self.font_medium.render("GOD MODE ACTIVE", True, self.HOT_PINK)
            god_rect = god_text.get_rect(center=(self.screen_width // 2, status_y))
            
            # Pulsing background
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100 + 50
            pulse_color = (int(pulse), 0, 0)
            bg_rect = god_rect.inflate(20, 10)
            pygame.draw.rect(surface, pulse_color, bg_rect)
            pygame.draw.rect(surface, self.HOT_PINK, bg_rect, 2)
            
            surface.blit(god_text, god_rect)
        
        # Controls help
        controls_y = self.screen_height - 80
        controls = [
            "↑↓/WS: Navigate  ←→/AD: Switch Category",
            "Enter/Space/Click: Activate  ESC: Exit",
            "Use this menu to test all weapons, upgrades, and game features!"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, self.WHITE)
            control_rect = control_text.get_rect(center=(self.screen_width // 2, controls_y + i * 20))
            surface.blit(control_text, control_rect)
        
        return None 