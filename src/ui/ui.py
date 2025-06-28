import pygame
import math

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Cyberpunk color palette (matching other UI elements)
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
        
        # Warning colors
        self.RED_BRIGHT = (255, 50, 50)
        self.YELLOW_BRIGHT = (255, 255, 50)
        
        # Fonts
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
            self.font_tiny = pygame.font.Font(None, 18)
        except:
            self.font_large = pygame.font.SysFont("arial", 48, bold=True)
            self.font_medium = pygame.font.SysFont("arial", 36, bold=True)
            self.font_small = pygame.font.SysFont("arial", 24)
            self.font_tiny = pygame.font.SysFont("arial", 18)
    
    def draw(self, surface, player, wave, score, enemies_remaining, in_wave_break, wave_timer, wave_break_duration, level_system=None, camera_x=0.0, camera_y=0.0, boss_notification_timer=0, is_boss_wave=False):
        # Draw health panel
        self.draw_health_panel(surface, player)
        
        # Draw wave info panel
        self.draw_wave_panel(surface, wave, enemies_remaining, in_wave_break, wave_timer, wave_break_duration, boss_notification_timer, is_boss_wave)
        
        # Draw score panel
        self.draw_score_panel(surface, score)
        
        # Draw level and XP panel
        if level_system:
            self.draw_level_panel(surface, level_system)
        
        # Draw power-up indicators
        self.draw_powerup_panels(surface, player)
        
        # Draw controls panel
        self.draw_controls_panel(surface)
        
        # Draw debug info (if needed)
        # self.draw_debug_panel(surface, camera_x, camera_y, player)
    
    def draw_health_panel(self, surface, player):
        """Draw cyberpunk-style health panel"""
        # Panel dimensions
        panel_width = 320
        panel_height = 80
        panel_x = 20
        panel_y = 20
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, self.BORDER_LIGHT)
        
        # Health label
        label_text = "VITALS"
        label_surface = self.font_small.render(label_text, True, self.CYAN_BRIGHT)
        surface.blit(label_surface, (panel_x + 15, panel_y + 8))
        
        # Health bar
        bar_x = panel_x + 15
        bar_y = panel_y + 30
        bar_width = 250
        bar_height = 15
        
        # Health percentage
        health_percentage = player.get_health_percentage()
        health_width = int(bar_width * health_percentage)
        
        # Health bar background
        bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, self.BLACK, bar_bg_rect)
        pygame.draw.rect(surface, self.BORDER_DARK, bar_bg_rect, 1)
        
        # Health bar fill with gradient effect
        if health_percentage > 0.6:
            health_color = self.CYAN_BRIGHT
        elif health_percentage > 0.3:
            health_color = self.YELLOW_BRIGHT
        else:
            health_color = self.RED_BRIGHT
        
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(surface, health_color, health_rect)
            
            # Add glow effect for low health
            if health_percentage <= 0.3:
                glow_rect = pygame.Rect(bar_x - 2, bar_y - 2, health_width + 4, bar_height + 4)
                pygame.draw.rect(surface, (health_color[0]//4, health_color[1]//4, health_color[2]//4), glow_rect)
        
        # Health text
        actual_max_health = player.max_health + getattr(player, 'max_health_bonus', 0)
        health_text = f"{int(player.health)}/{int(actual_max_health)}"
        health_surface = self.font_small.render(health_text, True, self.WHITE)
        surface.blit(health_surface, (panel_x + 15, panel_y + 50))
        
        # Shield indicator
        if hasattr(player, 'shield_current') and player.shield_current > 0:
            shield_text = f"SHIELD: {int(player.shield_current)}"
            shield_surface = self.font_tiny.render(shield_text, True, self.BLUE_BRIGHT)
            surface.blit(shield_surface, (panel_x + 120, panel_y + 50))
        
        # Status indicators
        status_x = panel_x + 280
        status_y = panel_y + 15
        
        # Critical health warning
        if health_percentage <= 0.25:
            pygame.draw.circle(surface, self.RED_BRIGHT, (status_x, status_y), 8)
            pygame.draw.circle(surface, self.WHITE, (status_x, status_y), 8, 2)
    
    def draw_wave_panel(self, surface, wave, enemies_remaining, in_wave_break, wave_timer, wave_break_duration, boss_notification_timer=0, is_boss_wave=False):
        """Draw cyberpunk-style wave information panel"""
        # Panel dimensions
        panel_width = 400
        panel_height = 60
        panel_x = self.screen_width // 2 - panel_width // 2
        panel_y = 20
        
        # Determine panel color based on state
        if boss_notification_timer > 0:
            border_color = self.RED_BRIGHT
            text_color = self.RED_BRIGHT
        elif is_boss_wave:
            border_color = self.ORANGE
            text_color = self.ORANGE
        elif in_wave_break:
            border_color = self.CYAN_BRIGHT
            text_color = self.CYAN_BRIGHT
        else:
            border_color = self.BLUE_BRIGHT
            text_color = self.BLUE_BRIGHT
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, border_color)
        
        # Wave text
        if boss_notification_timer > 0:
            time_left = boss_notification_timer / 1000.0
            text = f"⚠️ BOSS WAVE {wave} INCOMING: {time_left:.1f}s ⚠️"
        elif in_wave_break:
            time_left = (wave_break_duration - wave_timer) / 1000.0
            text = f"WAVE {wave} INCOMING: {time_left:.1f}s"
        else:
            wave_type = " [BOSS]" if is_boss_wave else ""
            text = f"WAVE {wave}{wave_type} - HOSTILES: {enemies_remaining}"
        
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=panel_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Pulse effect for boss warnings
        if boss_notification_timer > 0:
            pulse_alpha = int(abs(math.sin(boss_notification_timer * 0.01)) * 100)
            pulse_surface = pygame.Surface((panel_width, panel_height))
            pulse_surface.set_alpha(pulse_alpha)
            pulse_surface.fill(self.RED_BRIGHT)
            surface.blit(pulse_surface, (panel_x, panel_y))
    
    def draw_score_panel(self, surface, score):
        """Draw cyberpunk-style score panel"""
        # Panel dimensions
        panel_width = 200
        panel_height = 60
        panel_x = self.screen_width - panel_width - 20
        panel_y = 20
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, self.CYAN_BRIGHT)
        
        # Label
        label_text = "SCORE"
        label_surface = self.font_small.render(label_text, True, self.CYAN_BRIGHT)
        surface.blit(label_surface, (panel_x + 15, panel_y + 8))
        
        # Score value
        score_text = f"{score:,}"
        score_surface = self.font_medium.render(score_text, True, self.WHITE)
        surface.blit(score_surface, (panel_x + 15, panel_y + 28))
    
    def draw_level_panel(self, surface, level_system):
        """Draw cyberpunk-style level and XP panel"""
        # Panel dimensions
        panel_width = 250
        panel_height = 80
        panel_x = self.screen_width - panel_width - 20
        panel_y = 100
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, self.PURPLE_BRIGHT)
        
        # Level label and value
        level_text = f"LEVEL {level_system.level}"
        level_surface = self.font_medium.render(level_text, True, self.PURPLE_BRIGHT)
        surface.blit(level_surface, (panel_x + 15, panel_y + 8))
        
        # XP bar
        bar_x = panel_x + 15
        bar_y = panel_y + 40
        bar_width = 220
        bar_height = 12
        
        # XP progress
        xp_progress = level_system.get_xp_progress()
        xp_width = int(bar_width * xp_progress)
        
        # XP bar background
        bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, self.BLACK, bar_bg_rect)
        pygame.draw.rect(surface, self.BORDER_DARK, bar_bg_rect, 1)
        
        # XP bar fill
        if xp_width > 0:
            xp_rect = pygame.Rect(bar_x, bar_y, xp_width, bar_height)
            pygame.draw.rect(surface, self.PURPLE_BRIGHT, xp_rect)
        
        # XP text
        xp_text = f"XP: {level_system.xp}/{level_system.xp_to_next_level}"
        xp_surface = self.font_tiny.render(xp_text, True, self.WHITE)
        surface.blit(xp_surface, (bar_x, bar_y + bar_height + 3))
    
    def draw_powerup_panels(self, surface, player):
        """Draw cyberpunk-style powerup indicators"""
        start_x = 20
        start_y = 120
        panel_size = 60
        spacing = 70
        
        x_offset = 0
        
        for powerup_type, timer in player.powerup_timers.items():
            if timer > 0:
                # Panel position
                panel_x = start_x + x_offset
                panel_y = start_y
                panel_rect = pygame.Rect(panel_x, panel_y, panel_size, panel_size)
                
                # Determine color based on powerup type
                if powerup_type == "damage":
                    color = self.RED_BRIGHT
                    icon_char = "⚡"
                elif powerup_type == "speed":
                    color = self.BLUE_BRIGHT
                    icon_char = "➤"
                else:
                    color = self.CYAN_BRIGHT
                    icon_char = "●"
                
                # Draw panel
                self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, color)
                
                # Icon
                icon_surface = self.font_large.render(icon_char, True, color)
                icon_rect = icon_surface.get_rect(center=(panel_x + panel_size // 2, panel_y + panel_size // 2 - 5))
                surface.blit(icon_surface, icon_rect)
                
                # Timer
                time_left = timer / 1000.0
                time_text = f"{time_left:.1f}s"
                time_surface = self.font_tiny.render(time_text, True, color)
                time_rect = time_surface.get_rect(center=(panel_x + panel_size // 2, panel_y + panel_size - 8))
                surface.blit(time_surface, time_rect)
                
                x_offset += spacing
    
    def draw_controls_panel(self, surface):
        """Draw cyberpunk-style controls panel"""
        # Panel dimensions
        panel_width = 280
        panel_height = 80
        panel_x = 20
        panel_y = self.screen_height - panel_height - 20
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, self.BORDER_LIGHT)
        
        # Controls text
        controls = [
            "WASD/Arrows: Movement",
            "Mouse/Space: Fire",
            "ESC: Pause  C: Debug"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font_tiny.render(control, True, self.GRAY_LIGHT)
            surface.blit(control_surface, (panel_x + 15, panel_y + 15 + i * 18))
    
    def draw_debug_panel(self, surface, camera_x, camera_y, player):
        """Draw debug information panel"""
        # Panel dimensions
        panel_width = 250
        panel_height = 80
        panel_x = self.screen_width - panel_width - 20
        panel_y = self.screen_height - panel_height - 20
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_angled_panel(surface, panel_rect, self.PANEL_BG, self.GRAY_MID)
        
        # Debug info
        debug_lines = [
            f"Camera: ({camera_x:.0f}, {camera_y:.0f})",
            f"Player: ({player.rect.centerx:.0f}, {player.rect.centery:.0f})",
            f"FPS: {pygame.time.Clock().get_fps():.0f}"
        ]
        
        for i, line in enumerate(debug_lines):
            debug_surface = self.font_tiny.render(line, True, self.GRAY_LIGHT)
            surface.blit(debug_surface, (panel_x + 15, panel_y + 15 + i * 18))
    
    def draw_angled_panel(self, surface, rect, bg_color, border_color):
        """Draw a panel with angled corners using proper clipping"""
        corner_size = 12
        
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