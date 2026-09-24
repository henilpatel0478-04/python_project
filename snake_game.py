"""
================================================================================
🐍 RETRO NEON SNAKE GAME - PYTHON & TKINTER
================================================================================
An arcade-quality Snake game built with Python and Tkinter.
Features:
  - Modern Dark Neon Cyberpunk Aesthetic & Glowing Canvas
  - Gradient body with directional googly eyes and flickering tongue
  - Multiple Snack types:
      * Crispy Red Apples (Regular Snack, +10 pts)
      * Golden Super Snacks (Timed bonus with glowing countdown ring, +50-80 pts)
  - Particle burst sparkles on eating snacks
  - 4 Difficulty Speeds: Casual, Arcade, Fast, Turbo
  - 2 Wall Modes: Solid Walls (Classic) & Wrap Portal (Wrap-Around)
  - Persistent High Score tracking (snake_highscores.json)
  - Non-blocking arcade sound effects via winsound
  - Bulletproof controls: zero-focus steal (takefocus=False), bind_all,
    rapid keypress suicide prevention, and clean window closing.
================================================================================
"""

import os
import sys
import json
import math
import random
import time
import threading
import tkinter as tk
from tkinter import font as tkfont

# Optional sound support on Windows
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# ----------------------------------------------------------------------
# Configuration Constants
# ----------------------------------------------------------------------
GRID_SIZE = 24       # 24 cells wide and high
CELL_SIZE = 25       # 25 pixels per cell -> 600x600 canvas
CANVAS_WIDTH = GRID_SIZE * CELL_SIZE
CANVAS_HEIGHT = GRID_SIZE * CELL_SIZE

# Color Palette (Arcade Neon / Dark Theme)
BG_COLOR = "#0c1017"
CANVAS_BG = "#0f172a"
GRID_LINE_COLOR = "#1e293b"
BORDER_COLOR = "#334155"

SNAKE_HEAD_COLOR = "#00ff88"
SNAKE_EYE_COLOR = "#ffffff"
SNAKE_PUPIL_COLOR = "#0f172a"
SNAKE_TONGUE_COLOR = "#ff0055"

# Gradient colors along snake body
BODY_COLORS = [
    "#00ff88", "#00f099", "#00e1aa", "#00d2bb",
    "#00c3cc", "#00b4dd", "#00a5ee", "#0096ff",
    "#2575fc", "#4a54f1", "#6a11cb"
]

APPLE_COLOR = "#ff2a5f"
APPLE_LEAF_COLOR = "#10b981"
APPLE_STEM_COLOR = "#854d0e"

GOLDEN_COLOR = "#facc15"
GOLDEN_GLOW = "#fef08a"

TEXT_WHITE = "#f8fafc"
TEXT_MUTED = "#94a3b8"
ACCENT_GREEN = "#10b981"
ACCENT_CYAN = "#06b6d4"
ACCENT_PURPLE = "#a855f7"
ACCENT_AMBER = "#f59e0b"
ACCENT_RED = "#ef4444"

SPEEDS = {
    "Casual": 125,   # ms per tick
    "Arcade": 90,
    "Fast": 65,
    "Turbo": 45
}

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_highscores.json")


# ----------------------------------------------------------------------
# Sound Manager (Daemon Threaded, Non-blocking, Lock-Protected)
# ----------------------------------------------------------------------
class SoundManager:
    def __init__(self):
        self.enabled = HAS_WINSOUND
        self._lock = threading.Lock()

    def play(self, sound_type):
        if not self.enabled or not HAS_WINSOUND:
            return
        threading.Thread(target=self._play_worker, args=(sound_type,), daemon=True).start()

    def _play_worker(self, sound_type):
        # Non-blocking lock prevents audio driver contention
        if not self._lock.acquire(blocking=False):
            return
        try:
            if sound_type == "eat":
                winsound.Beep(920, 35)
                winsound.Beep(1280, 45)
            elif sound_type == "golden":
                winsound.Beep(650, 40)
                winsound.Beep(880, 45)
                winsound.Beep(1320, 80)
            elif sound_type == "gameover":
                winsound.Beep(420, 110)
                winsound.Beep(320, 130)
                winsound.Beep(210, 240)
            elif sound_type == "click":
                winsound.Beep(1200, 20)
            elif sound_type == "levelup":
                winsound.Beep(880, 50)
                winsound.Beep(1175, 70)
        except Exception:
            pass
        finally:
            self._lock.release()


