import pygame
import math
import random
from src.entities.player import Player
from src.entities.enemy import Enemy, EnemySpawner
from src.entities.projectile import Projectile
from src.entities.powerup import PowerUp
from src.ui.ui import UI
from src.systems.particle import ParticleSystem
from src.systems.sound_manager import SoundManager
from src.core.level_system import LevelSystem, XPOrb
from src.ui.level_up_ui import LevelUpUI
from src.ui.main_menu import MainMenu
from src.ui.cheat_menu import CheatMenu

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
    pygame.K_c = 99
    pygame.SRCALPHA = 65536

class Game:
    def __init__(self):
        # Screen settings
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Cyber Survival")
        
        # World settings (larger than screen)
        self.WORLD_WIDTH = 4800   # 4x screen width
        self.WORLD_HEIGHT = 3200  # 4x screen height
        
        # Load background map
        try:
            self.background_map = pygame.image.load("assets/pixel_art_map.png").convert()
            print("Background map loaded successfully!")
        except pygame.error:
            print("Could not load assets/pixel_art_map.png, using simple background")
            self.background_map = None
        
        # Camera system
        self.camera_x = 0
        self.camera_y = 0
        self.camera_smooth = 0.15  # Camera smoothing factor (increased for more responsiveness)
        
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
        
        # Visual enhancement variables
        self.background_animation_timer = 0
        self.grid_pulse_timer = 0
        self.screen_flash_timer = 0
        self.screen_flash_color = self.WHITE
        self.screen_distortion = 0
        
        # Game objects
        self.player = Player(self.WORLD_WIDTH // 2, self.WORLD_HEIGHT // 2)
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.xp_orbs = []
        self.enemy_spawner = EnemySpawner(self.WORLD_WIDTH, self.WORLD_HEIGHT)
        
        # Game systems
        self.particle_system = ParticleSystem()
        self.ui = UI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.sound_manager = SoundManager()
        self.level_system = LevelSystem()
        self.level_up_ui = LevelUpUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.main_menu = MainMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.cheat_menu = CheatMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Wave system - Enhanced for horde mode
        self.current_wave = 1
        self.base_enemies_per_wave = 15  # Increased base count for horde feel
        self.enemies_in_wave = self.base_enemies_per_wave
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.wave_timer = 0
        self.wave_break_duration = 2000  # Reduced to 2 seconds for faster pacing
        self.in_wave_break = False
        self.is_boss_wave = False
        self.boss_notification_timer = 0
        self.boss_notification_duration = 3000  # 3 seconds to show boss warning
        
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
                elif event.key == pygame.K_c and self.game_state == "playing":
                    self.game_state = "cheat_menu"
            
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
            
            # Handle cheat menu input
            elif self.game_state == "cheat_menu":
                cheat_action = self.cheat_menu.handle_input(event)
                if cheat_action:
                    self.handle_cheat_action(cheat_action)
                    if cheat_action[1] == "action" and cheat_action[2] == "exit":
                        self.game_state = "playing"
    
    def update(self, dt):
        if self.game_state == "playing":
            self.update_game_logic(dt)
        
    def update_game_logic(self, dt):
        # Update visual timers
        self.background_animation_timer += dt
        self.grid_pulse_timer += dt
        self.screen_flash_timer = max(0, self.screen_flash_timer - dt)
        self.screen_distortion = max(0, self.screen_distortion - dt * 0.01)
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt, self.WORLD_WIDTH, self.WORLD_HEIGHT)
        
        # Update camera to follow player
        self.update_camera()
        
        # Handle player shooting
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            new_projectiles = self.player.shoot(self.camera_x, self.camera_y)
            for projectile in new_projectiles:
                self.projectiles.add(projectile)
            if new_projectiles:
                self.sound_manager.play_sound("shoot")
        
        # Limit total projectiles to prevent performance issues
        max_projectiles = 150  # Reasonable limit for performance
        
        # Handle auto-targeting system
        # Only allow auto-targeting if we haven't hit projectile limit
        if len(self.projectiles) < max_projectiles:
            # Count existing auto-targeting projectiles
            auto_projectiles = sum(1 for proj in self.projectiles if hasattr(proj, 'weapon_type') and proj.weapon_type == "auto_targeting")
            max_auto_projectiles = 20  # Limit auto-targeting projectiles specifically
            
            if auto_projectiles < max_auto_projectiles:
                auto_shot = self.player.get_auto_target_shot(self.enemies)
                if auto_shot:
                    self.projectiles.add(auto_shot)
                    self.sound_manager.play_sound("shoot")
        
        # Handle passive weapon attacks
        if len(self.projectiles) < max_projectiles:
            passive_attacks = self.player.get_passive_attacks()
            for attack in passive_attacks:
                if len(self.projectiles) < max_projectiles:  # Check again before each attack
                    self.handle_passive_attack(attack)
        
        # Spawn enemies - Enhanced for horde mode
        if not self.in_wave_break and self.enemies_spawned < self.enemies_in_wave:
            if self.enemy_spawner.should_spawn(dt):
                enemy = self.enemy_spawner.spawn_enemy(self.current_wave, self.player.rect.center)
                if enemy:
                    # Handle group spawning (especially for swarm enemies)
                    spawn_count = self.enemy_spawner.get_spawn_count_for_type(enemy.enemy_type, self.current_wave)
                    
                    # Add the main enemy
                    self.enemies.add(enemy)
                    self.enemies_spawned += 1
                    
                    # Add additional enemies for group spawning
                    for i in range(1, min(spawn_count, self.enemies_in_wave - self.enemies_spawned + 1)):
                        # Spawn additional enemies nearby
                        offset_x = random.randint(-50, 50)
                        offset_y = random.randint(-50, 50)
                        spawn_x, spawn_y = self.enemy_spawner.get_spawn_position(self.player.rect.center)
                        additional_enemy = Enemy(spawn_x + offset_x, spawn_y + offset_y, enemy.enemy_type, self.current_wave)
                        self.enemies.add(additional_enemy)
                        self.enemies_spawned += 1
                        
                        if self.enemies_spawned >= self.enemies_in_wave:
                            break
        
        # Update enemies and handle shooting
        for enemy in self.enemies:
            enemy.update(dt, self.player.rect.center)
            
            # Update enemy shooting timer
            if hasattr(enemy, 'shoot_timer'):
                enemy.shoot_timer = max(0, enemy.shoot_timer - dt)
            
            # Handle enemy shooting
            if hasattr(enemy, 'can_shoot') and enemy.can_shoot:
                if enemy.can_shoot_at_player(self.player.rect.center):
                    enemy_projectile = enemy.shoot_at_player(self.player.rect.center)
                    if enemy_projectile:
                        self.projectiles.add(enemy_projectile)
        
        # Update projectiles
        projectiles_to_remove = []
        for projectile in self.projectiles:
            projectile.update(dt)
            # Remove projectiles that are off-world bounds (with buffer) or marked for removal
            buffer = 100
            if (projectile.rect.x < -buffer or projectile.rect.x > self.WORLD_WIDTH + buffer or
                projectile.rect.y < -buffer or projectile.rect.y > self.WORLD_HEIGHT + buffer):
                projectiles_to_remove.append(projectile)
        
        # Remove projectiles safely
        for projectile in projectiles_to_remove:
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
    
    def update_camera(self):
        """Update camera position to follow player smoothly"""
        # Target camera position (center player on screen)
        target_x = self.player.rect.centerx - self.SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - self.SCREEN_HEIGHT // 2
        
        # Keep camera within world bounds
        target_x = max(0, min(target_x, self.WORLD_WIDTH - self.SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.WORLD_HEIGHT - self.SCREEN_HEIGHT))
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * self.camera_smooth
        self.camera_y += (target_y - self.camera_y) * self.camera_smooth
    
    def update_wave_system(self, dt):
        # Handle boss notification timer
        if self.boss_notification_timer > 0:
            self.boss_notification_timer -= dt
            if self.boss_notification_timer <= 0:
                self.in_wave_break = True
                self.wave_timer = 0
        
        if self.in_wave_break:
            self.wave_timer += dt
            if self.wave_timer >= self.wave_break_duration:
                self.start_next_wave()
        else:
            # Check if wave is complete
            enemies_count = len(self.enemies)
            if self.enemies_spawned >= self.enemies_in_wave and enemies_count == 0:
                print(f"Wave {self.current_wave} complete! All {self.enemies_in_wave} enemies defeated.")
                self.complete_wave()
    
    def start_next_wave(self):
        self.in_wave_break = False
        self.wave_timer = 0
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.boss_notification_timer = 0
        
        # Calculate enemies for this wave (horde progression)
        # More enemies each wave, with boss waves having different counts
        self.is_boss_wave = (self.current_wave % 5 == 0) and self.current_wave >= 5
        
        if self.is_boss_wave:
            # Boss waves have fewer total enemies but include powerful bosses
            self.enemies_in_wave = max(8, int(self.base_enemies_per_wave * 0.6 + (self.current_wave - 1) * 1.5))
        else:
            # Regular waves scale up more aggressively for horde feel
            self.enemies_in_wave = int(self.base_enemies_per_wave + (self.current_wave - 1) * 4)
        
        # Update enemy spawner for new wave
        self.enemy_spawner.update_spawn_rate(self.current_wave)
        self.enemy_spawner.reset_boss_flag()
        
        print(f"Starting Wave {self.current_wave} {'(BOSS WAVE!) ' if self.is_boss_wave else ''}with {self.enemies_in_wave} enemies")
        
    def complete_wave(self):
        old_wave = self.current_wave
        self.current_wave += 1
        
        # Check if next wave is a boss wave
        next_is_boss_wave = (self.current_wave % 5 == 0) and self.current_wave >= 5
        
        if next_is_boss_wave:
            # Start boss notification period
            self.boss_notification_timer = self.boss_notification_duration
            self.in_wave_break = False  # Don't go into normal wave break yet
        else:
            self.in_wave_break = True
            self.wave_timer = 0
        
        # Give score bonus (increased for later waves)
        base_bonus = 100
        wave_multiplier = max(1.0, 1.0 + (old_wave - 1) * 0.2)
        boss_multiplier = 2.0 if (old_wave % 5 == 0) and old_wave >= 5 else 1.0
        wave_bonus = int(base_bonus * wave_multiplier * boss_multiplier)
        self.score += wave_bonus
        
        print(f"WAVE {old_wave} COMPLETED! Next wave: {self.current_wave}")
        print(f"Score bonus: +{wave_bonus}. Total score: {self.score}")
        
        if next_is_boss_wave:
            print("⚠️  BOSS WAVE INCOMING! ⚠️")
        
        # Chance to spawn powerup (higher chance after boss waves)
        powerup_chance = 0.5 if (old_wave % 5 == 0) and old_wave >= 5 else 0.3
        if random.random() < powerup_chance:
            powerup = PowerUp(
                random.randint(50, self.SCREEN_WIDTH - 50),
                random.randint(50, self.SCREEN_HEIGHT - 50)
            )
            self.powerups.add(powerup)
            print("Powerup spawned!")
        
        self.sound_manager.play_sound("wave_complete")
    
    def check_collisions(self):
        # Separate player and enemy projectiles
        player_projectiles = []
        enemy_projectiles = []
        
        for projectile in list(self.projectiles):
            if hasattr(projectile, 'is_enemy') and projectile.is_enemy:
                enemy_projectiles.append(projectile)
            else:
                player_projectiles.append(projectile)
        
        # Enemy projectiles vs Player collisions
        projectiles_to_remove = []
        for projectile in enemy_projectiles:
            if self.player.rect.colliderect(projectile.rect):
                if self.player.can_take_damage():
                    self.player.take_damage(projectile.damage)
                    self.add_camera_shake(8)
                    self.sound_manager.play_sound("player_hit")
                    
                    # Create damage particles
                    self.particle_system.create_explosion(
                        self.player.rect.centerx, self.player.rect.centery,
                        self.HOT_PINK, 6
                    )
                
                projectiles_to_remove.append(projectile)
        
        # Player projectiles vs Enemy collisions
        for projectile in player_projectiles:
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
                    enemy_type_values = {
                        "basic": 1, "fast": 2, "tank": 3, "sniper": 3, 
                        "swarm": 1, "heavy": 4, "elite": 4, "boss": 5
                    }
                    type_multiplier = enemy_type_values.get(enemy.enemy_type, 1)
                    xp_value = 5 + (type_multiplier * 2)  # Different XP per enemy type
                    xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, xp_value)
                    self.xp_orbs.append(xp_orb)
                    
                    self.enemies.remove(enemy)
                    self.enemies_killed += 1
                    self.total_kills += 1
                    self.score += enemy.score_value
                    
                    # Create enhanced death particles
                    self.particle_system.create_death_explosion(
                        enemy.rect.centerx, enemy.rect.centery, enemy.enemy_type
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
                                enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "sniper": 3, "swarm": 1, "heavy": 4, "elite": 4, "boss": 5}
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
                projectiles_to_remove.append(projectile)
        
        # Remove projectiles safely after iteration
        for projectile in projectiles_to_remove:
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)
        
        # Player vs Enemy collisions
        hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)  # type: ignore
        for enemy in hit_enemies:
            if self.player.can_take_damage():
                self.player.take_damage(enemy.damage)
                self.add_camera_shake(10)
                self.sound_manager.play_sound("player_hit")
                self.add_screen_distortion(2.0)
                
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
    
    def add_screen_flash(self, color, duration=200):
        """Add a screen flash effect for dramatic moments"""
        self.screen_flash_color = color
        self.screen_flash_timer = duration
    
    def add_screen_distortion(self, intensity=1.0):
        """Add screen distortion effect"""
        self.screen_distortion = max(self.screen_distortion, intensity)
    
    def draw(self):
        # Clear screen with dark background
        self.screen.fill(self.DARK_PURPLE)
        
        # Draw background map or fallback to grid
        self.draw_background()
        
        # Calculate total offset (camera + shake)
        total_offset_x = -self.camera_x + self.shake_offset_x
        total_offset_y = -self.camera_y + self.shake_offset_y
        
        # Draw enemies with camera offset
        for enemy in self.enemies:
            screen_x = enemy.rect.x + total_offset_x
            screen_y = enemy.rect.y + total_offset_y
            # Only draw if on screen (with buffer)
            if (-50 < screen_x < self.SCREEN_WIDTH + 50 and 
                -50 < screen_y < self.SCREEN_HEIGHT + 50):
                # Create temporary rect for drawing
                temp_rect = pygame.Rect(screen_x, screen_y, enemy.rect.width, enemy.rect.height)
                original_rect = enemy.rect
                enemy.rect = temp_rect
                enemy.draw(self.screen)
                enemy.rect = original_rect
        
        # Draw projectiles with camera offset
        for projectile in self.projectiles:
            screen_x = projectile.rect.x + total_offset_x
            screen_y = projectile.rect.y + total_offset_y
            # Only draw if on screen (with buffer)
            if (-50 < screen_x < self.SCREEN_WIDTH + 50 and 
                -50 < screen_y < self.SCREEN_HEIGHT + 50):
                # Calculate screen center position
                screen_center_x = projectile.rect.centerx + total_offset_x
                screen_center_y = projectile.rect.centery + total_offset_y
                projectile.draw(self.screen, (screen_center_x, screen_center_y), (total_offset_x, total_offset_y))
        
        # Draw powerups with camera offset
        for powerup in self.powerups:
            screen_x = powerup.rect.x + total_offset_x
            screen_y = powerup.rect.y + total_offset_y
            if (-50 < screen_x < self.SCREEN_WIDTH + 50 and 
                -50 < screen_y < self.SCREEN_HEIGHT + 50):
                temp_rect = pygame.Rect(screen_x, screen_y, powerup.rect.width, powerup.rect.height)
                original_rect = powerup.rect
                powerup.rect = temp_rect
                powerup.draw(self.screen)
                powerup.rect = original_rect
        
        # Draw XP orbs with camera offset
        for orb in self.xp_orbs:
            orb_rect = orb.get_rect()
            screen_x = orb_rect.x + total_offset_x
            screen_y = orb_rect.y + total_offset_y
            if (-50 < screen_x < self.SCREEN_WIDTH + 50 and 
                -50 < screen_y < self.SCREEN_HEIGHT + 50):
                # Temporarily modify orb position for drawing
                original_x, original_y = orb.x, orb.y
                orb.x = orb.x + total_offset_x
                orb.y = orb.y + total_offset_y
                orb.draw(self.screen)
                orb.x, orb.y = original_x, original_y
        
        # Draw player with camera offset
        player_screen_x = self.player.rect.x + total_offset_x
        player_screen_y = self.player.rect.y + total_offset_y
        temp_rect = pygame.Rect(player_screen_x, player_screen_y, self.player.rect.width, self.player.rect.height)
        original_rect = self.player.rect
        self.player.rect = temp_rect
        self.player.draw(self.screen)
        # Draw passive weapons with modified player position
        self.player.draw_passive_weapons(self.screen)
        self.player.rect = original_rect
        
        # Draw particles with camera offset
        for particle in self.particle_system.particles:
            # Temporarily modify particle position for drawing
            original_x, original_y = particle.x, particle.y
            particle.x = particle.x + total_offset_x
            particle.y = particle.y + total_offset_y
            particle.draw(self.screen)
            particle.x, particle.y = original_x, original_y
        
        # Draw UI (not affected by camera)
        enemies_remaining = len(self.enemies)
        self.ui.draw(self.screen, self.player, self.current_wave, self.score, 
                    enemies_remaining, self.in_wave_break, 
                    self.wave_timer, self.wave_break_duration, self.level_system,
                    self.camera_x, self.camera_y, self.boss_notification_timer, self.is_boss_wave)
        
        # Draw world bounds indicator
        self.draw_world_bounds(total_offset_x, total_offset_y)
        
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
        elif self.game_state == "cheat_menu":
            self.cheat_menu.draw(self.screen)
        
        # Apply screen effects
        self.apply_screen_effects()
    
    def apply_screen_effects(self):
        """Apply post-processing screen effects"""
        # Screen flash effect
        if self.screen_flash_timer > 0:
            flash_alpha = int(255 * (self.screen_flash_timer / 200))
            flash_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(self.screen_flash_color)
            self.screen.blit(flash_surface, (0, 0))
        
        # Simple screen shake effect instead of distortion
        if self.screen_distortion > 0:
            # Just add more camera shake instead of complex distortion
            self.add_camera_shake(int(self.screen_distortion * 5))
    
    def draw_background(self):
        """Draw the background map or fallback to grid"""
        if self.background_map:
            # Calculate camera offset for background
            total_offset_x = -self.camera_x + self.shake_offset_x
            total_offset_y = -self.camera_y + self.shake_offset_y
            
            # Create a rect for the visible portion of the background
            source_rect = pygame.Rect(
                max(0, -total_offset_x),  # Source x
                max(0, -total_offset_y),  # Source y
                min(self.SCREEN_WIDTH, self.background_map.get_width() + total_offset_x),  # Source width
                min(self.SCREEN_HEIGHT, self.background_map.get_height() + total_offset_y)  # Source height
            )
            
            # Destination rect on screen
            dest_rect = pygame.Rect(
                max(0, total_offset_x),  # Dest x
                max(0, total_offset_y),  # Dest y
                source_rect.width,       # Dest width
                source_rect.height       # Dest height
            )
            
            # Only draw if there's something to draw
            if source_rect.width > 0 and source_rect.height > 0:
                self.screen.blit(self.background_map, dest_rect, source_rect)
        else:
            # Fallback to simple grid
            self.draw_world_grid()
    
    def draw_world_grid(self):
        """Draw a grid that shows the world coordinates (fallback)"""
        grid_size = 100  # Larger grid for better visibility
        grid_color = (self.CYAN[0]//6, self.CYAN[1]//6, self.CYAN[2]//6)  # Dimmer grid
        
        # Calculate grid offset based on camera position
        offset_x = int(self.camera_x) % grid_size
        offset_y = int(self.camera_y) % grid_size
        
        # Draw vertical lines
        for x in range(-offset_x, self.SCREEN_WIDTH + grid_size, grid_size):
            if 0 <= x <= self.SCREEN_WIDTH:
                pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.SCREEN_HEIGHT), 1)
        
        # Draw horizontal lines  
        for y in range(-offset_y, self.SCREEN_HEIGHT + grid_size, grid_size):
            if 0 <= y <= self.SCREEN_HEIGHT:
                pygame.draw.line(self.screen, grid_color, (0, y), (self.SCREEN_WIDTH, y), 1)
    
    def draw_world_bounds(self, offset_x, offset_y):
        """Draw indicators showing the world boundaries"""
        border_color = self.HOT_PINK
        border_width = 3
        
        # Calculate world bounds on screen
        world_left = 0 + offset_x
        world_right = self.WORLD_WIDTH + offset_x
        world_top = 0 + offset_y
        world_bottom = self.WORLD_HEIGHT + offset_y
        
        # Draw world boundary lines if they're visible on screen
        if -border_width <= world_left <= self.SCREEN_WIDTH + border_width:
            pygame.draw.line(self.screen, border_color, 
                           (world_left, max(0, world_top)), 
                           (world_left, min(self.SCREEN_HEIGHT, world_bottom)), border_width)
        
        if -border_width <= world_right <= self.SCREEN_WIDTH + border_width:
            pygame.draw.line(self.screen, border_color,
                           (world_right, max(0, world_top)), 
                           (world_right, min(self.SCREEN_HEIGHT, world_bottom)), border_width)
        
        if -border_width <= world_top <= self.SCREEN_HEIGHT + border_width:
            pygame.draw.line(self.screen, border_color,
                           (max(0, world_left), world_top), 
                           (min(self.SCREEN_WIDTH, world_right), world_top), border_width)
        
        if -border_width <= world_bottom <= self.SCREEN_HEIGHT + border_width:
            pygame.draw.line(self.screen, border_color,
                           (max(0, world_left), world_bottom), 
                           (min(self.SCREEN_WIDTH, world_right), world_bottom), border_width)
    
    def draw_pause_screen(self):
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((15, 20, 25))  # DARK_BG
        self.screen.blit(overlay, (0, 0))
        
        # Title frame
        self.draw_hex_frame(self.SCREEN_WIDTH // 2, 200, 350, 100)
        
        # Title with glow effect
        font_large = pygame.font.Font(None, 72)
        title_text = "SYSTEM PAUSED"
        title_surface = font_large.render(title_text, True, (0, 255, 255))  # CYAN_BRIGHT
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
        
        # Glow effect
        glow_surface = font_large.render(title_text, True, (0, 150, 180))  # CYAN_DARK
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_surface, title_rect)
        
        # Menu items with cyberpunk panels
        font_medium = pygame.font.Font(None, 48)
        start_y = self.SCREEN_HEIGHT // 2 - 20
        item_height = 80
        
        for i, item in enumerate(self.pause_menu_items):
            is_selected = (i == self.pause_selected_index)
            item_y = start_y + i * item_height
            
            # Panel dimensions
            panel_width = 400
            panel_height = 60
            panel_x = self.SCREEN_WIDTH // 2 - panel_width // 2
            panel_rect = pygame.Rect(panel_x, item_y - 30, panel_width, panel_height)
            
            # Colors based on selection
            if is_selected:
                bg_color = (25, 35, 45)  # PANEL_BG
                border_color = (0, 255, 255)  # CYAN_BRIGHT
                text_color = (0, 255, 255)  # CYAN_BRIGHT
                accent_color = (255, 165, 0)  # ORANGE
            else:
                bg_color = (10, 20, 30)  # Darker panel
                border_color = (60, 85, 110)  # BORDER_LIGHT
                text_color = (255, 255, 255)  # WHITE
                accent_color = (120, 120, 120)  # GRAY_MID
            
            # Draw panel with angled corners
            self.draw_angled_panel(panel_rect, bg_color, border_color)
            
            # Selection indicators
            if is_selected:
                # Left indicator
                left_points = [
                    (panel_rect.left - 20, item_y),
                    (panel_rect.left - 5, item_y - 8),
                    (panel_rect.left - 5, item_y + 8)
                ]
                pygame.draw.polygon(self.screen, accent_color, left_points)
                
                # Right indicator
                right_points = [
                    (panel_rect.right + 20, item_y),
                    (panel_rect.right + 5, item_y - 8),
                    (panel_rect.right + 5, item_y + 8)
                ]
                pygame.draw.polygon(self.screen, accent_color, right_points)
            
            # Text
            item_surface = font_medium.render(item, True, text_color)
            item_text_rect = item_surface.get_rect(center=panel_rect.center)
            self.screen.blit(item_surface, item_text_rect)
        
        # Controls hint panel
        hint_panel = pygame.Rect(self.SCREEN_WIDTH // 2 - 250, self.SCREEN_HEIGHT - 80, 500, 40)
        self.draw_angled_panel(hint_panel, (25, 35, 45), (60, 85, 110))
        
        font_small = pygame.font.Font(None, 24)
        hint_text = "↑↓ / WS: Navigate    Enter / Space / Click: Select    ESC: Resume"
        hint_surface = font_small.render(hint_text, True, (180, 180, 180))  # GRAY_LIGHT
        hint_rect = hint_surface.get_rect(center=hint_panel.center)
        self.screen.blit(hint_surface, hint_rect)
    
    def draw_angled_panel(self, rect, bg_color, border_color):
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
        pygame.draw.polygon(self.screen, bg_color, points)
        
        # Draw the border
        pygame.draw.polygon(self.screen, border_color, points, 2)
    
    def draw_hex_frame(self, center_x, center_y, width, height):
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
        pygame.draw.polygon(self.screen, (25, 35, 45), hex_points)  # PANEL_BG
        pygame.draw.polygon(self.screen, (0, 200, 220), hex_points, 3)  # CYAN_MID
        
        # Corner accents
        for i, point in enumerate(hex_points):
            pygame.draw.circle(self.screen, (255, 165, 0), point, 4)  # ORANGE
    
    def draw_game_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((15, 20, 25))  # DARK_BG
        self.screen.blit(overlay, (0, 0))
        
        # Title frame
        self.draw_hex_frame(self.SCREEN_WIDTH // 2, 200, 400, 100)
        
        # Title with glow effect
        font_large = pygame.font.Font(None, 72)
        title_text = "SYSTEM FAILURE"
        title_surface = font_large.render(title_text, True, (255, 50, 50))  # RED_BRIGHT
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
        
        # Glow effect
        glow_surface = font_large.render(title_text, True, (150, 30, 30))  # Darker red
        for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_surface, title_rect)
        
        # Stats panel
        stats_panel = pygame.Rect(self.SCREEN_WIDTH // 2 - 250, 280, 500, 200)
        self.draw_angled_panel(stats_panel, (25, 35, 45), (200, 100, 255))  # PANEL_BG, PURPLE_BRIGHT
        
        # Stats content
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # Final score
        score_label = font_small.render("FINAL SCORE", True, (200, 100, 255))  # PURPLE_BRIGHT
        self.screen.blit(score_label, (stats_panel.x + 30, stats_panel.y + 30))
        
        score_value = font_medium.render(f"{self.score:,}", True, (255, 255, 255))  # WHITE
        self.screen.blit(score_value, (stats_panel.x + 30, stats_panel.y + 60))
        
        # Wave reached
        wave_label = font_small.render("WAVE REACHED", True, (0, 255, 255))  # CYAN_BRIGHT
        self.screen.blit(wave_label, (stats_panel.x + 30, stats_panel.y + 110))
        
        wave_value = font_medium.render(f"{self.current_wave}", True, (255, 255, 255))  # WHITE
        self.screen.blit(wave_value, (stats_panel.x + 30, stats_panel.y + 140))
        
        # Restart instruction panel
        restart_panel = pygame.Rect(self.SCREEN_WIDTH // 2 - 200, self.SCREEN_HEIGHT - 120, 400, 60)
        self.draw_angled_panel(restart_panel, (25, 35, 45), (255, 165, 0))  # PANEL_BG, ORANGE
        
        restart_text = "Press R to restart mission"
        restart_surface = font_small.render(restart_text, True, (255, 165, 0))  # ORANGE
        restart_rect = restart_surface.get_rect(center=restart_panel.center)
        self.screen.blit(restart_surface, restart_rect)
    
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
    
    def handle_cheat_action(self, action):
        """Handle cheat menu actions"""
        name, action_type, action_value = action
        
        print(f"Cheat activated: {name}")
        
        if action_type == "weapon":
            self.player.current_weapon = action_value
            print(f"Weapon changed to: {action_value}")
        
        elif action_type == "upgrade":
            # Apply upgrade through level system
            if self.level_system.apply_upgrade(action_value):
                self.player.apply_level_upgrade(action_value, self.level_system)
                print(f"Upgrade applied: {action_value}")
        
        elif action_type == "powerup":
            duration = 30000  # 30 seconds
            self.player.apply_powerup(action_value, duration)
            print(f"Powerup applied: {action_value} for 30 seconds")
        
        elif action_type == "cheat":
            if action_value == "full_health":
                actual_max_health = self.player.max_health + getattr(self.player, 'max_health_bonus', 0)
                self.player.health = actual_max_health
                print("Health restored to full")
            
            elif action_value == "god_mode":
                self.cheat_menu.god_mode_active = not self.cheat_menu.god_mode_active
                if self.cheat_menu.god_mode_active:
                    self.player.health = 99999  # Effectively infinite
                    print("God mode activated")
                else:
                    actual_max_health = self.player.max_health + getattr(self.player, 'max_health_bonus', 0)
                    self.player.health = actual_max_health
                    print("God mode deactivated")
            
            elif action_value == "max_upgrades":
                # Apply all upgrades to max level
                for upgrade_id in self.level_system.available_upgrades:
                    max_level = self.level_system.available_upgrades[upgrade_id]["max_level"]
                    for _ in range(max_level):
                        if self.level_system.apply_upgrade(upgrade_id):
                            self.player.apply_level_upgrade(upgrade_id, self.level_system)
                print("All upgrades maxed out!")
            
            elif action_value == "add_xp":
                self.level_system.add_xp(1000)
                print("Added 1000 XP")
            
            elif action_value == "level_up":
                if self.level_system.level_up():
                    self.trigger_level_up()
                print("Triggered level up")
            
            elif action_value == "add_score":
                self.score += 10000
                print("Added 10000 score")
            
            elif action_value == "wave_5":
                self.current_wave = 5
                self.start_next_wave()
                print("Jumped to wave 5")
            
            elif action_value == "wave_10":
                self.current_wave = 10
                self.start_next_wave()
                print("Jumped to wave 10")
            
            elif action_value == "clear_enemies":
                self.enemies.empty()
                print("All enemies cleared")
            
            elif action_value == "spawn_basic":
                for i in range(10):
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        "basic",
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned 10 basic enemies")
            
            elif action_value == "spawn_fast":
                for i in range(5):
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        "fast",
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned 5 fast enemies")
            
            elif action_value == "spawn_tank":
                for i in range(3):
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        "tank",
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned 3 tank enemies")
            
            elif action_value == "spawn_swarm":
                for i in range(5):
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        "swarm",
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned 5 swarm enemies")
            
            elif action_value == "spawn_sniper":
                for i in range(2):
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        "sniper",
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned 2 sniper enemies")
            
            elif action_value == "spawn_heavy":
                for i in range(2):
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        "heavy",
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned 2 heavy enemies")
            
            elif action_value == "spawn_elite":
                enemy = Enemy(
                    random.randint(50, self.SCREEN_WIDTH - 50),
                    random.randint(50, self.SCREEN_HEIGHT - 50),
                    "elite",
                    self.current_wave
                )
                self.enemies.add(enemy)
                print("Spawned 1 elite enemy")
            
            elif action_value == "spawn_boss":
                enemy = Enemy(
                    self.SCREEN_WIDTH // 2,
                    self.SCREEN_HEIGHT // 2,
                    "boss",
                    self.current_wave
                )
                self.enemies.add(enemy)
                print("Spawned 1 boss enemy")
            
            elif action_value == "spawn_mixed":
                enemy_types = ["basic", "fast", "tank", "sniper", "swarm", "heavy", "elite", "boss"]
                for enemy_type in enemy_types:
                    enemy = Enemy(
                        random.randint(50, self.SCREEN_WIDTH - 50),
                        random.randint(50, self.SCREEN_HEIGHT - 50),
                        enemy_type,
                        self.current_wave
                    )
                    self.enemies.add(enemy)
                print("Spawned mixed enemy wave (all types)")
            
            elif action_value == "spawn_powerup":
                powerup = PowerUp(
                    random.randint(50, self.SCREEN_WIDTH - 50),
                    random.randint(50, self.SCREEN_HEIGHT - 50)
                )
                self.powerups.add(powerup)
                print("Spawned powerup")
            
            elif action_value == "clear_powerups":
                self.powerups.empty()
                print("All powerups cleared")
            
            elif action_value == "reset_player":
                # Reset player to initial state
                player_x, player_y = self.player.rect.center
                self.player = Player(player_x, player_y)
                print("Player reset to initial state")
            
            elif action_value == "camera_shake":
                self.add_camera_shake(50)
                print("Big camera shake!")
        
        elif action_type == "action":
            if action_value == "exit":
                print("Exiting cheat menu")
    
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
                    enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "sniper": 3, "swarm": 1, "heavy": 4, "elite": 4, "boss": 5}
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
                        enemy_type_values = {"basic": 1, "fast": 2, "tank": 3, "sniper": 3, "swarm": 1, "heavy": 4, "elite": 4, "boss": 5}
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
                
                # Check which menu item was clicked (coordinates match drawing code)
                start_y = self.SCREEN_HEIGHT // 2 - 20
                item_height = 80
                
                for i, item in enumerate(self.pause_menu_items):
                    item_y = start_y + i * item_height
                    # Panel dimensions match drawing code
                    panel_width = 400
                    panel_height = 60
                    panel_x = self.SCREEN_WIDTH // 2 - panel_width // 2
                    item_rect = pygame.Rect(panel_x, item_y - 30, panel_width, panel_height)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        self.pause_selected_index = i
                        self.handle_pause_selection()
                        break
        elif event.type == pygame.MOUSEMOTION:
            # Highlight menu item under mouse (coordinates match drawing code)
            mouse_x, mouse_y = event.pos
            start_y = self.SCREEN_HEIGHT // 2 - 20
            item_height = 80
            
            for i, item in enumerate(self.pause_menu_items):
                item_y = start_y + i * item_height
                # Panel dimensions match drawing code
                panel_width = 400
                panel_height = 60
                panel_x = self.SCREEN_WIDTH // 2 - panel_width // 2
                item_rect = pygame.Rect(panel_x, item_y - 30, panel_width, panel_height)
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