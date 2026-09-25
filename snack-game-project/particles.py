"""
Particle system and floating text animations for vibrant game feel.
"""
import random
import math
import pygame

class Particle:
    def __init__(self, x: float, y: float, color: tuple, size: float, vx: float, vy: float, lifetime: float, is_sparkle: bool = False):
        self.x = x
        self.y = y
        self.color = color
        self.base_size = size
        self.size = size
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.is_sparkle = is_sparkle
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

    def update(self, dt: float) -> bool:
        """Update particle position, size and lifetime. Returns True if alive."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        self.x += self.vx * dt
        self.y += self.vy * dt
        # Drag/friction
        self.vx *= 0.94
        self.vy *= 0.94
        self.rotation += self.rot_speed * dt

        progress = max(0.0, self.lifetime / self.max_lifetime)
        self.size = self.base_size * progress
        return True

    def draw(self, surface: pygame.Surface):
        if self.size < 0.5:
            return

        progress = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        alpha = int(255 * progress)

        # Sparkle star or glowing circle
        if self.is_sparkle:
            s_size = int(self.size * 2.2)
            if s_size < 2:
                return
            star_surf = pygame.Surface((s_size * 2, s_size * 2), pygame.SRCALPHA)
            cx, cy = s_size, s_size
            col = (*self.color[:3], alpha)
            # Draw diamond / 4-point star
            pygame.draw.line(star_surf, col, (cx - s_size, cy), (cx + s_size, cy), max(1, int(self.size * 0.7)))
            pygame.draw.line(star_surf, col, (cx, cy - s_size), (cx, cy + s_size), max(1, int(self.size * 0.7)))
            pygame.draw.circle(star_surf, (255, 255, 255, alpha), (cx, cy), max(1, int(s_size * 0.3)))
            surface.blit(star_surf, (self.x - cx, self.y - cy))
        else:
            p_surf = pygame.Surface((int(self.size * 2) + 2, int(self.size * 2) + 2), pygame.SRCALPHA)
            col = (*self.color[:3], alpha)
            pygame.draw.circle(p_surf, col, (int(self.size) + 1, int(self.size) + 1), int(self.size))
            surface.blit(p_surf, (self.x - self.size - 1, self.y - self.size - 1))


class FloatingText:
    def __init__(self, text: str, x: float, y: float, color: tuple, font: pygame.font.Font, duration: float = 0.9, scale_burst: bool = False):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = font
        self.duration = duration
        self.max_duration = duration
        self.vy = -45.0  # Moves upward
        self.scale_burst = scale_burst

    def update(self, dt: float) -> bool:
        self.duration -= dt
        if self.duration <= 0:
            return False
        self.y += self.vy * dt
        self.vy *= 0.96  # Decelerates
        return True

    def draw(self, surface: pygame.Surface):
        progress = max(0.0, min(1.0, self.duration / self.max_duration))
        alpha = int(255 * (progress ** 0.7))

        # Render text with shadow for crisp contrast
        fg_col = (*self.color[:3], alpha)
        shadow_col = (0, 0, 0, int(alpha * 0.7))

        rendered_shadow = self.font.render(self.text, True, shadow_col[:3])
        rendered_shadow.set_alpha(shadow_col[3])
        
        rendered_fg = self.font.render(self.text, True, fg_col[:3])
        rendered_fg.set_alpha(fg_col[3])

        rect = rendered_fg.get_rect(center=(self.x, self.y))
        surface.blit(rendered_shadow, (rect.x + 2, rect.y + 2))
        surface.blit(rendered_fg, rect)


class ParticleManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []

    def emit_snack_burst(self, x: float, y: float, colors: list, count: int = 16, is_bonus: bool = False):
        """Spawns an energetic burst of colorful particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 200) if not is_bonus else random.uniform(70, 260)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(3, 7) if not is_bonus else random.uniform(4, 9)
            color = random.choice(colors)
            lifetime = random.uniform(0.4, 0.85) if not is_bonus else random.uniform(0.6, 1.1)
            is_sparkle = is_bonus and random.random() < 0.6
            self.particles.append(Particle(x, y, color, size, vx, vy, lifetime, is_sparkle))

    def emit_trail(self, x: float, y: float, color: tuple):
        """Soft movement trail particle."""
        vx = random.uniform(-10, 10)
        vy = random.uniform(-10, 10)
        size = random.uniform(2, 4.5)
        lifetime = random.uniform(0.2, 0.4)
        self.particles.append(Particle(x, y, color, size, vx, vy, lifetime))

    def add_floating_text(self, text: str, x: float, y: float, color: tuple, font: pygame.font.Font, is_big: bool = False):
        dur = 1.1 if is_big else 0.85
        self.floating_texts.append(FloatingText(text, x, y, color, font, duration=dur, scale_burst=is_big))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            p.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface)

    def clear(self):
        self.particles.clear()
        self.floating_texts.clear()