# ----------------------------------------------------------------------
# Particle System (Visual flair for eating snacks)
# ----------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.0, 5.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(3.0, 6.0)
        self.life = random.randint(10, 18)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.life -= 1
        return self.life > 0

    def draw(self, canvas):
        r = self.size * (self.life / self.max_life)
        canvas.create_oval(
            self.x - r, self.y - r, self.x + r, self.y + r,
            fill=self.color, outline=""
        )


# ----------------------------------------------------------------------
# Main Game Class
# ----------------------------------------------------------------------
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Neon Snake Arcade")
        self.root.geometry("640x790")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Handle window closing gracefully
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.sounds = SoundManager()
        self.high_score = self.load_high_score()

        # Game State
        self.state = "START"  # "START", "RUNNING", "PAUSED", "GAMEOVER", "CLOSED"
        self.score = 0
        self.apples_eaten = 0
        self.snake = []
        self.direction = "Right"
        self.next_direction = "Right"
        self.dir_locked = False
        self.after_id = None
        self.food = None
        self.golden_food = None
        self.golden_timer = 0
        self.golden_max_timer = 70
        self.particles = []
        self.tongue_flicker = 0
        self.pulse_phase = 0.0

        # Settings
        self.difficulty = "Arcade"
        self.wrap_walls = False
        self.sound_on = self.sounds.enabled

        self.setup_ui()
        self.bind_events()
        self.show_start_screen()

    # ------------------------------------------------------------------
    # High Score Persistence
    # ------------------------------------------------------------------
    def load_high_score(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"high_score": self.high_score, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def setup_ui(self):
        # 1. Top HUD Bar
        hud_frame = tk.Frame(self.root, bg=BG_COLOR, padx=16, pady=8)
        hud_frame.pack(fill=tk.X)

        # Left: Current Score
        score_box = tk.Frame(hud_frame, bg="#161f30", padx=12, pady=4, relief=tk.FLAT)
        score_box.pack(side=tk.LEFT)
        tk.Label(score_box, text="SCORE", font=("Helvetica", 9, "bold"), fg=TEXT_MUTED, bg="#161f30").pack(anchor="w")
        self.lbl_score = tk.Label(score_box, text="000", font=("Consolas", 18, "bold"), fg=ACCENT_GREEN, bg="#161f30")
        self.lbl_score.pack(anchor="w")

        # Center: Snacks Counter & Golden Alert
        center_box = tk.Frame(hud_frame, bg=BG_COLOR)
        center_box.pack(side=tk.LEFT, expand=True)

        self.lbl_snacks = tk.Label(center_box, text="🍎 Snacks: 0", font=("Helvetica", 11, "bold"), fg=TEXT_WHITE, bg=BG_COLOR)
        self.lbl_snacks.pack()

        self.lbl_golden_status = tk.Label(
            center_box, text="", font=("Helvetica", 9, "bold"), fg=GOLDEN_COLOR, bg=BG_COLOR
        )
        self.lbl_golden_status.pack()

        # Right: High Score
        hi_box = tk.Frame(hud_frame, bg="#161f30", padx=12, pady=4, relief=tk.FLAT)
        hi_box.pack(side=tk.RIGHT)
        tk.Label(hi_box, text="🏆 BEST", font=("Helvetica", 9, "bold"), fg=TEXT_MUTED, bg="#161f30").pack(anchor="e")
        self.lbl_high_score = tk.Label(hi_box, text=f"{self.high_score:03d}", font=("Consolas", 18, "bold"), fg=GOLDEN_COLOR, bg="#161f30")
        self.lbl_high_score.pack(anchor="e")

        # 2. Main Game Canvas
        canvas_border = tk.Frame(self.root, bg=BORDER_COLOR, padx=2, pady=2)
        canvas_border.pack(padx=16, pady=4)

        self.canvas = tk.Canvas(
            canvas_border,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=CANVAS_BG,
            highlightthickness=0
        )
        self.canvas.pack()

        # 3. Bottom Controls / Options Bar
        bottom_frame = tk.Frame(self.root, bg=BG_COLOR, padx=14, pady=6)
        bottom_frame.pack(fill=tk.X)

        # Row 1: Action Buttons (takefocus=False prevents keyboard focus stealing)
        btn_frame = tk.Frame(bottom_frame, bg=BG_COLOR)
        btn_frame.pack(fill=tk.X, pady=2)

        self.btn_main = tk.Button(
            btn_frame,
            text="▶ Start Game",
            font=("Helvetica", 10, "bold"),
            bg="#059669",
            fg="white",
            activebackground="#10b981",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            takefocus=False,
            command=self.handle_main_button
        )
        self.btn_main.pack(side=tk.LEFT, padx=3)

        self.btn_restart = tk.Button(
            btn_frame,
            text="🔄 Reset",
            font=("Helvetica", 10),
            bg="#334155",
            fg=TEXT_WHITE,
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            takefocus=False,
            command=self.reset_game
        )
        self.btn_restart.pack(side=tk.LEFT, padx=3)

        self.btn_diff = tk.Button(
            btn_frame,
            text=f"⚡ {self.difficulty}",
            font=("Helvetica", 10),
            bg="#334155",
            fg=ACCENT_CYAN,
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            takefocus=False,
            command=self.cycle_difficulty
        )
        self.btn_diff.pack(side=tk.LEFT, padx=3)

        self.btn_walls = tk.Button(
            btn_frame,
            text="🧱 Solid Walls",
            font=("Helvetica", 10),
            bg="#334155",
            fg=TEXT_WHITE,
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            takefocus=False,
            command=self.toggle_walls
        )
        self.btn_walls.pack(side=tk.LEFT, padx=3)

        self.btn_sound = tk.Button(
            btn_frame,
            text="🔊 Sound",
            font=("Helvetica", 10),
            bg="#334155",
            fg=ACCENT_AMBER if self.sound_on else TEXT_MUTED,
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            takefocus=False,
            command=self.toggle_sound
        )
        self.btn_sound.pack(side=tk.RIGHT, padx=3)

        # Row 2: Helpful Key Guide
        guide_lbl = tk.Label(
            bottom_frame,
            text="🕹 Controls: Arrow Keys or W/A/S/D  •  Space: Pause/Resume  •  R: Restart",
            font=("Helvetica", 9),
            fg=TEXT_MUTED,
            bg=BG_COLOR
        )
        guide_lbl.pack(pady=4)

    # ------------------------------------------------------------------
    # Key Bindings (bind_all ensures keypresses work regardless of focus)
    # ------------------------------------------------------------------
    def bind_events(self):
        for key in ("<Left>", "<a>", "<A>"):
            self.root.bind_all(key, lambda e: self.change_direction("Left"))
        for key in ("<Right>", "<d>", "<D>"):
            self.root.bind_all(key, lambda e: self.change_direction("Right"))
        for key in ("<Up>", "<w>", "<W>"):
            self.root.bind_all(key, lambda e: self.change_direction("Up"))
        for key in ("<Down>", "<s>", "<S>"):
            self.root.bind_all(key, lambda e: self.change_direction("Down"))

        self.root.bind_all("<space>", lambda e: self.handle_space_bar())
        self.root.bind_all("<p>", lambda e: self.toggle_pause())
        self.root.bind_all("<P>", lambda e: self.toggle_pause())
        self.root.bind_all("<r>", lambda e: self.reset_game())
        self.root.bind_all("<R>", lambda e: self.reset_game())
        self.root.bind_all("<m>", lambda e: self.toggle_sound())
        self.root.bind_all("<M>", lambda e: self.toggle_sound())

    def change_direction(self, new_dir):
        if self.state != "RUNNING" or self.dir_locked:
            return
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        # Check against next_direction to avoid rapid turn suicide bug
        if new_dir != opposites.get(self.next_direction) and new_dir != self.next_direction:
            self.next_direction = new_dir
            self.dir_locked = True

    def handle_space_bar(self):
        if self.state in ("START", "GAMEOVER"):
            self.start_game()
        elif self.state in ("RUNNING", "PAUSED"):
            self.toggle_pause()

    def handle_main_button(self):
        if self.state in ("START", "GAMEOVER"):
            self.start_game()
        elif self.state in ("RUNNING", "PAUSED"):
            self.toggle_pause()

    def toggle_pause(self):
        if self.state == "RUNNING":
            self.state = "PAUSED"
            self.cancel_timer()
            self.btn_main.config(text="▶ Resume", bg="#2563eb")
            self.draw_overlay("⏸ PAUSED", "Press [SPACE] or Click Resume", ACCENT_CYAN)
        elif self.state == "PAUSED":
            self.state = "RUNNING"
            self.btn_main.config(text="⏸ Pause", bg="#d97706")
            self.game_loop()

    def cycle_difficulty(self):
        diffs = list(SPEEDS.keys())
        idx = (diffs.index(self.difficulty) + 1) % len(diffs)
        self.difficulty = diffs[idx]
        self.btn_diff.config(text=f"⚡ {self.difficulty}")
        self.sounds.play("click")

    def toggle_walls(self):
        self.wrap_walls = not self.wrap_walls
        if self.wrap_walls:
            self.btn_walls.config(text="🌀 Wrap Portal", fg=ACCENT_PURPLE)
        else:
            self.btn_walls.config(text="🧱 Solid Walls", fg=TEXT_WHITE)
        self.sounds.play("click")
        if self.state in ("RUNNING", "PAUSED"):
            self.render()

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.sounds.enabled = self.sound_on
        if self.sound_on:
            self.btn_sound.config(text="🔊 Sound", fg=ACCENT_AMBER)
            self.sounds.play("click")
        else:
            self.btn_sound.config(text="🔇 Muted", fg=TEXT_MUTED)

    def cancel_timer(self):
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def on_closing(self):
        self.state = "CLOSED"
        self.cancel_timer()
        try:
            self.root.destroy()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Start / Reset / Game Over Handlers
    # ------------------------------------------------------------------
    def start_game(self):
        self.cancel_timer()
        self.snake = [
            (GRID_SIZE // 2, GRID_SIZE // 2),
            (GRID_SIZE // 2 - 1, GRID_SIZE // 2),
            (GRID_SIZE // 2 - 2, GRID_SIZE // 2),
        ]
        self.direction = "Right"
        self.next_direction = "Right"
        self.dir_locked = False
        self.score = 0
        self.apples_eaten = 0
        self.golden_food = None
        self.golden_timer = 0
        self.particles.clear()
        self.update_score_display()

        self.spawn_food()
        self.state = "RUNNING"
        self.btn_main.config(text="⏸ Pause", bg="#d97706")
        self.sounds.play("click")
        self.game_loop()

    def reset_game(self):
        self.cancel_timer()
        self.state = "START"
        self.score = 0
        self.apples_eaten = 0
        self.golden_food = None
        self.golden_timer = 0
        self.particles.clear()
        self.update_score_display()
        self.btn_main.config(text="▶ Start Game", bg="#059669")
        self.show_start_screen()

    def game_over(self):
        self.cancel_timer()
        self.state = "GAMEOVER"
        self.sounds.play("gameover")
        self.btn_main.config(text="🔄 Play Again", bg="#059669")

        is_new_high = False
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.lbl_high_score.config(text=f"{self.high_score:03d}")
            is_new_high = True

        self.draw_game_over_screen(is_new_high)

    # ------------------------------------------------------------------
    # Food Management
    # ------------------------------------------------------------------
    def spawn_food(self):
        available = [
            (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
            if (x, y) not in self.snake and (x, y) != self.golden_food
        ]
        if available:
            self.food = random.choice(available)
        else:
            self.food = (0, 0)

    def spawn_golden_food(self):
        available = [
            (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
            if (x, y) not in self.snake and (x, y) != self.food
        ]
        if available:
            self.golden_food = random.choice(available)
            self.golden_timer = self.golden_max_timer
            self.lbl_golden_status.config(text="⭐ GOLDEN SNACK ACTIVE! +50")
            self.sounds.play("levelup")

    def spawn_particles(self, gx, gy, color, count=14):
        cx = gx * CELL_SIZE + CELL_SIZE / 2
        cy = gy * CELL_SIZE + CELL_SIZE / 2
        for _ in range(count):
            self.particles.append(Particle(cx, cy, color))

    # ------------------------------------------------------------------
    # Main Engine Loop
    # ------------------------------------------------------------------
    def game_loop(self):
        if self.state != "RUNNING":
            return

        self.cancel_timer()

        self.direction = self.next_direction
        self.dir_locked = False
        head_x, head_y = self.snake[0]

        # Calculate new head coordinate
        if self.direction == "Up":
            new_head = (head_x, head_y - 1)
        elif self.direction == "Down":
            new_head = (head_x, head_y + 1)
        elif self.direction == "Left":
            new_head = (head_x - 1, head_y)
        elif self.direction == "Right":
            new_head = (head_x + 1, head_y)

        # Handle Wall Collisions or Wrap-around
        nx, ny = new_head
        if self.wrap_walls:
            nx = nx % GRID_SIZE
            ny = ny % GRID_SIZE
            new_head = (nx, ny)
        else:
            if nx < 0 or nx >= GRID_SIZE or ny < 0 or ny >= GRID_SIZE:
                self.game_over()
                return

        # Handle Self Collision (ignore tail because it moves away if not eating)
        tail = self.snake[-1]
        will_grow = (new_head == self.food) or (new_head == self.golden_food)
        body_to_check = self.snake if will_grow else self.snake[:-1]

        if new_head in body_to_check:
            self.game_over()
            return

        # Advance snake
        self.snake.insert(0, new_head)

        # Check Food Collision
        if new_head == self.food:
            self.score += 10
            self.apples_eaten += 1
            self.sounds.play("eat")
            self.spawn_particles(new_head[0], new_head[1], APPLE_COLOR, 14)
            self.update_score_display()
            self.spawn_food()

            # Check if golden fruit should spawn (every 5 apples)
            if self.apples_eaten > 0 and self.apples_eaten % 5 == 0 and not self.golden_food:
                self.spawn_golden_food()

        elif self.golden_food and new_head == self.golden_food:
            bonus = 50 + int((self.golden_timer / self.golden_max_timer) * 30)
            self.score += bonus
            self.sounds.play("golden")
            self.spawn_particles(new_head[0], new_head[1], GOLDEN_COLOR, 22)
            self.golden_food = None
            self.golden_timer = 0
            self.lbl_golden_status.config(text="")
            self.update_score_display()

        else:
            # Normal move, remove tail
            self.snake.pop()

        # Update Golden Food Timer
        if self.golden_food:
            self.golden_timer -= 1
            pct = int((self.golden_timer / self.golden_max_timer) * 100)
            self.lbl_golden_status.config(text=f"⭐ GOLDEN SNACK: {pct}%")
            if self.golden_timer <= 0:
                self.golden_food = None
                self.lbl_golden_status.config(text="")

        # Update visuals
        self.pulse_phase += 0.25
        self.tongue_flicker = (self.tongue_flicker + 1) % 6
        self.render()

        # Schedule next tick
        if self.state == "RUNNING":
            delay = SPEEDS.get(self.difficulty, 90)
            self.after_id = self.root.after(delay, self.game_loop)

    def update_score_display(self):
        self.lbl_score.config(text=f"{self.score:03d}")
        self.lbl_snacks.config(text=f"🍎 Snacks: {self.apples_eaten}")
        if self.score > self.high_score:
            self.lbl_high_score.config(text=f"{self.score:03d}", fg="#00ff88")

    # ------------------------------------------------------------------
    # Rendering Methods
    # ------------------------------------------------------------------
    def render(self):
        try:
            self.canvas.delete("all")
            self.draw_grid()
            self.draw_particles()
            self.draw_food()
            self.draw_snake()
        except tk.TclError:
            pass  # Window closed during render

    def draw_grid(self):
        # Subtle glowing grid pattern
        for x in range(0, CANVAS_WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill=GRID_LINE_COLOR, width=1)
        for y in range(0, CANVAS_HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, CANVAS_WIDTH, y, fill=GRID_LINE_COLOR, width=1)

        # Border outline if solid walls
        if not self.wrap_walls:
            self.canvas.create_rectangle(
                1, 1, CANVAS_WIDTH - 1, CANVAS_HEIGHT - 1,
                outline="#dc2626", width=2
            )

    def draw_particles(self):
        surviving = []
        for p in self.particles:
            if p.update():
                p.draw(self.canvas)
                surviving.append(p)
        self.particles = surviving

    def draw_food(self):
        # 1. Regular Apple
        if self.food:
            fx, fy = self.food
            cx = fx * CELL_SIZE + CELL_SIZE / 2
            cy = fy * CELL_SIZE + CELL_SIZE / 2

            pulse = math.sin(self.pulse_phase) * 1.5
            r = (CELL_SIZE / 2 - 2) + pulse

            # Apple Body
            self.canvas.create_oval(
                cx - r, cy - r + 1, cx + r, cy + r + 1,
                fill=APPLE_COLOR, outline="#ff6b8b", width=1
            )
            # Specular highlight
            self.canvas.create_oval(
                cx - r * 0.5, cy - r * 0.6, cx - r * 0.1, cy - r * 0.2,
                fill="#ffffff", outline=""
            )
            # Stem
            self.canvas.create_line(
                cx, cy - r + 1, cx + 2, cy - r - 4,
                fill=APPLE_STEM_COLOR, width=2
            )
            # Green leaf
            self.canvas.create_oval(
                cx + 1, cy - r - 4, cx + 6, cy - r,
                fill=APPLE_LEAF_COLOR, outline=""
            )

        # 2. Golden Super Snack (if active)
        if self.golden_food:
            gx, gy = self.golden_food
            cx = gx * CELL_SIZE + CELL_SIZE / 2
            cy = gy * CELL_SIZE + CELL_SIZE / 2

            # Pulsing golden halo
            halo_r = (CELL_SIZE / 2 + 3) + math.sin(self.pulse_phase * 2) * 2.5
            self.canvas.create_oval(
                cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r,
                outline=GOLDEN_GLOW, width=2
            )

            # Golden orb
            r = CELL_SIZE / 2 - 2
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=GOLDEN_COLOR, outline="#fff", width=1.5
            )
            # Star icon on top
            self.canvas.create_text(
                cx, cy, text="★", font=("Helvetica", 12, "bold"), fill="#78350f"
            )

    def draw_snake(self):
        if not self.snake:
            return

        # Draw body segments from tail to head
        body_len = len(self.snake)
        for i in range(body_len - 1, 0, -1):
            x, y = self.snake[i]
            cx = x * CELL_SIZE + CELL_SIZE / 2
            cy = y * CELL_SIZE + CELL_SIZE / 2

            color_idx = min(int((i / max(body_len, 1)) * len(BODY_COLORS)), len(BODY_COLORS) - 1)
            seg_color = BODY_COLORS[color_idx]

            radius = (CELL_SIZE / 2) - 1.5
            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=seg_color, outline="#0f172a", width=1
            )

            inner_r = radius * 0.45
            self.canvas.create_oval(
                cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
                fill="#ffffff", outline="", stipple="gray25" if sys.platform.startswith("win") else ""
            )

        # Draw Head with Eyes and Tongue
        hx, hy = self.snake[0]
        hcx = hx * CELL_SIZE + CELL_SIZE / 2
        hcy = hy * CELL_SIZE + CELL_SIZE / 2
        hradius = CELL_SIZE / 2

        self.canvas.create_oval(
            hcx - hradius, hcy - hradius, hcx + hradius, hcy + hradius,
            fill=SNAKE_HEAD_COLOR, outline="#ffffff", width=1.5
        )

        eye_offset = 6
        pupil_offset = 2
        eye_r = 3.5
        pupil_r = 1.8

        if self.direction == "Right":
            eye1 = (hcx + 3, hcy - eye_offset)
            eye2 = (hcx + 3, hcy + eye_offset)
            p_dx, p_dy = pupil_offset, 0
            t_start = (hcx + hradius, hcy)
            t_end = (hcx + hradius + 6, hcy)
            t_fork1 = (hcx + hradius + 9, hcy - 3)
            t_fork2 = (hcx + hradius + 9, hcy + 3)
        elif self.direction == "Left":
            eye1 = (hcx - 3, hcy - eye_offset)
            eye2 = (hcx - 3, hcy + eye_offset)
            p_dx, p_dy = -pupil_offset, 0
            t_start = (hcx - hradius, hcy)
            t_end = (hcx - hradius - 6, hcy)
            t_fork1 = (hcx - hradius - 9, hcy - 3)
            t_fork2 = (hcx - hradius - 9, hcy + 3)
        elif self.direction == "Up":
            eye1 = (hcx - eye_offset, hcy - 3)
            eye2 = (hcx + eye_offset, hcy - 3)
            p_dx, p_dy = 0, -pupil_offset
            t_start = (hcx, hcy - hradius)
            t_end = (hcx, hcy - hradius - 6)
            t_fork1 = (hcx - 3, hcy - hradius - 9)
            t_fork2 = (hcx + 3, hcy - hradius - 9)
        else:  # Down
            eye1 = (hcx - eye_offset, hcy + 3)
            eye2 = (hcx + eye_offset, hcy + 3)
            p_dx, p_dy = 0, pupil_offset
            t_start = (hcx, hcy + hradius)
            t_end = (hcx, hcy + hradius + 6)
            t_fork1 = (hcx - 3, hcy + hradius + 9)
            t_fork2 = (hcx + 3, hcy + hradius + 9)

        if self.tongue_flicker < 3:
            self.canvas.create_line(t_start[0], t_start[1], t_end[0], t_end[1], fill=SNAKE_TONGUE_COLOR, width=2)
            self.canvas.create_line(t_end[0], t_end[1], t_fork1[0], t_fork1[1], fill=SNAKE_TONGUE_COLOR, width=1.5)
            self.canvas.create_line(t_end[0], t_end[1], t_fork2[0], t_fork2[1], fill=SNAKE_TONGUE_COLOR, width=1.5)

        for ex, ey in (eye1, eye2):
            self.canvas.create_oval(
                ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r,
                fill=SNAKE_EYE_COLOR, outline=""
            )
            self.canvas.create_oval(
                ex + p_dx - pupil_r, ey + p_dy - pupil_r,
                ex + p_dx + pupil_r, ey + p_dy + pupil_r,
                fill=SNAKE_PUPIL_COLOR, outline=""
            )

    # ------------------------------------------------------------------
    # Overlays (Start, Pause, Game Over)
    # ------------------------------------------------------------------
    def show_start_screen(self):
        self.canvas.delete("all")
        self.draw_grid()

        mid_x = CANVAS_WIDTH / 2
        mid_y = CANVAS_HEIGHT / 2

        self.canvas.create_rectangle(
            mid_x - 220, mid_y - 170, mid_x + 220, mid_y + 170,
            fill="#111827", outline="#374151", width=2
        )

        self.canvas.create_text(
            mid_x, mid_y - 110,
            text="🐍 NEON SNAKE",
            font=("Impact", 36),
            fill=SNAKE_HEAD_COLOR
        )
        self.canvas.create_text(
            mid_x, mid_y - 65,
            text="CLASSIC ARCADE EDITION",
            font=("Helvetica", 11, "bold"),
            fill=ACCENT_CYAN
        )

        self.canvas.create_line(
            mid_x - 140, mid_y - 45, mid_x + 140, mid_y - 45,
            fill="#374151", width=1.5
        )

        items = [
            "🍎 Eat Crispy Red Snacks to Grow (+10 pts)",
            "⭐ Catch Timed Golden Snacks (+50+ pts)",
            "🧱 Avoid Walls or Switch to Wrap Portal",
            "⚡ Choose your speed: Casual to Turbo"
        ]
        for idx, item in enumerate(items):
            self.canvas.create_text(
                mid_x, mid_y - 20 + idx * 26,
                text=item,
                font=("Helvetica", 10),
                fill=TEXT_WHITE
            )

        self.canvas.create_rectangle(
            mid_x - 150, mid_y + 105, mid_x + 150, mid_y + 145,
            fill="#059669", outline="#34d399", width=2
        )
        self.canvas.create_text(
            mid_x, mid_y + 125,
            text="PRESS SPACE TO PLAY",
            font=("Helvetica", 12, "bold"),
            fill="white"
        )

    def draw_overlay(self, title, subtitle, color):
        mid_x = CANVAS_WIDTH / 2
        mid_y = CANVAS_HEIGHT / 2

        self.canvas.create_rectangle(
            mid_x - 180, mid_y - 65, mid_x + 180, mid_y + 65,
            fill="#090d16", outline="#334155", width=2
        )
        self.canvas.create_text(
            mid_x, mid_y - 18,
            text=title,
            font=("Impact", 28),
            fill=color
        )
        self.canvas.create_text(
            mid_x, mid_y + 24,
            text=subtitle,
            font=("Helvetica", 11),
            fill=TEXT_MUTED
        )

    def draw_game_over_screen(self, is_new_high):
        mid_x = CANVAS_WIDTH / 2
        mid_y = CANVAS_HEIGHT / 2

        self.canvas.create_rectangle(
            mid_x - 210, mid_y - 160, mid_x + 210, mid_y + 160,
            fill="#0f172a", outline=ACCENT_RED, width=2
        )

        self.canvas.create_text(
            mid_x, mid_y - 110,
            text="GAME OVER",
            font=("Impact", 36),
            fill=ACCENT_RED
        )

        if is_new_high:
            self.canvas.create_text(
                mid_x, mid_y - 65,
                text="🎉 NEW RECORD HIGH SCORE! 🎉",
                font=("Helvetica", 12, "bold"),
                fill=GOLDEN_COLOR
            )
        else:
            self.canvas.create_text(
                mid_x, mid_y - 65,
                text="You collided! Better luck next run!",
                font=("Helvetica", 10),
                fill=TEXT_MUTED
            )

        self.canvas.create_text(
            mid_x - 50, mid_y - 20,
            text="Final Score:",
            font=("Helvetica", 12, "bold"),
            fill=TEXT_WHITE,
            anchor="e"
        )
        self.canvas.create_text(
            mid_x - 20, mid_y - 20,
            text=f"{self.score}",
            font=("Consolas", 16, "bold"),
            fill=ACCENT_GREEN,
            anchor="w"
        )

        self.canvas.create_text(
            mid_x - 50, mid_y + 15,
            text="Snacks Eaten:",
            font=("Helvetica", 12, "bold"),
            fill=TEXT_WHITE,
            anchor="e"
        )
        self.canvas.create_text(
            mid_x - 20, mid_y + 15,
            text=f"{self.apples_eaten} 🍎",
            font=("Consolas", 14, "bold"),
            fill=APPLE_COLOR,
            anchor="w"
        )

        self.canvas.create_text(
            mid_x - 50, mid_y + 48,
            text="Best Record:",
            font=("Helvetica", 12, "bold"),
            fill=TEXT_WHITE,
            anchor="e"
        )
        self.canvas.create_text(
            mid_x - 20, mid_y + 48,
            text=f"{self.high_score} 🏆",
            font=("Consolas", 14, "bold"),
            fill=GOLDEN_COLOR,
            anchor="w"
        )

        self.canvas.create_rectangle(
            mid_x - 140, mid_y + 95, mid_x + 140, mid_y + 135,
            fill="#059669", outline="#34d399", width=2
        )
        self.canvas.create_text(
            mid_x, mid_y + 115,
            text="PRESS SPACE TO RETRY",
            font=("Helvetica", 11, "bold"),
            fill="white"
        )


# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
