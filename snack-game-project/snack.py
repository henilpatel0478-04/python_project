"""
Snack definitions and procedural vector rendering for delicious foods.
Includes Apple, Pizza, Donut, Burger, Taco, Chili Pepper, and Golden Sundae.
"""
import math
import random
import pygame

class SnackType:
    APPLE = "Apple"
    PIZZA = "Pizza"
    DONUT = "Donut"
    BURGER = "Burger"
    TACO = "Taco"
    CHILI = "Chili Pepper"
    SUNDAE = "Golden Sundae"

SNACK_DATA = {
    SnackType.APPLE: {
        "points": 10,
        "growth": 1,
        "weight": 50,
        "colors": [(230, 40, 50), (255, 100, 110), (120, 200, 50)],
        "name": "Apple",
        "desc": "+10 Pts",
    },
    SnackType.PIZZA: {
        "points": 25,
        "growth": 2,
        "weight": 22,
        "colors": [(255, 185, 30), (210, 45, 30), (200, 130, 50)],
        "name": "Pizza",
        "desc": "+25 Pts",
    },
    SnackType.DONUT: {
        "points": 35,
        "growth": 2,
        "weight": 16,
        "colors": [(255, 105, 180), (240, 180, 100), (0, 240, 255)],
        "name": "Donut",
        "desc": "+35 Pts",
    },
    SnackType.TACO: {
        "points": 40,
        "growth": 2,
        "weight": 12,
        "colors": [(245, 200, 60), (70, 180, 50), (210, 45, 30)],
        "name": "Taco",
        "desc": "+40 Pts",
    },
    SnackType.BURGER: {
        "points": 50,
        "growth": 3,
        "weight": 8,
        "colors": [(215, 145, 65), (75, 185, 55), (105, 55, 25)],
        "name": "Burger",
        "desc": "+50 Pts",
    },
    SnackType.CHILI: {
        "points": 30,
        "growth": 1,
        "weight": 10,
        "colors": [(255, 45, 20), (255, 140, 0), (60, 180, 40)],
        "name": "Chili",
        "desc": "2X FRENZY",
        "is_powerup": True,
    },
    SnackType.SUNDAE: {
        "points": 100,
        "growth": 2,
        "weight": 0,  # Spawned specially via bonus timer
        "colors": [(255, 215, 0), (255, 240, 180), (240, 20, 60)],
        "name": "Sundae",
        "desc": "+100 BONUS",
        "is_bonus": True,
    }
}


