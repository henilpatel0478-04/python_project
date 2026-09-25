"""
Snack Attack! - Arcade Snake & Snack Game in Python
Entry point script.
"""
import os
import sys
import traceback

# Center the game window on user's screen
os.environ["SDL_VIDEO_CENTERED"] = "1"

import pygame
from game import Game

def create_window_icon() -> pygame.Surface:
    """Create a crisp 32x32 icon for the Windows taskbar and titlebar."""
    icon_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Red apple icon
    pygame.draw.circle(icon_surf, (220, 30, 40), (16, 18), 12)
    pygame.draw.circle(icon_surf, (255, 120, 130), (12, 14), 4)
    # Green leaf & stem
    pygame.draw.line(icon_surf, (95, 55, 20), (16, 8), (17, 3), 2)
    pygame.draw.polygon(icon_surf, (60, 200, 50), [(17, 6), (25, 3), (21, 10)])
    return icon_surf

def main():
    try:
        # Initialize pygame
        pygame.init()
        
        # Set taskbar icon
        try:
            icon = create_window_icon()
            pygame.display.set_icon(icon)
        except Exception:
            pass

        # Start game engine
        print("Starting Snack Attack!...")
        game = Game()
        game.run()
        print("Game closed gracefully.")
    except Exception as e:
        print("\n" + "=" * 50)
        print("AN ERROR OCCURRED WHILE RUNNING THE GAME:")
        print("=" * 50)
        traceback.print_exc()
        print("=" * 50)
        try:
            input("\nPress Enter to exit...")
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
