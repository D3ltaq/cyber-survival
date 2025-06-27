import pygame
import math

class UI:
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
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont("arial", 48)
            self.font_medium = pygame.font.SysFont("arial", 36)
            self.font_small = pygame.font.SysFont("arial", 24)
    
    def draw(self, surface, player, wave, score, enemies_remaining, in_wave_break, wave_timer, wave_break_duration, level_system=None, camera_x=0.0, camera_y=0.0, boss_notification_timer=0, is_boss_wave=False):
        # Draw health bar
        self.draw_health_bar(surface, player)
        
        # Draw wave info
        self.draw_wave_info(surface, wave, enemies_remaining, in_wave_break, wave_timer, wave_break_duration, boss_notification_timer, is_boss_wave)
        
        # Draw score
        self.draw_score(surface, score)
        
        # Draw level and XP bar
        if level_system:
            self.draw_level_info(surface, level_system)
        
        # Draw power-up indicators
        self.draw_powerup_indicators(surface, player)
        
        # Draw camera position (for debugging)
        self.draw_camera_info(surface, camera_x, camera_y, player)
        
        # Draw controls hint
        self.draw_controls(surface)
    
    def draw_health_bar(self, surface, player):
        # Health bar position
        bar_x = 20
        bar_y = 20
        bar_width = 300
        bar_height = 20
        
        # Background
        pygame.draw.rect(surface, self.BLACK, 
                        pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(surface, self.BLACK, 
                        pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_percentage = player.get_health_percentage()
        health_width = int(bar_width * health_percentage)
        
        # Health bar color based on percentage
        if health_percentage > 0.6:
            health_color = self.MINT_GREEN
        elif health_percentage > 0.3:
            health_color = self.CYAN
        else:
            health_color = self.HOT_PINK
        
        if health_width > 0:
            pygame.draw.rect(surface, health_color, 
                            pygame.Rect(bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, self.WHITE, 
                        pygame.Rect(bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text with shield
        actual_max_health = player.max_health + getattr(player, 'max_health_bonus', 0)
        if hasattr(player, 'shield_current') and player.shield_current > 0:
            health_text = f"HEALTH: {int(player.health)}/{int(actual_max_health)} + {int(player.shield_current)} SHIELD"
        else:
            health_text = f"HEALTH: {int(player.health)}/{int(actual_max_health)}"
        text_surface = self.font_small.render(health_text, True, self.WHITE)
        surface.blit(text_surface, (bar_x, bar_y + bar_height + 5))
    
    def draw_wave_info(self, surface, wave, enemies_remaining, in_wave_break, wave_timer, wave_break_duration, boss_notification_timer=0, is_boss_wave=False):
        # Position in top center
        center_x = self.screen_width // 2
        y = 20
        
        # Handle boss notification
        if boss_notification_timer > 0:
            time_left = boss_notification_timer / 1000.0
            text = f"⚠️ BOSS WAVE {wave} INCOMING IN: {time_left:.1f}s ⚠️"
            color = self.CORAL  # Red warning color
            
            # Add pulsing effect for boss warning
            pulse = abs(int((boss_notification_timer % 500) / 500 * 255))
            color = (min(255, color[0] + pulse//4), color[1], color[2])
            
        elif in_wave_break:
            # Show wave break countdown
            time_left = (wave_break_duration - wave_timer) / 1000.0
            text = f"WAVE {wave} INCOMING IN: {time_left:.1f}s"
            color = self.CYAN
        else:
            # Show current wave and enemies remaining
            wave_type = " (BOSS WAVE)" if is_boss_wave else ""
            text = f"WAVE {wave}{wave_type} - ENEMIES: {enemies_remaining}"
            color = self.CORAL if is_boss_wave else self.ROYAL_BLUE
        
        text_surface = self.font_medium.render(text, True, color)
        text_rect = text_surface.get_rect(center=(center_x, y + 15))
        
        # Background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(surface, self.BLACK, bg_rect)
        pygame.draw.rect(surface, color, bg_rect, 2)
        
        surface.blit(text_surface, text_rect)
    
    def draw_score(self, surface, score):
        # Position in top right
        x = self.screen_width - 20
        y = 20
        
        text = f"SCORE: {score:,}"
        text_surface = self.font_medium.render(text, True, self.MINT_GREEN)
        text_rect = text_surface.get_rect(topright=(x, y))
        
        # Background
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(surface, self.BLACK, bg_rect)
        pygame.draw.rect(surface, self.MINT_GREEN, bg_rect, 2)
        
        surface.blit(text_surface, text_rect)
    
    def draw_powerup_indicators(self, surface, player):
        # Position below health bar
        start_x = 20
        start_y = 70
        indicator_size = 40
        spacing = 50
        
        x_offset = 0
        
        for powerup_type, timer in player.powerup_timers.items():
            if timer > 0:
                # Background
                indicator_rect = pygame.Rect(start_x + x_offset, start_y, indicator_size, indicator_size)
                pygame.draw.rect(surface, self.BLACK, indicator_rect)
                
                # Icon based on type
                center_x = indicator_rect.centerx
                center_y = indicator_rect.centery
                
                if powerup_type == "damage":
                    color = self.HOT_PINK
                    # Draw star
                    self.draw_star(surface, center_x, center_y, 12, color)
                elif powerup_type == "speed":
                    color = self.ELECTRIC_BLUE
                    # Draw lightning
                    self.draw_lightning(surface, center_x, center_y, 12, color)
                
                # Border
                pygame.draw.rect(surface, color, indicator_rect, 2)
                
                # Timer
                time_left = timer / 1000.0
                time_text = f"{time_left:.1f}s"
                text_surface = self.font_small.render(time_text, True, color)
                text_rect = text_surface.get_rect(center=(center_x, center_y + 25))
                surface.blit(text_surface, text_rect)
                
                x_offset += spacing
    
    def draw_star(self, surface, center_x, center_y, size, color):
        # Simple star shape
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size // 2
            
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            points.append((x, y))
        
        pygame.draw.polygon(surface, color, points)
    
    def draw_lightning(self, surface, center_x, center_y, size, color):
        # Simple lightning bolt
        points = [
            (center_x - size//3, center_y - size),
            (center_x + size//6, center_y - size//3),
            (center_x - size//6, center_y - size//3),
            (center_x + size//3, center_y + size),
            (center_x - size//6, center_y + size//3),
            (center_x + size//6, center_y + size//3)
        ]
        pygame.draw.polygon(surface, color, points)
    
    def draw_controls(self, surface):
        # Position in bottom left
        x = 20
        y = self.screen_height - 100
        
        controls = [
            "WASD/Arrows: Move",
            "Mouse/Space: Shoot",
            "ESC: Pause  C: Cheats"
        ]
        
        for i, control in enumerate(controls):
            text_surface = self.font_small.render(control, True, self.WHITE)
            surface.blit(text_surface, (x, y + i * 20))
    
    def draw_level_info(self, surface, level_system):
        """Draw level and XP bar"""
        # Position below score
        x = self.screen_width - 20
        y = 60
        
        # Level text
        level_text = f"LEVEL {level_system.level}"
        level_surface = self.font_medium.render(level_text, True, self.CYAN)
        level_rect = level_surface.get_rect(topright=(x, y))
        
        # Background for level
        bg_rect = level_rect.inflate(10, 5)
        pygame.draw.rect(surface, self.BLACK, bg_rect)
        pygame.draw.rect(surface, self.CYAN, bg_rect, 2)
        
        surface.blit(level_surface, level_rect)
        
        # XP bar
        bar_width = 200
        bar_height = 10
        bar_x = x - bar_width
        bar_y = y + 35
        
        # Background
        pygame.draw.rect(surface, self.BLACK, 
                        pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        
        # XP fill
        xp_progress = level_system.get_xp_progress()
        xp_width = int(bar_width * xp_progress)
        
        if xp_width > 0:
            pygame.draw.rect(surface, self.CYAN, 
                            pygame.Rect(bar_x, bar_y, xp_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, self.WHITE, 
                        pygame.Rect(bar_x, bar_y, bar_width, bar_height), 1)
        
        # XP text
        xp_text = f"XP: {level_system.xp}/{level_system.xp_to_next_level}"
        xp_surface = self.font_small.render(xp_text, True, self.WHITE)
        surface.blit(xp_surface, (bar_x, bar_y + bar_height + 3))
    
    def draw_camera_info(self, surface, camera_x, camera_y, player):
        # Position in bottom right
        x = self.screen_width - 20
        y = self.screen_height - 120
        
        # Camera position text
        camera_text = f"CAMERA: ({camera_x:.0f}, {camera_y:.0f})"
        camera_surface = self.font_small.render(camera_text, True, self.WHITE)
        camera_rect = camera_surface.get_rect(bottomright=(x, y))
        
        # Player position text
        player_text = f"PLAYER: ({player.rect.centerx:.0f}, {player.rect.centery:.0f})"
        player_surface = self.font_small.render(player_text, True, self.CYAN)
        player_rect = player_surface.get_rect(bottomright=(x, y + 20))
        
        # Background for both
        combined_rect = camera_rect.union(player_rect)
        bg_rect = combined_rect.inflate(10, 5)
        pygame.draw.rect(surface, self.BLACK, bg_rect)
        pygame.draw.rect(surface, self.WHITE, bg_rect, 2)
        
        surface.blit(camera_surface, camera_rect)
        surface.blit(player_surface, player_rect) 