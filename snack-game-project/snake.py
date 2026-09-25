"""
Snake entity module with expressive cartoon eyes, flicking tongue,
gradient body rendering, directional input buffering, and frenzy state.
"""
import math
import random
import pygame

# Directions as (dx, dy)
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

OPPOSITE_DIR = {
    DIR_UP: DIR_DOWN,
    DIR_DOWN: DIR_UP,
    DIR_LEFT: DIR_RIGHT,
    DIR_RIGHT: DIR_LEFT,
}

class Snake:
    def __init__(self, start_x: int, start_y: int, length: int = 4):
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.input_queue = []
        
        # Segments list of (grid_x, grid_y)
        self.body = [(start_x - i, start_y) for i in range(length)]
        self.growth_pending = 0
        
        # Animation states
        self.tongue_timer = 0.0
        self.tongue_out = False
        self.frenzy_timer = 0.0
        self.alive = True
        self.time_alive = 0.0

    @property
    def head(self):
        return self.body[0]

    @property
    def is_frenzy(self) -> bool:
        return self.frenzy_timer > 0

    def queue_direction(self, new_dir: tuple):
        """Buffers direction input preventing 180-degree instant suicide turns."""
        last_dir = self.input_queue[-1] if self.input_queue else self.direction
        if new_dir != last_dir and new_dir != OPPOSITE_DIR.get(last_dir):
            if len(self.input_queue) < 3:
                self.input_queue.append(new_dir)

    def trigger_frenzy(self, duration: float = 8.0):
        self.frenzy_timer = duration

    def update(self, dt: float, cols: int, rows: int, wrap_walls: bool = False) -> tuple:
        """
        Advances the snake one grid step.
        Returns (moved_successfully, ate_self, hit_wall).
        """
        self.time_alive += dt
        if self.frenzy_timer > 0:
            self.frenzy_timer = max(0.0, self.frenzy_timer - dt)

        # Tongue flick timer
        self.tongue_timer += dt
        if self.tongue_timer >= 2.0:
            self.tongue_out = True
            if self.tongue_timer >= 2.4:
                self.tongue_out = False
                self.tongue_timer = 0.0

        # Apply queued direction
        if self.input_queue:
            self.direction = self.input_queue.pop(0)

        hx, hy = self.head
        dx, dy = self.direction
        new_hx = hx + dx
        new_hy = hy + dy

        hit_wall = False
        if wrap_walls:
            new_hx = new_hx % cols
            new_hy = new_hy % rows
        else:
            if new_hx < 0 or new_hx >= cols or new_hy < 0 or new_hy >= rows:
                hit_wall = True
                self.alive = False
                return False, False, True

        new_head = (new_hx, new_hy)

        # Self collision (excluding the very tip of tail if not growing)
        check_body = self.body[:-1] if self.growth_pending == 0 else self.body
        if new_head in check_body:
            self.alive = False
            return False, True, False

        # Move body
        self.body.insert(0, new_head)
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()

        return True, False, False

    def grow(self, amount: int = 1):
        self.growth_pending += amount

    def draw(self, surface: pygame.Surface, cell_size: int, offset_x: int = 0, offset_y: int = 0):
        if not self.body:
            return

        body_len = len(self.body)

        # 1. Draw body segments from tail to head
        for i in range(body_len - 1, 0, -1):
            curr_pt = self.body[i]
            prev_pt = self.body[i - 1]

            cx = offset_x + curr_pt[0] * cell_size + cell_size // 2
            cy = offset_y + curr_pt[1] * cell_size + cell_size // 2

            # Taper tail slightly
            taper_factor = 0.72 + 0.28 * min(1.0, (body_len - i) / 4.0)
            seg_radius = int((cell_size * 0.44) * taper_factor)

            # Color calculation
            progress = i / max(1, body_len)
            if self.is_frenzy:
                # Rainbow / Fire cycling
                hue_shift = (self.time_alive * 4.0 + progress * 2.0) % 1.0
                seg_color = self._get_frenzy_color(hue_shift)
                glow_color = (255, 200, 50)
            else:
                # Emerald green to electric lime / teal gradient
                g = int(220 - 70 * progress)
                b = int(120 + 80 * (1.0 - progress))
                r = int(20 + 40 * progress)
                seg_color = (r, g, b)
                glow_color = (max(0, r - 15), max(0, g - 25), max(0, b - 15))

            # Connect current segment to previous segment for smooth continuous body
            px = offset_x + prev_pt[0] * cell_size + cell_size // 2
            py = offset_y + prev_pt[1] * cell_size + cell_size // 2

            # Only connect if adjacent (not wrapping around screen)
            if abs(curr_pt[0] - prev_pt[0]) <= 1 and abs(curr_pt[1] - prev_pt[1]) <= 1:
                pygame.draw.line(surface, glow_color, (cx, cy), (px, py), seg_radius * 2)
                pygame.draw.line(surface, seg_color, (cx, cy), (px, py), int(seg_radius * 1.7))

            # Draw rounded joint
            pygame.draw.circle(surface, glow_color, (cx, cy), seg_radius)
            pygame.draw.circle(surface, seg_color, (cx, cy), max(2, int(seg_radius * 0.85)))
            # Subtle glossy reflection
            pygame.draw.circle(surface, (255, 255, 255, 60), (cx - 2, cy - 2), max(1, int(seg_radius * 0.3)))

        # 2. Draw Snake Head
        head_pos = self.head
        hx = offset_x + head_pos[0] * cell_size + cell_size // 2
        hy = offset_y + head_pos[1] * cell_size + cell_size // 2
        head_r = int(cell_size * 0.46)

        # Frenzy head aura
        if self.is_frenzy:
            frenzy_aura = pygame.Surface((cell_size * 2, cell_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(frenzy_aura, (255, 120, 0, 90), (cell_size, cell_size), int(head_r * 1.5))
            surface.blit(frenzy_aura, (hx - cell_size, hy - cell_size))

        # Main head circle / rounded rect
        head_color = (255, 100, 30) if self.is_frenzy else (35, 225, 115)
        head_border = (200, 60, 10) if self.is_frenzy else (15, 160, 75)

        pygame.draw.circle(surface, head_border, (hx, hy), head_r + 1)
        pygame.draw.circle(surface, head_color, (hx, hy), head_r)

        # 3. Flicking Tongue
        if self.tongue_out and self.alive:
            self._draw_tongue(surface, hx, hy, cell_size)

        # 4. Expressive Eyes
        self._draw_eyes(surface, hx, hy, head_r)

    def _draw_tongue(self, surface: pygame.Surface, hx: int, hy: int, cell_size: int):
        dx, dy = self.direction
        t_len = int(cell_size * 0.45)
        # Base of tongue at front of head
        bx = hx + dx * int(cell_size * 0.42)
        by = hy + dy * int(cell_size * 0.42)
        tx = bx + dx * t_len
        ty = by + dy * t_len

        # Fork tips
        perp_x, perp_y = -dy, dx
        fork_size = 4
        tip1 = (tx + perp_x * fork_size + dx * 3, ty + perp_y * fork_size + dy * 3)
        tip2 = (tx - perp_x * fork_size + dx * 3, ty - perp_y * fork_size + dy * 3)

        pygame.draw.line(surface, (235, 50, 70), (bx, by), (tx, ty), 2)
        pygame.draw.line(surface, (235, 50, 70), (tx, ty), tip1, 2)
        pygame.draw.line(surface, (235, 50, 70), (tx, ty), tip2, 2)

    def _draw_eyes(self, surface: pygame.Surface, hx: int, hy: int, head_r: int):
        dx, dy = self.direction
        # Eye offset perpendicular to movement direction
        perp_x, perp_y = -dy, dx
        eye_spacing = int(head_r * 0.48)
        forward_offset = int(head_r * 0.28)
        eye_r = max(3, int(head_r * 0.36))
        pupil_r = max(2, int(eye_r * 0.55))

        eye1_center = (hx + perp_x * eye_spacing + dx * forward_offset,
                       hy + perp_y * eye_spacing + dy * forward_offset)
        eye2_center = (hx - perp_x * eye_spacing + dx * forward_offset,
                       hy - perp_y * eye_spacing + dy * forward_offset)

        for ec in [eye1_center, eye2_center]:
            # White eye ball
            pygame.draw.circle(surface, (255, 255, 255), ec, eye_r)
            pygame.draw.circle(surface, (40, 40, 40), ec, eye_r, 1)

            if not self.alive:
                # Cute 'X' eyes on death!
                arm = int(eye_r * 0.65)
                pygame.draw.line(surface, (200, 30, 30), (ec[0] - arm, ec[1] - arm), (ec[0] + arm, ec[1] + arm), 2)
                pygame.draw.line(surface, (200, 30, 30), (ec[0] - arm, ec[1] + arm), (ec[0] + arm, ec[1] - arm), 2)
            else:
                # Pupil looking toward moving direction
                pupil_center = (ec[0] + int(dx * eye_r * 0.4), ec[1] + int(dy * eye_r * 0.4))
                pupil_col = (20, 20, 30) if not self.is_frenzy else (180, 20, 10)
                pygame.draw.circle(surface, pupil_col, pupil_center, pupil_r)

                # Cute anime eye shine
                shine_pos = (pupil_center[0] - 1, pupil_center[1] - 1)
                pygame.draw.circle(surface, (255, 255, 255), shine_pos, max(1, pupil_r // 2))

    def _get_frenzy_color(self, t: float) -> tuple:
        """Returns rainbow color cycle for frenzy mode."""
        r = int((math.sin(t * 2 * math.pi) * 0.5 + 0.5) * 255)
        g = int((math.sin((t + 0.33) * 2 * math.pi) * 0.5 + 0.5) * 200)
        b = int((math.sin((t + 0.66) * 2 * math.pi) * 0.5 + 0.5) * 255)
        return (max(60, r), max(30, g), max(20, b))

if __name__ == "__main__":
    from main import main
    main()

