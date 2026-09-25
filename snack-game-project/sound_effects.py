"""
Procedural sound effect generator using Python's standard library math and struct.
Zero external audio files required! Synthesizes 8-bit retro arcade sounds directly into pygame.mixer.Sound.
"""
import math
import struct
import pygame

class SoundManager:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.muted = False
        self.sounds = {}
        self.enabled = False

        try:
            # Initialize mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._generate_all_sounds()
        except Exception as e:
            print(f"Warning: Audio device initialization failed ({e}). Running in silent mode.")
            self.enabled = False

    def _generate_sound(self, generator_fn, duration_sec: float) -> pygame.mixer.Sound:
        """Helper to create a pygame Sound from an audio waveform generator function."""
        total_samples = int(self.sample_rate * duration_sec)
        raw_bytes = bytearray()
        
        for i in range(total_samples):
            t = i / self.sample_rate
            val = generator_fn(t, duration_sec)
            # Clamp between -1.0 and 1.0
            val = max(-1.0, min(1.0, val))
            # Convert to signed 16-bit integer (-32768 to 32767)
            sample = int(val * 30000)
            raw_bytes.extend(struct.pack('<h', sample))
            
        return pygame.mixer.Sound(buffer=bytes(raw_bytes))

    def _generate_all_sounds(self):
        """Generates all the retro arcade sound effects procedurally."""
        # 1. Normal Munch Sound (quick cheerful chirp)
        def eat_wave(t, dur):
            progress = t / dur
            # Pitch rises quickly from 400 to 800 Hz
            freq = 420 + 450 * (progress ** 0.8)
            env = (1.0 - progress) ** 1.5
            square = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -0.4
            return square * env * 0.45

        # 2. Big Munch / Heavy Snack (crunchy bite)
        def big_eat_wave(t, dur):
            progress = t / dur
            freq = 280 + 350 * progress
            env = (1.0 - progress) ** 1.2
            # Blend triangle and square for punchy bite
            wave = (2.0 / math.pi) * math.asin(math.sin(2 * math.pi * freq * t))
            return wave * env * 0.55

        # 3. Bonus Snack Jingle (sweet arpeggio chime)
        def bonus_wave(t, dur):
            notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
            note_idx = min(int((t / dur) * len(notes)), len(notes) - 1)
            freq = notes[note_idx]
            sub_t = t % (dur / len(notes))
            sub_dur = dur / len(notes)
            env = math.exp(-6.0 * (sub_t / sub_dur))
            sine = math.sin(2 * math.pi * freq * t)
            sine2 = math.sin(4 * math.pi * freq * t) * 0.3
            return (sine + sine2) * env * 0.5

        # 4. Frenzy / Powerup Sweep (upward hyper slide with vibrato)
        def frenzy_wave(t, dur):
            progress = t / dur
            base_freq = 300 + 900 * (progress ** 1.3)
            vibrato = math.sin(2 * math.pi * 18 * t) * 40
            freq = base_freq + vibrato
            env = min(1.0, progress * 8.0) * (1.0 - progress)
            saw = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            return saw * env * 0.4

        # 5. Game Over Crash (deep rumble crash with pitch drop)
        def die_wave(t, dur):
            progress = t / dur
            freq = max(40.0, 320.0 * (1.0 - progress) ** 2)
            env = (1.0 - progress) ** 1.8
            # Low tone plus harsh noise
            pseudo_noise = math.sin(t * 12345.67)
            sine = math.sin(2 * math.pi * freq * t)
            return (sine * 0.7 + pseudo_noise * 0.3) * env * 0.65

        # 6. UI Click / Blip
        def click_wave(t, dur):
            progress = t / dur
            freq = 950 - 200 * progress
            env = (1.0 - progress) ** 3
            return math.sin(2 * math.pi * freq * t) * env * 0.35

        # 7. High Score Fanfare
        def high_score_wave(t, dur):
            # Joyful triumph progression
            notes = [440, 554, 659, 880, 1108]
            note_idx = min(int((t / dur) * len(notes)), len(notes) - 1)
            freq = notes[note_idx]
            sub_t = t % (dur / len(notes))
            sub_dur = dur / len(notes)
            env = math.exp(-4.5 * (sub_t / sub_dur))
            return (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)) * env * 0.5

        try:
            self.sounds['eat'] = self._generate_sound(eat_wave, 0.12)
            self.sounds['big_eat'] = self._generate_sound(big_eat_wave, 0.18)
            self.sounds['bonus'] = self._generate_sound(bonus_wave, 0.35)
            self.sounds['frenzy'] = self._generate_sound(frenzy_wave, 0.45)
            self.sounds['die'] = self._generate_sound(die_wave, 0.6)
            self.sounds['click'] = self._generate_sound(click_wave, 0.05)
            self.sounds['high_score'] = self._generate_sound(high_score_wave, 0.6)
        except Exception as e:
            print(f"Warning: Failed to compile procedural audio: {e}")

    def play(self, sound_name: str):
        """Play sound by name if audio is enabled and not muted."""
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def toggle_mute(self) -> bool:
        """Toggle mute state. Returns new muted state."""
        self.muted = not self.muted
        return self.muted
