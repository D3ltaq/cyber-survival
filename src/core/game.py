import pygame
import math
import random
from entities.player import Player
from entities.enemy import Enemy, EnemySpawner
from entities.projectile import Projectile
from entities.powerup import PowerUp
from ui.ui import UI
from systems.particle import ParticleSystem
from systems.sound_manager import SoundManager
from core.level_system import LevelSystem, XPOrb
from ui.level_up_ui import LevelUpUI
from ui.main_menu import MainMenu

# Fix linter errors for pygame constants
if not hasattr(pygame, 'QUIT'):
    pygame.QUIT = 256
    pygame.KEYDOWN = 768
    pygame.MOUSEBUTTONDOWN = 1025
    pygame.MOUSEMOTION = 1024
    pygame.K_ESCAPE = 27
    pygame.K_SPACE = 32
    pygame.K_RETURN = 13
    pygame.K_UP = 273
    pygame.K_DOWN = 274
    pygame.K_LEFT = 276
    pygame.K_RIGHT = 275
    pygame.K_w = 119
    pygame.K_s = 115
    pygame.K_a = 97
    pygame.K_d = 100
    pygame.K_r = 114

class Game:
    def __init__(self):
        # Screen settings
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Cyber Survival")
        
        # Game settings
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True
        self.game_state = "main_menu"  # main_menu, playing, paused, game_over, level_up, controls
        
        # Colors (New palette from user)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.MINT_GREEN = (108, 255, 222)  # Light mint from top left
        self.CYAN = (108, 222, 255)        # Bright cyan
        self.ELECTRIC_BLUE = (108, 178, 255)  # Electric blue
        self.ROYAL_BLUE = (108, 134, 255)   # Royal blue
        self.DEEP_BLUE = (56, 89, 178)      # Deep blue from palette
        self.PURPLE = (134, 108, 255)       # Purple
        self.VIOLET = (178, 108, 255)       # Violet
        self.MAGENTA = (222, 108, 255)      # Bright magenta
        self.HOT_PINK = (255, 108, 222)     # Hot pink
        self.CORAL = (255, 134, 178)        # Coral/salmon
        self.DARK_PURPLE = (44, 26, 89)     # Dark background purple
        
        # Game objects
        self.player = Player(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.xp_orbs = []
        self.enemy_spawner = EnemySpawner(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Game systems
        self.particle_system = ParticleSystem()
        self.ui = UI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.sound_manager = SoundManager()
        self.level_system = LevelSystem()
        self.level_up_ui = LevelUpUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.main_menu = MainMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Wave system
        self.current_wave = 1
        self.enemies_in_wave = 10
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.wave_timer = 0
        self.wave_break_duration = 3000  # 3 seconds between waves
        self.in_wave_break = False
        
        # Game stats
        self.score = 0
        self.total_kills = 0
        
        # Camera shake
        self.camera_shake = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Level up system
        self.level_up_choices = []
        self.selected_upgrade = None
        
        # Pause menu
        self.pause_selected_index = 0
        self.pause_menu_items = ["RESUME", "RESTART", "MAIN MENU", "QUIT"]
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "level_up":
                        # Can't escape level up screen
                        pass
                    elif self.game_state == "controls":
                        self.game_state = "main_menu"
                elif event.key == pygame.K_r and self.game_state == "game_over":
                    self.restart_game()
            
            # Handle main menu input
            if self.game_state == "main_menu":
                action = self.main_menu.handle_input(event)
                if action == "START GAME":
                    self.restart_game()
                    self.game_state = "playing"
                elif action == "CONTROLS":
                    self.game_state = "controls"
                elif action == "QUIT":
                    self.running = False
            
            # Handle controls screen input
            elif self.game_state == "controls":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_state = "main_menu"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.game_state = "main_menu"
            
            # Handle pause menu input
            elif self.game_state == "paused":
                self.handle_pause_input(event)
            
            # Handle level up screen input
            elif self.game_state == "level_up":
                selected_upgrade = self.level_up_ui.handle_input(event, self.level_up_choices)
                if selected_upgrade:
                    self.apply_level_upgrade(selected_upgrade)
                    self.game_state = "playing"
    
    def update(self, dt):
        if self.game_state == "playing":
            self.update_game_logic(dt)
        
    def update_game_logic(self, dt):
        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Handle player shooting
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            new_projectiles = self.player.shoot()
            for projectile in new_projectiles:
                self.projectiles.add(projectile)
            if new_projectiles:
                self.sound_manager.play_sound("shoot")
        
        # Handle auto-targeting system
        auto_shot = self.player.get_auto_target_shot(self.enemies)
        if auto_shot:
            self.projectiles.add(auto_shot)
            self.sound_manager.play_sound("shoot")
        
        # Handle passive weapon attacks
        passive_attacks = self.player.get_passive_attacks()
        for attack in passive_attacks:
            self.handle_passive_attack(attack)
        
        # Spawn enemies
        if not self.in_wave_break and self.enemies_spawned < self.enemies_in_wave:
            if self.enemy_spawner.should_spawn(dt):
                enemy = self.enemy_spawner.spawn_enemy(self.current_wave, self.player.rect.center)
                if enemy:
                    self.enemies.add(enemy)
                    self.enemies_spawned += 1
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.rect.center)
        
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
            # Remove projectiles that are off-screen
            if (projectile.rect.x < -50 or projectile.rect.x > self.SCREEN_WIDTH + 50 or
                projectile.rect.y < -50 or projectile.rect.y > self.SCREEN_HEIGHT + 50):
                self.projectiles.remove(projectile)
        
        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)
        
        # Update XP orbs
        magnet_range = 50
        if self.level_system.has_upgrade("xp_magnet"):
            magnet_range = 50 + (self.level_system.get_upgrade_level("xp_magnet") * 30)
        
        for orb in self.xp_orbs[:]:  # Use slice copy for safe iteration
            if not orb.update(dt, (self.player.rect.centerx, self.player.rect.centery), magnet_range):
                self.xp_orbs.remove(orb)
        
        # Check XP collection
        player_rect = pygame.Rect(self.player.rect.x - 10, self.player.rect.y - 10, 
                                self.player.rect.width + 20, self.player.rect.height + 20)
        for orb in self.xp_orbs[:]:
            if player_rect.colliderect(orb.get_rect()):
                self.xp_orbs.remove(orb)
                if self.level_system.add_xp(orb.value):
                    self.trigger_level_up()
        
        # Check area damage
        area_damage, area_radius = self.player.get_area_damage_info()
        if area_damage and area_radius:
            self.handle_area_damage(area_damage, area_radius)
        
        # Check energy shuriken collisions
        if self.player.energy_shuriken_level > 0:
            self.check_shuriken_collisions()
        
        # Check collisions
        self.check_collisions()
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Update wave system AFTER all collisions are processed
        self.update_wave_system(dt)
        
        # Update camera shake
        if self.camera_shake > 0:
            self.camera_shake -= dt * 5
            intensity = min(self.camera_shake, 10)
            intensity = max(1, int(intensity))  # Ensure minimum intensity of 1
            self.shake_offset_x = random.randint(-intensity, intensity)
            self.shake_offset_y = random.randint(-intensity, intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        # Check if player is dead
        if self.player.health <= 0:
            self.game_state = "game_over"
            self.sound_manager.play_sound("game_over")
    
    def update_wave_system(self, dt):
        if self.in_wave_break:
            self.wave_timer += dt
            if self.wave_timer >= self.wave_break_duration:
                self.start_next_wave()
        else:
            # Check if wave is complete
            enemies_count = len(self.enemies)
            if self.enemies_spawned >= self.enemies_in_wave and enemies_count == 0:
                self.complete_wave()
    
    def start_next_wave(self):
        self.in_wave_break = False
        self.wave_timer = 0
        self.enemies_spawned = 0
        self.enemies_killed = 0
        
        # Increase difficulty
        self.enemies_in_wave = int(10 + (self.current_wave - 1) * 3)
        self.enemy_spawner.increase_difficulty()
        
    def complete_wave(self):
        self.current_wave += 1
        self.in_wave_break = True
        self.wave_timer = 0
        
        # Give score bonus
        wave_bonus = self.current_wave * 100
        self.score += wave_bonus
        
        # Chance to spawn powerup
        if random.random() < 0.3:  # 30% chance
            powerup = PowerUp(
                random.randint(50, self.SCREEN_WIDTH - 50),
                random.randint(50, self.SCREEN_HEIGHT - 50)
            )
            self.powerups.add(powerup)
        
        self.sound_manager.play_sound("wave_complete")
    
    def check_collisions(self):
        # Projectile vs Enemy collisions
        for projectile in self.projectiles:
            hit_enemies = pygame.sprite.spritecollide(projectile, self.enemies, False)
            enemies_hit_this_frame = []
            
            for enemy in hit_enemies:
                # Skip if piercing projectile already hit this enemy
                if projectile.piercing and id(enemy) in projectile.pierced_enemies:
                    continue
                
                enemy.take_damage(projectile.damage)
                enemies_hit_this_frame.append(enemy)
                
                # Track pierced enemies
                if projectile.piercing:
                    projectile.pierced_enemies.add(id(enemy))
                
                # Create hit particles
                self.particle_system.create_explosion(
                    enemy.rect.centerx, enemy.rect.centery, 
                    self.ELECTRIC_BLUE, 5
                )
                
                # Check if enemy is dead
                if enemy.health <= 0:
                    # Drop XP orb
                    enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "boss": 5}
                    type_multiplier = enemy_type_values.get(enemy.enemy_type, 1)
                    xp_value = 5 + (type_multiplier * 2)  # Different XP per enemy type
                    xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, xp_value)
                    self.xp_orbs.append(xp_orb)
                    
                    self.enemies.remove(enemy)
                    self.enemies_killed += 1
                    self.total_kills += 1
                    self.score += enemy.score_value
                    
                    # Create death particles
                    self.particle_system.create_explosion(
                        enemy.rect.centerx, enemy.rect.centery,
                        self.HOT_PINK, 15
                    )
                    
                    self.sound_manager.play_sound("enemy_death")
                    self.add_camera_shake(5)
            
            # Handle explosive projectiles
            if enemies_hit_this_frame and projectile.explosive:
                # Explosion affects nearby enemies
                explosion_radius = 60
                for hit_enemy in enemies_hit_this_frame:
                    explosion_center = (hit_enemy.rect.centerx, hit_enemy.rect.centery)
                    
                    for enemy in self.enemies:
                        if enemy in enemies_hit_this_frame:
                            continue  # Already hit by direct impact
                        
                        dx = enemy.rect.centerx - explosion_center[0]
                        dy = enemy.rect.centery - explosion_center[1]
                        distance = (dx * dx + dy * dy) ** 0.5
                        
                        if distance <= explosion_radius:
                            explosion_damage = projectile.damage // 2  # Half damage for explosion
                            enemy.take_damage(explosion_damage)
                            
                            # Explosion particles
                            self.particle_system.create_explosion(
                                enemy.rect.centerx, enemy.rect.centery, 
                                self.HOT_PINK, 3
                            )
                            
                            # Check if enemy dies from explosion
                            if enemy.health <= 0:
                                enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "boss": 5}
                                type_multiplier = enemy_type_values.get(enemy.enemy_type, 1)
                                xp_value = 5 + (type_multiplier * 2)
                                xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, xp_value)
                                self.xp_orbs.append(xp_orb)
                                
                                self.enemies.remove(enemy)
                                self.enemies_killed += 1
                                self.total_kills += 1
                                self.score += enemy.score_value
                                
                                self.particle_system.create_explosion(
                                    enemy.rect.centerx, enemy.rect.centery,
                                    self.HOT_PINK, 10
                                )
                    
                    # Big explosion effect
                    self.particle_system.create_explosion(
                        explosion_center[0], explosion_center[1], self.HOT_PINK, 25
                    )
                    self.add_camera_shake(8)
            
            # Remove non-piercing projectiles that hit something
            if enemies_hit_this_frame and not projectile.piercing:
                self.projectiles.remove(projectile)
                break
        
        # Player vs Enemy collisions
        hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)  # type: ignore
        for enemy in hit_enemies:
            if self.player.can_take_damage():
                self.player.take_damage(enemy.damage)
                self.add_camera_shake(10)
                self.sound_manager.play_sound("player_hit")
                
                # Create damage particles
                self.particle_system.create_explosion(
                    self.player.rect.centerx, self.player.rect.centery,
                    self.HOT_PINK, 8
                )
        
        # Player vs PowerUp collisions
        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)  # type: ignore
        for powerup in collected_powerups:
            powerup.apply_effect(self.player)
            self.sound_manager.play_sound("powerup")
    
    def add_camera_shake(self, intensity):
        self.camera_shake = max(self.camera_shake, intensity)
    
    def draw(self):
        # Clear screen with dark background
        self.screen.fill(self.DARK_PURPLE)
        
        # Draw grid background (cyberpunk style)
        self.draw_grid()
        
        # Apply camera shake offset
        offset_x = self.shake_offset_x
        offset_y = self.shake_offset_y
        
        # Draw game objects with offset
        temp_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        temp_surface.fill(self.DARK_PURPLE)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(temp_surface)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(temp_surface)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(temp_surface)
        
        # Draw XP orbs
        for orb in self.xp_orbs:
            orb.draw(temp_surface)
        
        # Draw player
        self.player.draw(temp_surface)
        
        # Draw passive weapon effects
        self.player.draw_passive_weapons(temp_surface)
        
        # Draw particles
        self.particle_system.draw(temp_surface)
        
        # Apply the offset and blit to main screen
        self.screen.blit(temp_surface, (offset_x, offset_y))
        
        # Draw UI (not affected by camera shake)
        self.ui.draw(self.screen, self.player, self.current_wave, self.score, 
                    self.enemies_in_wave - self.enemies_spawned, self.in_wave_break, 
                    self.wave_timer, self.wave_break_duration, self.level_system)
        
        # Draw game state overlays
        if self.game_state == "main_menu":
            self.main_menu.draw(self.screen)
        elif self.game_state == "controls":
            self.main_menu.draw_controls_screen(self.screen)
        elif self.game_state == "paused":
            self.draw_pause_screen()
        elif self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "level_up":
            self.level_up_ui.draw(self.screen, self.level_system, self.level_up_choices)
    
    def draw_grid(self):
        grid_size = 50
        for x in range(0, self.SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, (self.CYAN[0]//4, self.CYAN[1]//4, self.CYAN[2]//4), 
                           (x, 0), (x, self.SCREEN_HEIGHT), 1)
        for y in range(0, self.SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, (self.CYAN[0]//4, self.CYAN[1]//4, self.CYAN[2]//4), 
                           (0, y), (self.SCREEN_WIDTH, y), 1)
    
    def draw_pause_screen(self):
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        font_large = pygame.font.Font(None, 72)
        title_text = font_large.render("GAME PAUSED", True, self.ELECTRIC_BLUE)
        title_rect = title_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(title_text, title_rect)
        
        # Menu items
        font_medium = pygame.font.Font(None, 48)
        start_y = self.SCREEN_HEIGHT // 2 - 50
        item_height = 60
        
        for i, item in enumerate(self.pause_menu_items):
            is_selected = (i == self.pause_selected_index)
            
            # Colors
            if is_selected:
                text_color = self.CYAN
                bg_color = (60, 60, 70)
                border_color = self.CYAN
            else:
                text_color = self.WHITE
                bg_color = (30, 30, 40)
                border_color = (60, 60, 70)
            
            # Background
            item_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, start_y + i * item_height - 20, 300, 50)
            pygame.draw.rect(self.screen, bg_color, item_rect)
            pygame.draw.rect(self.screen, border_color, item_rect, 2)
            
            # Text
            item_surface = font_medium.render(item, True, text_color)
            item_text_rect = item_surface.get_rect(center=(self.SCREEN_WIDTH // 2, start_y + i * item_height))
            self.screen.blit(item_surface, item_text_rect)
            
            # Selection arrows
            if is_selected:
                pygame.draw.polygon(self.screen, self.CYAN, [
                    (self.SCREEN_WIDTH // 2 - 180, start_y + i * item_height),
                    (self.SCREEN_WIDTH // 2 - 165, start_y + i * item_height - 8),
                    (self.SCREEN_WIDTH // 2 - 165, start_y + i * item_height + 8)
                ])
                pygame.draw.polygon(self.screen, self.CYAN, [
                    (self.SCREEN_WIDTH // 2 + 180, start_y + i * item_height),
                    (self.SCREEN_WIDTH // 2 + 165, start_y + i * item_height - 8),
                    (self.SCREEN_WIDTH // 2 + 165, start_y + i * item_height + 8)
                ])
        
        # Controls hint
        font_small = pygame.font.Font(None, 24)
        hint_text = "↑↓ / WS: Navigate    Enter / Space / Click: Select    ESC: Resume"
        hint_surface = font_small.render(hint_text, True, (120, 120, 120))
        hint_rect = hint_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))
        self.screen.blit(hint_surface, hint_rect)
    
    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, self.HOT_PINK)
        text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        font_medium = pygame.font.Font(None, 48)
        score_text = font_medium.render(f"Final Score: {self.score}", True, self.ELECTRIC_BLUE)
        score_rect = score_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        wave_text = font_medium.render(f"Wave Reached: {self.current_wave}", True, self.MINT_GREEN)
        wave_rect = wave_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(wave_text, wave_rect)
        
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Press R to restart", True, self.MINT_GREEN)
        restart_rect = restart_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        self.__init__()
        self.game_state = "playing"
    
    def trigger_level_up(self):
        """Trigger the level up screen"""
        self.game_state = "level_up"
        self.level_up_choices = self.level_system.get_available_upgrade_choices(3)
        self.level_up_ui.selected_index = 0
    
    def apply_level_upgrade(self, upgrade_id):
        """Apply the selected upgrade"""
        if self.level_system.apply_upgrade(upgrade_id):
            self.player.apply_level_upgrade(upgrade_id, self.level_system)
    
    def handle_area_damage(self, damage, radius):
        """Handle area damage effect"""
        player_center = (self.player.rect.centerx, self.player.rect.centery)
        
        for enemy in self.enemies:
            enemy_center = (enemy.rect.centerx, enemy.rect.centery)
            dx = enemy_center[0] - player_center[0]
            dy = enemy_center[1] - player_center[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= radius:
                enemy.take_damage(damage)
                
                # Create hit particles
                self.particle_system.create_explosion(
                    enemy.rect.centerx, enemy.rect.centery, 
                    self.ELECTRIC_BLUE, 3
                )
                
                # Check if enemy is dead
                if enemy.health <= 0:
                    # Drop XP
                    enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "boss": 5}
                    type_multiplier = enemy_type_values.get(enemy.enemy_type, 1)
                    xp_value = 5 + (type_multiplier * 2)  # Different XP per enemy type
                    xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, xp_value)
                    self.xp_orbs.append(xp_orb)
                    
                    self.enemies.remove(enemy)
                    self.enemies_killed += 1
                    self.total_kills += 1
                    self.score += enemy.score_value
                    
                    # Create death particles
                    self.particle_system.create_explosion(
                        enemy.rect.centerx, enemy.rect.centery,
                        self.HOT_PINK, 15
                    )
    
    def handle_passive_attack(self, attack):
        """Handle passive weapon attacks like missiles, lasers, etc."""
        import math
        
        if attack["type"] == "missile":
            # Create homing missile
            if self.enemies:
                # Find nearest enemy for homing
                nearest_enemy = None
                min_distance = float('inf')
                
                for enemy in self.enemies:
                    dx = enemy.rect.centerx - attack["x"]
                    dy = enemy.rect.centery - attack["y"]
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        nearest_enemy = enemy
                
                if nearest_enemy:
                    # Calculate angle to target
                    dx = nearest_enemy.rect.centerx - attack["x"]
                    dy = nearest_enemy.rect.centery - attack["y"]
                    angle = math.atan2(dy, dx)
                    
                    # Create homing projectile
                    missile = Projectile(attack["x"], attack["y"], angle, damage=attack["damage"])
                    missile.speed = 400
                    missile.color = self.MAGENTA
                    missile.size = 4
                    self.projectiles.add(missile)
        
        elif attack["type"] == "laser":
            # Continuous laser targeting nearest enemy
            if self.enemies:
                # Find nearest enemy
                nearest_enemy = None
                min_distance = float('inf')
                
                for enemy in self.enemies:
                    dx = enemy.rect.centerx - attack["x"]
                    dy = enemy.rect.centery - attack["y"]
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance < min_distance and distance < 300:  # Range limit
                        min_distance = distance
                        nearest_enemy = enemy
                
                if nearest_enemy:
                    # Calculate angle to target
                    dx = nearest_enemy.rect.centerx - attack["x"]
                    dy = nearest_enemy.rect.centery - attack["y"]
                    angle = math.atan2(dy, dx)
                    
                    # Create laser beam
                    laser = Projectile(attack["x"], attack["y"], angle, damage=attack["damage"])
                    laser.speed = 800
                    laser.color = self.ELECTRIC_BLUE
                    laser.size = 2
                    self.projectiles.add(laser)
        
        elif attack["type"] == "drone_shot":
            # Drone auto-aim shot
            if self.enemies:
                # Find nearest enemy
                nearest_enemy = None
                min_distance = float('inf')
                
                for enemy in self.enemies:
                    dx = enemy.rect.centerx - attack["x"]
                    dy = enemy.rect.centery - attack["y"]
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance < min_distance and distance < 250:  # Range limit
                        min_distance = distance
                        nearest_enemy = enemy
                
                if nearest_enemy:
                    # Calculate angle to target
                    dx = nearest_enemy.rect.centerx - attack["x"]
                    dy = nearest_enemy.rect.centery - attack["y"]
                    angle = math.atan2(dy, dx)
                    
                    # Create drone shot
                    drone_shot = Projectile(attack["x"], attack["y"], angle, damage=attack["damage"])
                    drone_shot.speed = 500
                    drone_shot.color = self.CYAN
                    drone_shot.size = 3
                    self.projectiles.add(drone_shot)
    
    def check_shuriken_collisions(self):
        """Check collisions for orbiting energy shuriken"""
        import math
        center_x, center_y = self.player.rect.center
        
        for i in range(self.player.energy_shuriken_level):
            angle = self.player.shuriken_angle + (i * 2 * math.pi / self.player.energy_shuriken_level)
            radius = 40 + (i * 10)
            shuriken_x = center_x + math.cos(angle) * radius
            shuriken_y = center_y + math.sin(angle) * radius
            
            # Create a collision rectangle for the shuriken
            shuriken_rect = pygame.Rect(shuriken_x - 8, shuriken_y - 8, 16, 16)
            
            # Check collisions with enemies
            for enemy in list(self.enemies):  # Convert to list for safe iteration
                if shuriken_rect.colliderect(enemy.rect) and id(enemy) not in self.player.shuriken_hit_enemies:
                    damage = 10 * self.player.energy_shuriken_level
                    enemy.take_damage(damage)
                    self.player.shuriken_hit_enemies.add(id(enemy))  # Prevent multiple hits
                    
                    # Create hit particles
                    self.particle_system.create_explosion(
                        enemy.rect.centerx, enemy.rect.centery, 
                        self.CYAN, 3
                    )
                    
                    # Check if enemy is dead
                    if enemy.health <= 0:
                        # Drop XP orb
                        enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "boss": 5}
                        type_multiplier = enemy_type_values.get(enemy.enemy_type, 1)
                        xp_value = 5 + (type_multiplier * 2)
                        xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, xp_value)
                        self.xp_orbs.append(xp_orb)
                        
                        self.enemies.remove(enemy)
                        self.enemies_killed += 1
                        self.total_kills += 1
                        self.score += enemy.score_value
                        
                        # Create death particles
                        self.particle_system.create_explosion(
                            enemy.rect.centerx, enemy.rect.centery,
                            self.HOT_PINK, 8
                        )
                        
                        self.sound_manager.play_sound("enemy_death")
    
    def handle_pause_input(self, event):
        """Handle input for pause menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.pause_selected_index = (self.pause_selected_index - 1) % len(self.pause_menu_items)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.pause_selected_index = (self.pause_selected_index + 1) % len(self.pause_menu_items)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.handle_pause_selection()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check which menu item was clicked
                start_y = self.SCREEN_HEIGHT // 2 - 50
                item_height = 60
                
                for i, item in enumerate(self.pause_menu_items):
                    item_y = start_y + i * item_height
                    item_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, item_y - 20, 300, 50)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        self.pause_selected_index = i
                        self.handle_pause_selection()
                        break
        elif event.type == pygame.MOUSEMOTION:
            # Highlight menu item under mouse
            mouse_x, mouse_y = event.pos
            start_y = self.SCREEN_HEIGHT // 2 - 50
            item_height = 60
            
            for i, item in enumerate(self.pause_menu_items):
                item_y = start_y + i * item_height
                item_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, item_y - 20, 300, 50)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    self.pause_selected_index = i
                    break
    
    def handle_pause_selection(self):
        """Handle pause menu selection"""
        selected_item = self.pause_menu_items[self.pause_selected_index]
        
        if selected_item == "RESUME":
            self.game_state = "playing"
        elif selected_item == "RESTART":
            self.restart_game()
            self.game_state = "playing"
        elif selected_item == "MAIN MENU":
            self.game_state = "main_menu"
        elif selected_item == "QUIT":
            self.running = False
    
    def run(self):
        while self.running:
            dt = self.clock.tick(self.FPS)
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            pygame.display.flip() 