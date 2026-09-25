"""
Core Game Engine coordinating snake, snacks, particle effects,
game loop state transitions, screen shake, and input handling.
"""
import random
import pygame
from sound_effects import SoundManager
from particles import ParticleManager
from snack import Snack, SnackSpawner, SnackType, SNACK_DATA
from snake import Snake, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
from ui import UIManager

class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

DIFFICULTIES = {
    "Easy": {"speed": 8.0, "name": "Easy (Chill)"},
    "Normal": {"speed": 12.0, "name": "Normal (Classic)"},
    "Hard": {"speed": 16.0, "name": "Hard (Speedy)"},
    "Insane": {"speed": 21.0, "name": "Insane (Frenzy)"},
}

class Game:
    def __init__(self):
        # Display settings
        self.cols = 28
        self.rows = 22
        self.cell_size = 30
        self.grid_width = self.cols * self.cell_size   # 840
        self.grid_height = self.rows * self.cell_size # 660

        self.hud_height = 68
        self.margin_x = 30
        self.margin_y = self.hud_height + 20
        self.window_width = self.grid_width + self.margin_x * 2  # 900
        self.window_height = self.margin_y + self.grid_height + 25 # 773

        # Pygame setup
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snack Attack! - Arcade Snake Game")
        self.clock = pygame.time.Clock()
        self.running = True

        # Systems
        self.sound = SoundManager()
        self.particles = ParticleManager()
        self.ui = UIManager(self.window_width, self.window_height, self.hud_height)
        self.spawner = SnackSpawner(self.cols, self.rows)

        # Options
        self.difficulty_names = list(DIFFICULTIES.keys())
        self.difficulty_idx = 1  # Normal
        self.wrap_walls = False

        # State machine
        self.state = GameState.MENU
        self.total_time = 0.0

        # In-game variables
        self.snake = None
        self.regular_snack = None
        self.bonus_snack = None
        self.score = 0
        self.snacks_eaten = 0
        self.move_accumulator = 0.0
        self.bonus_spawn_timer = 15.0
        self.is_new_high_score = False

        # Screen shake
        self.shake_time = 0.0
        self.shake_intensity = 0.0

    @property
    def current_difficulty(self) -> str:
        return self.difficulty_names[self.difficulty_idx]

    @property
    def base_speed(self) -> float:
        return DIFFICULTIES[self.current_difficulty]["speed"]

    def reset_game(self):
        """Initializes a fresh game round."""
        start_x = self.cols // 3
        start_y = self.rows // 2
        self.snake = Snake(start_x, start_y, length=4)
        self.score = 0
        self.snacks_eaten = 0
        self.move_accumulator = 0.0
        self.bonus_spawn_timer = random.uniform(14.0, 22.0)
        self.bonus_snack = None
        self.is_new_high_score = False
        self.shake_time = 0.0
        self.particles.clear()

        # Spawn first regular snack
        self.regular_snack = self.spawner.spawn_regular(set(self.snake.body))

    def trigger_shake(self, duration: float = 0.3, intensity: float = 6.0):
        self.shake_time = duration
        self.shake_intensity = intensity

    def cycle_difficulty(self):
        self.difficulty_idx = (self.difficulty_idx + 1) % len(self.difficulty_names)
        self.sound.play("click")

    def toggle_walls(self):
        self.wrap_walls = not self.wrap_walls
        self.sound.play("click")

    def toggle_sound(self):
        self.sound.toggle_mute()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key):
        # Global key toggles
        if key == pygame.K_m:
            self.toggle_sound()
            return

        if self.state == GameState.MENU:
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.sound.play("click")
                self.reset_game()
                self.state = GameState.PLAYING
            elif key == pygame.K_d:
                self.cycle_difficulty()
            elif key == pygame.K_w:
                self.toggle_walls()
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == GameState.PLAYING:
            # Snake directional inputs
            if key in (pygame.K_UP, pygame.K_w):
                self.snake.queue_direction(DIR_UP)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.snake.queue_direction(DIR_DOWN)
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.snake.queue_direction(DIR_LEFT)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.snake.queue_direction(DIR_RIGHT)
            elif key in (pygame.K_p, pygame.K_SPACE):
                self.sound.play("click")
                self.state = GameState.PAUSED
            elif key == pygame.K_r:
                self.sound.play("click")
                self.reset_game()
            elif key == pygame.K_ESCAPE:
                self.sound.play("click")
                self.state = GameState.MENU

        elif self.state == GameState.PAUSED:
            if key in (pygame.K_p, pygame.K_SPACE):
                self.sound.play("click")
                self.state = GameState.PLAYING
            elif key == pygame.K_r:
                self.sound.play("click")
                self.reset_game()
                self.state = GameState.PLAYING
            elif key == pygame.K_ESCAPE:
                self.sound.play("click")
                self.state = GameState.MENU

        elif self.state == GameState.GAME_OVER:
            if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                self.sound.play("click")
                self.reset_game()
                self.state = GameState.PLAYING
            elif key == pygame.K_ESCAPE:
                self.sound.play("click")
                self.state = GameState.MENU

    def update(self, dt: float):
        self.total_time += dt

        # Screen shake countdown
        if self.shake_time > 0:
            self.shake_time = max(0.0, self.shake_time - dt)

        # Update particles in all states
        self.particles.update(dt)

        if self.state == GameState.PLAYING:
            self._update_playing(dt)

    def _update_playing(self, dt: float):
        # Update bonus snack lifespan
        if self.bonus_snack:
            if not self.bonus_snack.update(dt):
                self.bonus_snack = None
        else:
            # Bonus snack countdown
            self.bonus_spawn_timer -= dt
            if self.bonus_spawn_timer <= 0:
                occupied = set(self.snake.body)
                if self.regular_snack:
                    occupied.add((self.regular_snack.grid_x, self.regular_snack.grid_y))
                self.bonus_snack = self.spawner.spawn_bonus(occupied)
                if self.bonus_snack:
                    self.sound.play("bonus")
                self.bonus_spawn_timer = random.uniform(18.0, 28.0)

        # Update regular snack animation
        if self.regular_snack:
            self.regular_snack.update(dt)

        # Frenzy tail trail particles
        if self.snake.is_frenzy:
            tail_x = self.margin_x + self.snake.body[-1][0] * self.cell_size + self.cell_size // 2
            tail_y = self.margin_y + self.snake.body[-1][1] * self.cell_size + self.cell_size // 2
            self.particles.emit_trail(tail_x, tail_y, (255, 120, 20))

        # Dynamic speed calculation
        speed = self.base_speed + min(4.0, (self.score / 250.0))
        step_interval = 1.0 / speed

        self.move_accumulator += dt
        while self.move_accumulator >= step_interval:
            self.move_accumulator -= step_interval
            success, ate_self, hit_wall = self.snake.update(step_interval, self.cols, self.rows, self.wrap_walls)

            if not success:
                self._handle_game_over(ate_self, hit_wall)
                return

            # Check snack collisions
            self._check_snack_collisions()

    def _check_snack_collisions(self):
        head = self.snake.head

        # 1. Regular Snack Collision
        if self.regular_snack and head == (self.regular_snack.grid_x, self.regular_snack.grid_y):
            self._eat_snack(self.regular_snack)
            occupied = set(self.snake.body)
            if self.bonus_snack:
                occupied.add((self.bonus_snack.grid_x, self.bonus_snack.grid_y))
            self.regular_snack = self.spawner.spawn_regular(occupied)

        # 2. Bonus Snack Collision
        if self.bonus_snack and head == (self.bonus_snack.grid_x, self.bonus_snack.grid_y):
            self._eat_snack(self.bonus_snack)
            self.bonus_snack = None

    def _eat_snack(self, snack: Snack):
        self.snacks_eaten += 1
        multiplier = 2 if self.snake.is_frenzy else 1
        pts = snack.points * multiplier
        self.score += pts
        self.snake.grow(snack.growth)

        # Screen coordinates for particle burst & floating text
        sx = self.margin_x + snack.grid_x * self.cell_size + self.cell_size // 2
        sy = self.margin_y + snack.grid_y * self.cell_size + self.cell_size // 2

        # Audio and special effects
        if snack.type == SnackType.CHILI:
            self.snake.trigger_frenzy(8.0)
            self.sound.play("frenzy")
            self.particles.emit_snack_burst(sx, sy, [(255, 60, 20), (255, 160, 30), (255, 220, 50)], count=24, is_bonus=True)
            self.particles.add_floating_text(f"+{pts} CHILI FRENZY 2X!", sx, sy - 10, (255, 100, 40), self.ui.popup_font, is_big=True)
        elif snack.is_bonus:
            self.sound.play("bonus")
            self.particles.emit_snack_burst(sx, sy, [(255, 215, 0), (255, 255, 255), (0, 240, 255), (255, 105, 180)], count=28, is_bonus=True)
            self.particles.add_floating_text(f"+{pts} MEGA BONUS!", sx, sy - 10, (255, 215, 50), self.ui.popup_font, is_big=True)
        else:
            if snack.points >= 40:
                self.sound.play("big_eat")
            else:
                self.sound.play("eat")
            self.particles.emit_snack_burst(sx, sy, snack.colors, count=16)
            txt = f"+{pts} FRENZY!" if self.snake.is_frenzy else f"+{pts}"
            col = (255, 180, 50) if self.snake.is_frenzy else (240, 245, 255)
            self.particles.add_floating_text(txt, sx, sy - 10, col, self.ui.popup_font)

        # High score instant celebration check
        if self.score > self.ui.high_score and not self.is_new_high_score:
            self.is_new_high_score = True
            self.sound.play("high_score")

    def _handle_game_over(self, ate_self: bool, hit_wall: bool):
        self.state = GameState.GAME_OVER
        self.trigger_shake(0.4, 7.0)
        self.sound.play("die")
        self.is_new_high_score = self.ui.save_high_score(self.score)

    def draw(self):
        # Background fill
        self.screen.fill((10, 13, 20))

        # Compute screen shake offset
        shake_ox = 0
        shake_oy = 0
        if self.shake_time > 0:
            shake_ox = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_oy = random.uniform(-self.shake_intensity, self.shake_intensity)

        board_x = self.margin_x + int(shake_ox)
        board_y = self.margin_y + int(shake_oy)

        # 1. Draw Checkerboard Game Grid
        self._draw_grid(board_x, board_y)

        # 2. Draw Snacks
        if self.regular_snack:
            self.regular_snack.draw(self.screen, self.cell_size, offset_x=board_x, offset_y=board_y)
        if self.bonus_snack:
            self.bonus_snack.draw(self.screen, self.cell_size, offset_x=board_x, offset_y=board_y)

        # 3. Draw Snake
        if self.snake:
            self.snake.draw(self.screen, self.cell_size, offset_x=board_x, offset_y=board_y)

        # 4. Draw Particles and Floating Text
        self.particles.draw(self.screen)

        # 5. Draw Glowing Neon Border Around Board
        border_rect = pygame.Rect(board_x - 3, board_y - 3, self.grid_width + 6, self.grid_height + 6)
        border_col = (0, 220, 180) if not (self.snake and self.snake.is_frenzy) else (255, 120, 30)
        pygame.draw.rect(self.screen, border_col, border_rect, width=2, border_radius=8)

        # 6. Top HUD
        frenzy_rem = self.snake.frenzy_timer if self.snake else 0.0
        self.ui.draw_hud(self.screen, self.score, self.snacks_eaten,
                         self.current_difficulty, self.wrap_walls, self.sound.muted,
                         frenzy_timer=frenzy_rem)

        # 7. Modal Overlays
        if self.state == GameState.MENU:
            self.ui.draw_menu(self.screen, self.total_time, self.current_difficulty, self.wrap_walls, self.sound.muted)
        elif self.state == GameState.PAUSED:
            self.ui.draw_pause(self.screen)
        elif self.state == GameState.GAME_OVER:
            length = len(self.snake.body) if self.snake else 4
            self.ui.draw_game_over(self.screen, self.score, self.snacks_eaten, length, self.is_new_high_score, self.total_time)

        pygame.display.flip()

    def _draw_grid(self, bx: int, by: int):
        c1 = (18, 22, 32)
        c2 = (22, 27, 38)
        for r in range(self.rows):
            for c in range(self.cols):
                color = c1 if (r + c) % 2 == 0 else c2
                rect = pygame.Rect(bx + c * self.cell_size, by + r * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            # Clamp dt to prevent massive jumps on window pause/unfocus
            dt = min(dt, 0.1)

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    from main import main
    main()
