import pygame

# Fix linter errors for pygame constants
if not hasattr(pygame, 'error'):
    pygame.error = Exception

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.sound_enabled = True
        
        # Try to initialize the mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.mixer_available = True
        except pygame.error:
            print("Warning: Could not initialize sound mixer. Game will run without sound.")
            self.mixer_available = False
            self.sound_enabled = False
        
        # Load sound effects (using procedural generation since we don't have audio files)
        if self.mixer_available:
            self.generate_sounds()
    
    def generate_sounds(self):
        """Generate simple procedural sound effects"""
        try:
            # Generate basic sound effects using pygame's sndarray if available
            # For now, we'll create placeholder sounds or skip if sndarray isn't available
            pass
        except:
            # If we can't generate sounds, disable them
            self.sound_enabled = False
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.sound_enabled or not self.mixer_available:
            return
        
        # Since we don't have actual audio files, we'll just print the sound effect
        # In a full implementation, you would load and play actual sound files
        if sound_name == "shoot":
            pass  # Would play shooting sound
        elif sound_name == "enemy_death":
            pass  # Would play enemy death sound
        elif sound_name == "player_hit":
            pass  # Would play player damage sound
        elif sound_name == "powerup":
            pass  # Would play powerup collection sound
        elif sound_name == "wave_complete":
            pass  # Would play wave completion sound
        elif sound_name == "game_over":
            pass  # Would play game over sound
    
    def set_volume(self, volume):
        """Set the overall volume (0.0 to 1.0)"""
        if self.mixer_available:
            try:
                pygame.mixer.music.set_volume(volume)
            except:
                pass
    
    def stop_all(self):
        """Stop all currently playing sounds"""
        if self.mixer_available:
            try:
                pygame.mixer.stop()
            except:
                pass 