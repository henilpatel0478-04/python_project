"""
Automated headless test script verifying game logic, sound effects,
snack spawners, state transitions, and high-score saving without GUI window.
"""
import os
import sys

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure headless drivers
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from game import Game, GameState
from snack import SnackType

def test_full_game_loop():
    pygame.init()
    game = Game()

    print("Step 1: Checking Initial State...")
    assert game.state == GameState.MENU, f"Expected MENU, got {game.state}"
    assert game.ui.high_score >= 0, "High score should be non-negative"

    print("Step 2: Switching to PLAYING...")
    game._handle_keydown(pygame.K_SPACE)
    assert game.state == GameState.PLAYING, f"Expected PLAYING, got {game.state}"
    assert game.snake is not None, "Snake should be initialized"
    assert game.regular_snack is not None, "Regular snack should be spawned"

    print("Step 3: Simulating 60 frames of gameplay...")
    for _ in range(60):
        game.update(0.016)
        game.draw()

    print("Step 4: Simulating Eating Snacks...")
    initial_score = game.score
    game._eat_snack(game.regular_snack)
    assert game.score > initial_score, "Score must increase after eating"
    assert game.snacks_eaten == 1, "Snacks eaten counter must increment"

    print("Step 5: Testing Chili Pepper Frenzy...")
    from snack import Snack
    chili = Snack(game.snake.head[0], game.snake.head[1], SnackType.CHILI)
    game._eat_snack(chili)
    assert game.snake.is_frenzy, "Snake should be in frenzy state"

    print("Step 6: Testing Pause & Resume...")
    game._handle_keydown(pygame.K_p)
    assert game.state == GameState.PAUSED, "Game should be paused"
    game._handle_keydown(pygame.K_p)
    assert game.state == GameState.PLAYING, "Game should be playing after unpause"

    print("Step 7: Testing Game Over...")
    game._handle_game_over(ate_self=False, hit_wall=True)
    assert game.state == GameState.GAME_OVER, "Game should enter GAME_OVER state"
    game.draw()

    print("Step 8: Testing High Score Persistence...")
    test_score = 999
    game.ui.save_high_score(test_score)
    loaded = game.ui.load_high_score()
    assert loaded == test_score, f"Expected {test_score}, got {loaded}"

    print("All headless tests passed successfully!")
    pygame.quit()

if __name__ == "__main__":
    test_full_game_loop()
