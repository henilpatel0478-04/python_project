"""
UI and HUD rendering, score tracking, local high score persistence,
menus, snack guide preview, and pause/game-over screens.
"""
import json
import math
import os
import pygame
from snack import SNACK_DATA, SnackType, Snack

HIGHSCORE_FILE = "highscore.json"

class UIManager:
    def __init__(self, window_width: int, window_height: int, hud_height: int = 68):
        self.width = window_width
        self.height = window_height
        self.hud_height = hud_height
        self.high_score = self.load_high_score()

        # Initialize fonts with fallback hierarchy
        font_families = ['segoe ui', 'trebuchet ms', 'helvetica', 'arial', 'sans-serif']
        self.title_font = pygame.font.SysFont(font_families, 46, bold=True)
        self.subtitle_font = pygame.font.SysFont(font_families, 22, bold=True)
        self.hud_font = pygame.font.SysFont(font_families, 20, bold=True)
        self.hud_val_font = pygame.font.SysFont(font_families, 22, bold=True)
        self.btn_font = pygame.font.SysFont(font_families, 18, bold=True)
        self.small_font = pygame.font.SysFont(font_families, 14)
        self.popup_font = pygame.font.SysFont(font_families, 22, bold=True)

        # Snack preview instances for menu
        self.preview_snacks = [
            Snack(0, 0, SnackType.APPLE),
            Snack(0, 0, SnackType.PIZZA),
            Snack(0, 0, SnackType.DONUT),
            Snack(0, 0, SnackType.TACO),
            Snack(0, 0, SnackType.BURGER),
            Snack(0, 0, SnackType.CHILI),
            Snack(0, 0, SnackType.SUNDAE),
        ]

    def load_high_score(self) -> int:
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, "r") as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
        except Exception:
            pass
        return 0

    def save_high_score(self, score: int) -> bool:
        if score > self.high_score:
            self.high_score = score
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    json.dump({"high_score": self.high_score}, f)
                return True
            except Exception:
                pass
        return False

    def draw_hud(self, surface: pygame.Surface, score: int, snacks_eaten: int,
                 difficulty: str, wrap_walls: bool, sound_muted: bool,
                 frenzy_timer: float = 0.0):
        """Draws a modern, polished dark top HUD bar."""
        # Top banner background
        hud_rect = pygame.Rect(0, 0, self.width, self.hud_height)
        pygame.draw.rect(surface, (14, 18, 27), hud_rect)
        # Glowing accent border line
        pygame.draw.line(surface, (30, 42, 60), (0, self.hud_height - 1), (self.width, self.hud_height - 1), 2)
        pygame.draw.line(surface, (0, 210, 180), (0, self.hud_height), (self.width, self.hud_height), 1)

        # 1. Current Score
        score_lbl = self.small_font.render("SCORE", True, (140, 160, 185))
        surface.blit(score_lbl, (25, 12))
        score_val_color = (255, 230, 80) if frenzy_timer > 0 else (255, 255, 255)
        score_val = self.hud_val_font.render(f"{score:,}", True, score_val_color)
        surface.blit(score_val, (25, 32))

        # 2. High Score
        high_lbl = self.small_font.render("BEST SCORE", True, (140, 160, 185))
        surface.blit(high_lbl, (155, 12))
        high_val = self.hud_val_font.render(f"{self.high_score:,}", True, (255, 210, 60))
        surface.blit(high_val, (155, 32))

        # 3. Center Status: Frenzy Banner or Snacks Count
        if frenzy_timer > 0:
            frenzy_bg = pygame.Rect(self.width // 2 - 130, 12, 260, 44)
            pygame.draw.rect(surface, (210, 45, 20), frenzy_bg, border_radius=8)
            pygame.draw.rect(surface, (255, 180, 40), frenzy_bg, width=2, border_radius=8)
            frenzy_txt = self.hud_font.render(f"FRENZY 2X ({frenzy_timer:.1f}s)!", True, (255, 255, 255))
            frenzy_rect = frenzy_txt.get_rect(center=frenzy_bg.center)
            surface.blit(frenzy_txt, frenzy_rect)
        else:
            snack_lbl = self.small_font.render("SNACKS EATEN", True, (140, 160, 185))
            snack_rect = snack_lbl.get_rect(center=(self.width // 2, 20))
            surface.blit(snack_lbl, snack_rect)
            snack_val = self.hud_val_font.render(f"{snacks_eaten}", True, (100, 240, 180))
            snack_val_rect = snack_val.get_rect(center=(self.width // 2, 42))
            surface.blit(snack_val, snack_val_rect)

        # 4. Right side: Difficulty, Walls, Sound
        right_x = self.width - 25
        sound_icon = "MUTED" if sound_muted else "AUDIO ON"
        sound_col = (180, 100, 100) if sound_muted else (120, 220, 140)
        sound_surf = self.small_font.render(f"[M] {sound_icon}", True, sound_col)
        sound_rect = sound_surf.get_rect(topright=(right_x, 12))
        surface.blit(sound_surf, sound_rect)

        mode_str = "WRAP" if wrap_walls else "SOLID"
        diff_str = f"{difficulty.upper()} | {mode_str}"
        diff_surf = self.small_font.render(diff_str, True, (130, 160, 200))
        diff_rect = diff_surf.get_rect(topright=(right_x, 38))
        surface.blit(diff_surf, diff_rect)

    def draw_menu(self, surface: pygame.Surface, time_sec: float, difficulty: str, wrap_walls: bool, sound_muted: bool):
        """Draws the animated title and menu screen."""
        # Backdrop overlay
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((12, 16, 25, 240))
        surface.blit(dim_surf, (0, 0))

        # Title with breathing scale and neon drop-shadow
        bounce = math.sin(time_sec * 3.5) * 5
        title_y = int(self.height * 0.12 + bounce)

        title_shadow = self.title_font.render("SNACK ATTACK!", True, (0, 140, 120))
        surface.blit(title_shadow, (self.width // 2 - title_shadow.get_width() // 2 + 3, title_y + 3))

        title_fg = self.title_font.render("SNACK ATTACK!", True, (0, 255, 190))
        surface.blit(title_fg, (self.width // 2 - title_fg.get_width() // 2, title_y))

        sub_txt = self.subtitle_font.render("The Ultimate Arcade Snake & Snack Feast!", True, (240, 240, 250))
        surface.blit(sub_txt, (self.width // 2 - sub_txt.get_width() // 2, title_y + 60))

        # Snack Showcase Card
        card_w, card_h = 820, 145
        card_x = (self.width - card_w) // 2
        card_y = title_y + 105
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(surface, (20, 26, 40), card_rect, border_radius=12)
        pygame.draw.rect(surface, (45, 60, 85), card_rect, width=1, border_radius=12)

        card_title = self.small_font.render("SNACK MENU & POWERUPS", True, (130, 175, 230))
        surface.blit(card_title, (card_x + 24, card_y + 12))

        # Render snack icons and labels
        spacing = card_w // (len(self.preview_snacks) + 1)
        for i, s in enumerate(self.preview_snacks):
            sx = card_x + spacing * (i + 1)
            sy = card_y + 60
            s.age = time_sec + i * 0.4
            s.duration = 10.0
            s.max_duration = 10.0
            # Draw preview
            s.grid_x, s.grid_y = 0, 0
            s.draw(surface, cell_size=36, offset_x=sx - 18, offset_y=sy - 18)

            name_lbl = self.small_font.render(s.data["name"], True, (240, 240, 240))
            pts_lbl = self.small_font.render(s.data["desc"], True, (255, 215, 60))
            surface.blit(name_lbl, name_lbl.get_rect(center=(sx, sy + 32)))
            surface.blit(pts_lbl, pts_lbl.get_rect(center=(sx, sy + 48)))

        # Options & Settings Buttons
        btn_y = card_y + card_h + 30
        pulse_alpha = int(200 + 55 * math.sin(time_sec * 6.0))

        # Big START GAME button
        start_rect = pygame.Rect(self.width // 2 - 180, btn_y, 360, 52)
        pygame.draw.rect(surface, (0, 190, 140), start_rect, border_radius=10)
        pygame.draw.rect(surface, (120, 255, 220), start_rect, width=2, border_radius=10)
        start_txt = self.btn_font.render("PRESS [SPACE] OR [ENTER] TO PLAY", True, (10, 30, 25))
        surface.blit(start_txt, start_txt.get_rect(center=start_rect.center))

        # Quick Toggles Box
        toggles_y = btn_y + 70
        toggles_w = 680
        toggles_x = (self.width - toggles_w) // 2

        t1 = f"[D] DIFFICULTY: {difficulty.upper()}"
        t2 = f"[W] WALLS: {'WRAP (PAC-MAN)' if wrap_walls else 'SOLID (CLASSIC)'}"
        t3 = f"[M] SOUND: {'MUTED' if sound_muted else 'ON'}"

        self._draw_pill_btn(surface, toggles_x, toggles_y, 210, 38, t1, (50, 110, 210))
        self._draw_pill_btn(surface, toggles_x + 230, toggles_y, 230, 38, t2, (180, 90, 220))
        self._draw_pill_btn(surface, toggles_x + 480, toggles_y, 190, 38, t3, (60, 180, 120))

        # Controls Hint Footer
        footer_y = toggles_y + 60
        ctrls = "Controls: Arrow Keys or W-A-S-D to Move | [P] Pause | [R] Restart | [ESC] Quit"
        foot_surf = self.small_font.render(ctrls, True, (140, 160, 190))
        surface.blit(foot_surf, foot_surf.get_rect(center=(self.width // 2, footer_y)))

    def _draw_pill_btn(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, text: str, col: tuple):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (24, 30, 46), rect, border_radius=8)
        pygame.draw.rect(surface, col, rect, width=2, border_radius=8)
        lbl = self.small_font.render(text, True, (240, 245, 255))
        surface.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_pause(self, surface: pygame.Surface):
        """Draws pause overlay."""
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((10, 14, 22, 180))
        surface.blit(dim_surf, (0, 0))

        card_w, card_h = 420, 220
        card_rect = pygame.Rect((self.width - card_w) // 2, (self.height - card_h) // 2, card_w, card_h)
        pygame.draw.rect(surface, (18, 24, 36), card_rect, border_radius=16)
        pygame.draw.rect(surface, (0, 200, 180), card_rect, width=2, border_radius=16)

        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(self.width // 2, card_rect.y + 45)))

        sub1 = self.hud_font.render("Press [SPACE] or [P] to Resume", True, (120, 230, 190))
        surface.blit(sub1, sub1.get_rect(center=(self.width // 2, card_rect.y + 105)))

        sub2 = self.btn_font.render("[R] Restart   |   [ESC] Exit to Menu", True, (150, 175, 205))
        surface.blit(sub2, sub2.get_rect(center=(self.width // 2, card_rect.y + 155)))

    def draw_game_over(self, surface: pygame.Surface, score: int, snacks_eaten: int,
                       snake_length: int, is_new_record: bool, time_sec: float):
        """Draws Game Over screen with score card and stats."""
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((12, 14, 20, 215))
        surface.blit(dim_surf, (0, 0))

        card_w, card_h = 520, 360
        card_rect = pygame.Rect((self.width - card_w) // 2, (self.height - card_h) // 2, card_w, card_h)
        pygame.draw.rect(surface, (20, 26, 40), card_rect, border_radius=18)
        border_col = (255, 215, 0) if is_new_record else (225, 45, 55)
        pygame.draw.rect(surface, border_col, card_rect, width=3, border_radius=18)

        # Header Title
        go_title = self.title_font.render("GAME OVER", True, (245, 60, 70))
        surface.blit(go_title, go_title.get_rect(center=(self.width // 2, card_rect.y + 45)))

        # New Record Celebration Banner
        if is_new_record:
            pulse = 1.0 + 0.05 * math.sin(time_sec * 8.0)
            rec_surf = self.hud_font.render("🎉 NEW HIGH SCORE! 🎉", True, (255, 225, 50))
            rec_rect = rec_surf.get_rect(center=(self.width // 2, card_rect.y + 90))
            surface.blit(rec_surf, rec_rect)
        else:
            sub = self.subtitle_font.render("Better luck on your next snack run!", True, (150, 170, 195))
            surface.blit(sub, sub.get_rect(center=(self.width // 2, card_rect.y + 85)))

        # Stats Card Body
        stat_y = card_rect.y + 130
        self._draw_stat_row(surface, card_rect.x + 40, stat_y, card_w - 80, "FINAL SCORE", f"{score:,}", (255, 235, 90))
        self._draw_stat_row(surface, card_rect.x + 40, stat_y + 38, card_w - 80, "BEST SCORE", f"{self.high_score:,}", (255, 205, 50))
        self._draw_stat_row(surface, card_rect.x + 40, stat_y + 76, card_w - 80, "SNACKS EATEN", f"{snacks_eaten}", (100, 230, 170))
        self._draw_stat_row(surface, card_rect.x + 40, stat_y + 114, card_w - 80, "SNAKE LENGTH", f"{snake_length} segments", (140, 200, 255))

        # Bottom Actions
        act_y = card_rect.y + card_h - 45
        act_lbl = self.btn_font.render("Press [SPACE] or [R] to Play Again   |   [ESC] Menu", True, (240, 245, 255))
        surface.blit(act_lbl, act_lbl.get_rect(center=(self.width // 2, act_y)))

    def _draw_stat_row(self, surface: pygame.Surface, x: int, y: int, w: int, label: str, value: str, val_col: tuple):
        lbl_surf = self.hud_font.render(label, True, (140, 160, 185))
        surface.blit(lbl_surf, (x, y))
        val_surf = self.hud_val_font.render(value, True, val_col)
        surface.blit(val_surf, (x + w - val_surf.get_width(), y))
        # Subtle dotted/line separator
        pygame.draw.line(surface, (35, 45, 65), (x, y + 28), (x + w, y + 28), 1)
