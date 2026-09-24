# 🐍 Neon Snake Arcade (Python)

A modern, arcade-style Snake game built with Python and Tkinter. Works out of the box with zero external dependencies required!

---

## 🚀 How to Run the Game

You can run the game in either of two easy ways:

### Option 1: Terminal
Open your terminal in this folder and run:
```bash
python snake_game.py
```

### Option 2: Double-Click
Double-click `run_snake.bat` in File Explorer.

---

## 🎮 Controls

| Key | Action |
| :--- | :--- |
| **Arrow Keys** or **W / A / S / D** | Steer the Snake (Up, Left, Down, Right) |
| **Spacebar** | Start Game / Pause / Resume / Retry |
| **P** | Toggle Pause |
| **R** | Reset / Restart Game |
| **M** | Mute / Unmute Sound Effects |

---

## ✨ Features

- **Cyberpunk / Neon Aesthetics**: Smooth gradient snake body, glowing animated eyes that look where you steer, and a flickering tongue.
- **Snack Varieties**:
  - 🍎 **Crispy Red Apple**: Regular snack (+10 points).
  - ⭐ **Golden Super Snack**: Timed bonus snack spawning every 5 apples (+50 to +80 bonus points with countdown timer).
- **Particle Explosion System**: Bursting sparkles when eating food.
- **4 Speed Settings**:
  - **Casual** (Relaxed pace)
  - **Arcade** (Classic pace)
  - **Fast** (Challenging)
  - **Turbo** (Lightning reflexes)
- **2 Wall Modes**:
  - 🧱 **Solid Walls**: Classic mode — touching the border results in game over.
  - 🌀 **Wrap Portal**: Snake teleports smoothly through borders to the opposite edge.
- **Audio Feedback**: Retro arcade sounds using Windows built-in sound engine (no external audio libraries required).
- **Persistent High Scores**: Automatically saves your best score to `snake_highscores.json`.