class Snack:
    def __init__(self, grid_x: int, grid_y: int, snack_type: str = SnackType.APPLE, duration: float = None):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = snack_type
        self.data = SNACK_DATA[snack_type]
        self.points = self.data["points"]
        self.growth = self.data["growth"]
        self.colors = self.data["colors"]
        self.is_bonus = self.data.get("is_bonus", False)
        self.is_powerup = self.data.get("is_powerup", False)
        
        self.duration = duration
        self.max_duration = duration if duration is not None else 0.0
        self.age = 0.0
        self.alive = True

    def update(self, dt: float) -> bool:
        self.age += dt
        if self.duration is not None:
            self.duration -= dt
            if self.duration <= 0:
                self.alive = False
                return False
        return True

    def draw(self, surface: pygame.Surface, cell_size: int, offset_x: int = 0, offset_y: int = 0):
        cx = offset_x + self.grid_x * cell_size + cell_size // 2
        cy = offset_y + self.grid_y * cell_size + cell_size // 2
        r = int(cell_size * 0.42)

        # Gentle pulsing breath effect
        pulse = 1.0 + 0.08 * math.sin(self.age * 5.0)
        draw_r = int(r * pulse)

        # Bonus snack countdown ring and glowing aura
        if self.is_bonus and self.max_duration > 0:
            glow_surf = pygame.Surface((cell_size * 2, cell_size * 2), pygame.SRCALPHA)
            aura_alpha = int(70 + 40 * math.sin(self.age * 8.0))
            pygame.draw.circle(glow_surf, (255, 215, 0, aura_alpha), (cell_size, cell_size), int(cell_size * 0.75))
            surface.blit(glow_surf, (cx - cell_size, cy - cell_size))

            # Timer arc
            progress = max(0.0, self.duration / self.max_duration)
            arc_rect = pygame.Rect(cx - cell_size // 2 - 2, cy - cell_size // 2 - 2, cell_size + 4, cell_size + 4)
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * progress)
            try:
                pygame.draw.arc(surface, (255, 230, 80), arc_rect, start_angle, end_angle, 3)
            except Exception:
                pass

        elif self.is_powerup:
            # Chili fiery aura
            glow_surf = pygame.Surface((cell_size * 2, cell_size * 2), pygame.SRCALPHA)
            aura_alpha = int(80 + 50 * math.sin(self.age * 12.0))
            pygame.draw.circle(glow_surf, (255, 80, 0, aura_alpha), (cell_size, cell_size), int(cell_size * 0.65))
            surface.blit(glow_surf, (cx - cell_size, cy - cell_size))

        # Render specific snack graphic
        if self.type == SnackType.APPLE:
            self._draw_apple(surface, cx, cy, draw_r)
        elif self.type == SnackType.PIZZA:
            self._draw_pizza(surface, cx, cy, draw_r)
        elif self.type == SnackType.DONUT:
            self._draw_donut(surface, cx, cy, draw_r)
        elif self.type == SnackType.BURGER:
            self._draw_burger(surface, cx, cy, draw_r)
        elif self.type == SnackType.TACO:
            self._draw_taco(surface, cx, cy, draw_r)
        elif self.type == SnackType.CHILI:
            self._draw_chili(surface, cx, cy, draw_r)
        elif self.type == SnackType.SUNDAE:
            self._draw_sundae(surface, cx, cy, draw_r)

    def _draw_apple(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        # Two overlapping lobes for apple silhouette
        lobe_offset = int(r * 0.35)
        lobe_r = int(r * 0.82)
        pygame.draw.circle(surface, (220, 30, 40), (cx - lobe_offset, cy + 2), lobe_r)
        pygame.draw.circle(surface, (240, 45, 55), (cx + lobe_offset, cy + 2), lobe_r)

        # Highlight reflection
        pygame.draw.circle(surface, (255, 140, 150), (cx - int(r * 0.45), cy - int(r * 0.3)), max(2, int(r * 0.25)))

        # Stem
        pygame.draw.line(surface, (95, 55, 20), (cx, cy - int(r * 0.4)), (cx + 2, cy - r - 2), max(2, int(r * 0.18)))
        # Leaf
        leaf_pts = [(cx + 2, cy - r), (cx + int(r * 0.7), cy - r - 4), (cx + int(r * 0.5), cy - int(r * 0.5))]
        pygame.draw.polygon(surface, (70, 190, 50), leaf_pts)

    def _draw_pizza(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        # Triangular cheese slice
        p_top = (cx, cy - r - 2)
        p_bl = (cx - int(r * 0.9), cy + int(r * 0.8))
        p_br = (cx + int(r * 0.9), cy + int(r * 0.8))

        # Crust (curved bottom)
        pygame.draw.line(surface, (200, 130, 50), p_bl, p_br, max(3, int(r * 0.35)))

        # Cheese body
        pygame.draw.polygon(surface, (255, 195, 35), [p_top, p_bl, p_br])

        # Pepperoni slices
        pep_r = max(2, int(r * 0.22))
        pep_positions = [
            (cx, cy + int(r * 0.25)),
            (cx - int(r * 0.4), cy + int(r * 0.45)),
            (cx + int(r * 0.35), cy + int(r * 0.38)),
            (cx - int(r * 0.1), cy - int(r * 0.2)),
        ]
        for px, py in pep_positions:
            pygame.draw.circle(surface, (190, 35, 25), (px, py), pep_r)
            pygame.draw.circle(surface, (240, 70, 60), (px - 1, py - 1), max(1, pep_r - 2))

    def _draw_donut(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        # Golden dough base
        pygame.draw.circle(surface, (225, 160, 85), (cx, cy), r)
        # Pink glaze
        pygame.draw.circle(surface, (255, 105, 180), (cx, cy), int(r * 0.88))
        # Center hole
        hole_r = max(3, int(r * 0.38))
        # Clear hole by drawing dark center
        pygame.draw.circle(surface, (22, 26, 36), (cx, cy), hole_r)
        pygame.draw.circle(surface, (200, 140, 70), (cx, cy), hole_r, 1)

        # Sprinkles
        sprinkle_colors = [(0, 240, 255), (255, 255, 255), (255, 230, 40), (120, 255, 120)]
        for i, col in enumerate(sprinkle_colors):
            angle = i * (math.pi / 2) + 0.4
            dist = r * 0.62
            sx = int(cx + math.cos(angle) * dist)
            sy = int(cy + math.sin(angle) * dist)
            pygame.draw.rect(surface, col, (sx - 2, sy - 1, 4, 3))

    def _draw_burger(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        bw = int(r * 1.8)
        bh = max(3, int(r * 0.28))

        # Bottom bun
        bb_rect = pygame.Rect(cx - bw // 2, cy + int(r * 0.4), bw, bh)
        pygame.draw.rect(surface, (215, 145, 65), bb_rect, border_radius=bh // 2)

        # Patty
        patty_rect = pygame.Rect(cx - bw // 2 + 1, cy + int(r * 0.15), bw - 2, bh)
        pygame.draw.rect(surface, (95, 45, 20), patty_rect, border_radius=2)

        # Melted Cheese
        cheese_pts = [(cx - bw // 2 + 2, cy + int(r * 0.12)), (cx + bw // 2 - 2, cy + int(r * 0.12)),
                      (cx, cy + int(r * 0.35))]
        pygame.draw.polygon(surface, (255, 210, 20), cheese_pts)

        # Lettuce (wavy green)
        lettuce_rect = pygame.Rect(cx - bw // 2 - 1, cy - int(r * 0.1), bw + 2, bh)
        pygame.draw.rect(surface, (65, 195, 45), lettuce_rect, border_radius=4)

        # Top bun (curved dome)
        tb_rect = pygame.Rect(cx - bw // 2, cy - int(r * 0.75), bw, int(r * 0.75))
        pygame.draw.ellipse(surface, (225, 155, 75), tb_rect)

        # Sesame seeds
        seed_col = (255, 245, 220)
        pygame.draw.circle(surface, seed_col, (cx - int(r * 0.4), cy - int(r * 0.45)), 1)
        pygame.draw.circle(surface, seed_col, (cx, cy - int(r * 0.55)), 1)
        pygame.draw.circle(surface, seed_col, (cx + int(r * 0.4), cy - int(r * 0.4)), 1)

    def _draw_taco(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        tw = int(r * 1.8)
        th = int(r * 1.3)
        # Curved folded taco shell
        shell_rect = pygame.Rect(cx - tw // 2, cy - th // 2 + 2, tw, th)
        # Shell
        pygame.draw.arc(surface, (245, 195, 50), shell_rect, 0, math.pi, max(4, int(r * 0.38)))
        # Fillings peaking out top: meat, greens, red tomato
        pygame.draw.circle(surface, (110, 50, 20), (cx - 4, cy - 2), max(2, int(r * 0.3)))
        pygame.draw.circle(surface, (70, 190, 50), (cx + 3, cy - 4), max(2, int(r * 0.32)))
        pygame.draw.circle(surface, (220, 40, 30), (cx - 1, cy - 5), max(2, int(r * 0.25)))
        # Cheese sprinkles
        pygame.draw.line(surface, (255, 225, 30), (cx - 6, cy - 6), (cx - 2, cy - 2), 2)
        pygame.draw.line(surface, (255, 225, 30), (cx + 1, cy - 7), (cx + 5, cy - 3), 2)

    def _draw_chili(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        # Fiery curved chili body
        pts = [
            (cx - int(r * 0.6), cy - int(r * 0.7)),
            (cx + int(r * 0.2), cy - int(r * 0.5)),
            (cx + int(r * 0.7), cy),
            (cx + int(r * 0.3), cy + int(r * 0.8)),
            (cx - int(r * 0.1), cy + int(r * 0.9)),
            (cx + int(r * 0.1), cy + int(r * 0.4)),
            (cx - int(r * 0.4), cy),
        ]
        pygame.draw.polygon(surface, (235, 30, 20), pts)
        pygame.draw.polygon(surface, (255, 110, 40), pts[:4])  # Highlight flame
        # Green chili stem & cap
        pygame.draw.circle(surface, (50, 180, 40), (cx - int(r * 0.5), cy - int(r * 0.65)), max(2, int(r * 0.25)))
        pygame.draw.line(surface, (40, 150, 30), (cx - int(r * 0.5), cy - int(r * 0.65)), (cx - int(r * 0.8), cy - r), 2)

    def _draw_sundae(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        # Sundae glass / bowl
        bowl_pts = [(cx - int(r * 0.7), cy + int(r * 0.1)), (cx + int(r * 0.7), cy + int(r * 0.1)),
                    (cx + int(r * 0.3), cy + int(r * 0.75)), (cx - int(r * 0.3), cy + int(r * 0.75))]
        pygame.draw.polygon(surface, (170, 220, 255), bowl_pts)
        # Base stem
        pygame.draw.rect(surface, (170, 220, 255), (cx - 2, cy + int(r * 0.75), 4, max(2, int(r * 0.25))))
        pygame.draw.line(surface, (170, 220, 255), (cx - int(r * 0.4), cy + r), (cx + int(r * 0.4), cy + r), 2)

        # Ice cream scoops (vanilla & strawberry swirls)
        pygame.draw.circle(surface, (255, 250, 230), (cx - int(r * 0.3), cy - int(r * 0.15)), int(r * 0.45))
        pygame.draw.circle(surface, (255, 170, 200), (cx + int(r * 0.3), cy - int(r * 0.15)), int(r * 0.45))
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy - int(r * 0.45)), int(r * 0.4))

        # Hot fudge drizzle
        fudge_pts = [(cx - int(r * 0.3), cy - int(r * 0.35)), (cx, cy - int(r * 0.2)), (cx + int(r * 0.3), cy - int(r * 0.35))]
        pygame.draw.lines(surface, (90, 45, 15), False, fudge_pts, 2)

        # Glossy Cherry on top!
        pygame.draw.circle(surface, (230, 20, 40), (cx, cy - int(r * 0.8)), max(2, int(r * 0.25)))
        pygame.draw.circle(surface, (255, 150, 160), (cx - 1, cy - int(r * 0.8) - 1), 1)
        pygame.draw.line(surface, (70, 160, 40), (cx, cy - int(r * 0.8)), (cx + 3, cy - r - 3), 1)


class SnackSpawner:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.snack_types = [t for t in SNACK_DATA.keys() if SNACK_DATA[t]["weight"] > 0]
        self.snack_weights = [SNACK_DATA[t]["weight"] for t in self.snack_types]
        self.snacks_eaten_count = 0
        self.bonus_timer = random.uniform(15.0, 25.0)

    def spawn_regular(self, occupied_positions: set) -> Snack:
        """Spawn a regular snack at an unoccupied grid cell."""
        valid_pos = self._get_free_position(occupied_positions)
        if not valid_pos:
            return None
        stype = random.choices(self.snack_types, weights=self.snack_weights, k=1)[0]
        return Snack(valid_pos[0], valid_pos[1], snack_type=stype)

    def spawn_bonus(self, occupied_positions: set) -> Snack:
        """Spawn a special Golden Sundae bonus snack with limited lifetime."""
        valid_pos = self._get_free_position(occupied_positions)
        if not valid_pos:
            return None
        return Snack(valid_pos[0], valid_pos[1], snack_type=SnackType.SUNDAE, duration=10.0)

    def _get_free_position(self, occupied_positions: set):
        all_cells = [(x, y) for x in range(self.cols) for y in range(self.rows)]
        free_cells = [c for c in all_cells if c not in occupied_positions]
        if not free_cells:
            return None
        return random.choice(free_cells)
