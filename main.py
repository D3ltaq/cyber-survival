#!/usr/bin/env python3
"""
Cyber Survival - Main Entry Point

A cyberpunk-themed wave-based survival game built with Python and Pygame.
"""

import sys
import os
import pygame

# Add src directory to Python path so we can import from it
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Now import the game
from src.core.game import Game

def main():
    pygame.init()  # pylint: disable=no-member
    game = Game()
    game.run()
    pygame.quit()  # pylint: disable=no-member
    sys.exit()

if __name__ == "__main__":
    main() 