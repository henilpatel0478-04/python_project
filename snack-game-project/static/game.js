/**
 * Snack Attack! - Canvas Arcade Game Engine & Flask API Integration
 */

// --- Retro Web Audio Synthesizer (Zero External Audio Files) ---
class RetroAudio {
    constructor() {
        this.ctx = null;
        this.muted = false;
    }

    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                this.ctx = new AudioCtx();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    playEat(isBonus = false) {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);

        const now = this.ctx.currentTime;
        if (isBonus) {
            // High chiming bonus sound
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(520, now);
            osc.frequency.exponentialRampToValueAtTime(1040, now + 0.15);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
            osc.start(now);
            osc.stop(now + 0.2);
        } else {
            // Standard crisp 8-bit blip
            osc.type = 'square';
            osc.frequency.setValueAtTime(320, now);
            osc.frequency.exponentialRampToValueAtTime(680, now + 0.08);
            gain.gain.setValueAtTime(0.18, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.09);
            osc.start(now);
            osc.stop(now + 0.09);
        }
    }

    playFrenzy() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        const freqs = [350, 440, 587, 740, 880];
        freqs.forEach((f, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(f, now + idx * 0.05);
            gain.gain.setValueAtTime(0.15, now + idx * 0.05);
            gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.05 + 0.12);
            osc.start(now + idx * 0.05);
            osc.stop(now + idx * 0.05 + 0.12);
        });
    }

    playCrash() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.exponentialRampToValueAtTime(30, now + 0.35);
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.38);

        osc.start(now);
        osc.stop(now + 0.38);
    }

    playHighScore() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
        const now = this.ctx.currentTime;
        notes.forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now + i * 0.1);
            gain.gain.setValueAtTime(0.25, now + i * 0.1);
            gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.1 + 0.25);
            osc.start(now + i * 0.1);
            osc.stop(now + i * 0.1 + 0.25);
        });
    }
}

// --- Snack Attack Game Engine ---
class SnackAttackGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.audio = new RetroAudio();

        // Grid Configuration (matches 760 x 600)
        this.cellSize = 20;
        this.cols = Math.floor(this.canvas.width / this.cellSize); // 38
        this.rows = Math.floor(this.canvas.height / this.cellSize); // 30

        // Game State
        this.state = 'MENU'; // 'MENU', 'PLAYING', 'PAUSED', 'GAMEOVER'
        this.score = 0;
        this.snacksEaten = 0;
        this.highScore = parseInt(document.getElementById('hudBest').textContent, 10) || 0;
        this.gameTime = 0;
        this.frenzyTimer = 0;
        this.shakeTimer = 0;
        this.shakeIntensity = 0;
        this.isNewHighScore = false;

        // Settings
        this.difficulty = 'Classic';
        this.speeds = { 'Chill': 8, 'Classic': 12, 'Speedy': 16, 'Frenzy': 21 };
        this.stepInterval = 1000 / this.speeds[this.difficulty];
        this.lastStepTime = 0;
        this.wallMode = 'solid'; // 'solid' or 'wrap'

        // Snake Model
        this.snake = [];
        this.dir = { x: 1, y: 0 };
        this.nextDir = { x: 1, y: 0 };
        this.growPending = 0;

        // Snack Spawner
        this.regularSnack = null;
        this.bonusSnack = null;
        this.particles = [];
        this.popups = [];

        // DOM elements
        this.dom = {
            hudScore: document.getElementById('hudScore'),
            hudBest: document.getElementById('hudBest'),
            hudSnacks: document.getElementById('hudSnacks'),
            hudMultiplier: document.getElementById('hudMultiplier'),
            frenzyIndicator: document.getElementById('frenzyIndicator'),
            hudTime: document.getElementById('hudTime'),
            globalHighScoreVal: document.getElementById('globalHighScoreVal'),
            startOverlay: document.getElementById('startOverlay'),
            pauseOverlay: document.getElementById('pauseOverlay'),
            gameOverOverlay: document.getElementById('gameOverOverlay'),
            finalScoreVal: document.getElementById('finalScoreVal'),
            finalSnacksVal: document.getElementById('finalSnacksVal'),
            finalLengthVal: document.getElementById('finalLengthVal'),
            finalTimeVal: document.getElementById('finalTimeVal'),
            playerNameInput: document.getElementById('playerNameInput'),
            scoreSubmitForm: document.getElementById('scoreSubmitForm'),
            submitFeedback: document.getElementById('submitFeedback'),
            btnToggleSound: document.getElementById('btnToggleSound'),
            btnToggleWalls: document.getElementById('btnToggleWalls'),
            btnCycleDiff: document.getElementById('btnCycleDiff'),
            difficultySelect: document.getElementById('difficultySelect'),
            wallModeSelect: document.getElementById('wallModeSelect'),
            leaderboardBody: document.getElementById('leaderboardBody'),
            snackGrid: document.getElementById('snackGrid')
        };

        this.initEventListeners();
        this.fetchLeaderboard();
        this.fetchSnackDefinitions();

        // Animation Loop
        this.lastFrameTime = performance.now();
        requestAnimationFrame((t) => this.gameLoop(t));
    }

    initEventListeners() {
        // Keyboard Controls
        window.addEventListener('keydown', (e) => {
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
                // Prevent scrolling when playing
                if (document.activeElement !== this.dom.playerNameInput) {
                    e.preventDefault();
                }
            }
            this.handleKey(e.key.toLowerCase());
        });

        // Start / Resume / Restart Buttons
        document.getElementById('btnStartGame').addEventListener('click', () => this.startGame());
        document.getElementById('btnResumeGame').addEventListener('click', () => this.togglePause());
        document.getElementById('btnPlayAgain').addEventListener('click', () => this.startGame());
        document.getElementById('btnQuickRestart').addEventListener('click', () => this.startGame());

        // Toolbar Buttons
        this.dom.btnToggleSound.addEventListener('click', () => {
            this.audio.muted = !this.audio.muted;
            this.dom.btnToggleSound.textContent = this.audio.muted ? '🔇 SOUND: OFF' : '🔊 SOUND: ON';
        });

        this.dom.btnToggleWalls.addEventListener('click', () => {
            this.wallMode = this.wallMode === 'solid' ? 'wrap' : 'solid';
            this.dom.wallModeSelect.value = this.wallMode;
            this.dom.btnToggleWalls.textContent = this.wallMode === 'solid' ? '🧱 SOLID WALLS' : '🌀 WRAP-AROUND';
        });

        this.dom.btnCycleDiff.addEventListener('click', () => {
            const diffs = ['Chill', 'Classic', 'Speedy', 'Frenzy'];
            const curIdx = diffs.indexOf(this.difficulty);
            this.difficulty = diffs[(curIdx + 1) % diffs.length];
            this.stepInterval = 1000 / this.speeds[this.difficulty];
            this.dom.difficultySelect.value = this.difficulty;
            this.dom.btnCycleDiff.textContent = `⚡ ${this.difficulty.toUpperCase()}`;
        });

        this.dom.difficultySelect.addEventListener('change', (e) => {
            this.difficulty = e.target.value;
            this.stepInterval = 1000 / this.speeds[this.difficulty];
            this.dom.btnCycleDiff.textContent = `⚡ ${this.difficulty.toUpperCase()}`;
        });

        this.dom.wallModeSelect.addEventListener('change', (e) => {
            this.wallMode = e.target.value;
            this.dom.btnToggleWalls.textContent = this.wallMode === 'solid' ? '🧱 SOLID WALLS' : '🌀 WRAP-AROUND';
        });

        // Mobile D-Pad Controls
        ['dpadUp', 'dpadDown', 'dpadLeft', 'dpadRight'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const dir = btn.getAttribute('data-dir');
                    if (dir === 'UP') this.setDirection(0, -1);
                    if (dir === 'DOWN') this.setDirection(0, 1);
                    if (dir === 'LEFT') this.setDirection(-1, 0);
                    if (dir === 'RIGHT') this.setDirection(1, 0);
                });
            }
        });

        // Refresh Leaderboard Button
        document.getElementById('btnRefreshLeaderboard').addEventListener('click', () => {
            this.fetchLeaderboard();
        });

        // Submit Score Form to Flask REST API
        this.dom.scoreSubmitForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitScoreToAPI();
        });
    }

    handleKey(key) {
        if (document.activeElement === this.dom.playerNameInput) return;

        if (this.state === 'MENU') {
            if (key === ' ' || key === 'enter') this.startGame();
            return;
        }

        if (this.state === 'GAMEOVER') {
            if (key === ' ' || key === 'enter') this.startGame();
            return;
        }

        if (key === 'p') {
            this.togglePause();
            return;
        }

        if (key === 'r') {
            this.startGame();
            return;
        }

        if (this.state !== 'PLAYING') return;

        if (key === 'arrowup' || key === 'w') this.setDirection(0, -1);
        else if (key === 'arrowdown' || key === 's') this.setDirection(0, 1);
        else if (key === 'arrowleft' || key === 'a') this.setDirection(-1, 0);
        else if (key === 'arrowright' || key === 'd') this.setDirection(1, 0);
    }

    setDirection(x, y) {
        if (this.snake.length > 1 && this.dir.x === -x && this.dir.y === -y) return;
        this.nextDir = { x, y };
    }

    startGame() {
        this.audio.init();
        this.hideAllOverlays();

        const startX = Math.floor(this.cols / 2);
        const startY = Math.floor(this.rows / 2);
        this.snake = [
            { x: startX, y: startY },
            { x: startX - 1, y: startY },
            { x: startX - 2, y: startY }
        ];

        this.dir = { x: 1, y: 0 };
        this.nextDir = { x: 1, y: 0 };
        this.growPending = 0;
        this.score = 0;
        this.snacksEaten = 0;
        this.gameTime = 0;
        this.frenzyTimer = 0;
        this.isNewHighScore = false;
        this.particles = [];
        this.popups = [];
        this.bonusSnack = null;

        this.spawnRegularSnack();
        this.state = 'PLAYING';
        this.updateHUD();
    }

    togglePause() {
        if (this.state === 'PLAYING') {
            this.state = 'PAUSED';
            this.dom.pauseOverlay.classList.add('active');
        } else if (this.state === 'PAUSED') {
            this.state = 'PLAYING';
            this.dom.pauseOverlay.classList.remove('active');
        }
    }

    hideAllOverlays() {
        this.dom.startOverlay.classList.remove('active');
        this.dom.pauseOverlay.classList.remove('active');
        this.dom.gameOverOverlay.classList.remove('active');
    }

    spawnRegularSnack() {
        const types = [
            { type: 'Apple', weight: 45 },
            { type: 'Pizza', weight: 20 },
            { type: 'Donut', weight: 15 },
            { type: 'Taco', weight: 12 },
            { type: 'Burger', weight: 8 },
            { type: 'Chili', weight: 10 }
        ];

        const totalWeight = types.reduce((acc, t) => acc + t.weight, 0);
        let rand = Math.random() * totalWeight;
        let chosenType = 'Apple';
        for (const t of types) {
            if (rand < t.weight) {
                chosenType = t.type;
                break;
            }
            rand -= t.weight;
        }

        const pos = this.findFreeGridCell();
        this.regularSnack = {
            type: chosenType,
            x: pos.x,
            y: pos.y,
            age: 0
        };
    }

    spawnBonusSundae() {
        const pos = this.findFreeGridCell();
        this.bonusSnack = {
            type: 'Sundae',
            x: pos.x,
            y: pos.y,
            duration: 8.5,
            maxDuration: 8.5,
            age: 0
        };
        this.addPopup(pos.x, pos.y, '⭐ BONUS SUNDAE!', '#ffd700');
    }

    findFreeGridCell() {
        let attempts = 0;
        while (attempts < 500) {
            const x = Math.floor(Math.random() * (this.cols - 2)) + 1;
            const y = Math.floor(Math.random() * (this.rows - 2)) + 1;
            const inSnake = this.snake.some(seg => seg.x === x && seg.y === y);
            const inSnack = this.regularSnack && this.regularSnack.x === x && this.regularSnack.y === y;
            if (!inSnake && !inSnack) {
                return { x, y };
            }
            attempts++;
        }
        return { x: 5, y: 5 };
    }

    // --- Game Logic Update Loop ---
    gameLoop(timestamp) {
        const dt = Math.min((timestamp - this.lastFrameTime) / 1000, 0.1);
        this.lastFrameTime = timestamp;

        if (this.state === 'PLAYING') {
            this.gameTime += dt;
            if (this.frenzyTimer > 0) {
                this.frenzyTimer -= dt;
                if (this.frenzyTimer <= 0) {
                    this.frenzyTimer = 0;
                    this.dom.frenzyIndicator.classList.remove('frenzy-active');
                    this.dom.hudMultiplier.textContent = '1X';
                }
            }

            if (this.bonusSnack) {
                this.bonusSnack.duration -= dt;
                if (this.bonusSnack.duration <= 0) {
                    this.bonusSnack = null;
                }
            }

            // Fixed step movement
            if (timestamp - this.lastStepTime >= this.stepInterval) {
                this.stepSnake();
                this.lastStepTime = timestamp;
            }

            this.updateHUD();
        }

        // Screen Shake decay
        if (this.shakeTimer > 0) {
            this.shakeTimer -= dt;
            if (this.shakeTimer < 0) this.shakeTimer = 0;
        }

        // Particle System update
        this.updateParticles(dt);

        // Render Frame
        this.render();

        requestAnimationFrame((t) => this.gameLoop(t));
    }

    stepSnake() {
        this.dir = { ...this.nextDir };
        const head = this.snake[0];
        let newX = head.x + this.dir.x;
        let newY = head.y + this.dir.y;

        // Wall collisions
        if (this.wallMode === 'wrap') {
            if (newX < 0) newX = this.cols - 1;
            else if (newX >= this.cols) newX = 0;
            if (newY < 0) newY = this.rows - 1;
            else if (newY >= this.rows) newY = 0;
        } else {
            if (newX < 0 || newX >= this.cols || newY < 0 || newY >= this.rows) {
                this.gameOver('Crashed into the arena wall!');
                return;
            }
        }

        // Self collision
        if (this.snake.some((seg, idx) => idx > 0 && seg.x === newX && seg.y === newY)) {
            this.gameOver('Ouch! Bit your own tail!');
            return;
        }

        const newHead = { x: newX, y: newY };
        this.snake.unshift(newHead);

        // Check Regular Snack Eaten
        let ate = false;
        if (this.regularSnack && newX === this.regularSnack.x && newY === this.regularSnack.y) {
            this.eatSnack(this.regularSnack);
            this.spawnRegularSnack();
            ate = true;
        }

        // Check Bonus Sundae Eaten
        if (this.bonusSnack && newX === this.bonusSnack.x && newY === this.bonusSnack.y) {
            this.eatSnack(this.bonusSnack);
            this.bonusSnack = null;
            ate = true;
        }

        if (this.growPending > 0) {
            this.growPending--;
        } else if (!ate) {
            this.snake.pop();
        }
    }

    eatSnack(snack) {
        const specs = {
            'Apple': { pts: 10, grow: 1, color: '#e62832' },
            'Pizza': { pts: 25, grow: 2, color: '#ffb91e' },
            'Donut': { pts: 35, grow: 2, color: '#ff69b4' },
            'Taco': { pts: 40, grow: 2, color: '#f5c83c' },
            'Burger': { pts: 50, grow: 3, color: '#d79141' },
            'Chili': { pts: 30, grow: 1, color: '#ff2d14' },
            'Sundae': { pts: 100, grow: 2, color: '#ffd700' }
        };

        const spec = specs[snack.type] || { pts: 10, grow: 1, color: '#00f0ff' };
        const multiplier = this.frenzyTimer > 0 ? 2 : 1;
        const ptsEarned = spec.pts * multiplier;

        this.score += ptsEarned;
        this.snacksEaten++;
        this.growPending += spec.grow;

        // Visual effects & audio
        this.createExplosion(snack.x, snack.y, spec.color);
        this.addPopup(snack.x, snack.y, `+${ptsEarned}`, spec.color);

        if (snack.type === 'Chili') {
            this.frenzyTimer = 8.0;
            this.audio.playFrenzy();
            this.dom.frenzyIndicator.classList.add('frenzy-active');
            this.dom.hudMultiplier.textContent = '2X';
            this.addPopup(snack.x, snack.y - 1, '🔥 2X FRENZY!', '#ff3344');
        } else if (snack.type === 'Sundae') {
            this.audio.playEat(true);
        } else {
            this.audio.playEat(false);
        }

        // Spawn bonus sundae every 8 snacks
        if (this.snacksEaten > 0 && this.snacksEaten % 8 === 0 && !this.bonusSnack) {
            this.spawnBonusSundae();
        }

        // High score trigger
        if (this.score > this.highScore && !this.isNewHighScore) {
            this.isNewHighScore = true;
            this.highScore = this.score;
            this.audio.playHighScore();
            this.addPopup(snack.x, snack.y - 2, '👑 NEW RECORD!', '#ffd700');
        } else if (this.score > this.highScore) {
            this.highScore = this.score;
        }
    }

    gameOver(reason) {
        this.state = 'GAMEOVER';
        this.audio.playCrash();
        this.shakeTimer = 0.45;
        this.shakeIntensity = 10;

        document.getElementById('gameOverTitle').textContent = reason;
        this.dom.finalScoreVal.textContent = this.score.toLocaleString();
        this.dom.finalSnacksVal.textContent = this.snacksEaten;
        this.dom.finalLengthVal.textContent = this.snake.length;
        this.dom.finalTimeVal.textContent = this.formatTime(this.gameTime);
        this.dom.submitFeedback.textContent = '';
        this.dom.submitFeedback.className = 'submit-feedback';

        this.dom.gameOverOverlay.classList.add('active');
        this.dom.playerNameInput.focus();
    }

    updateHUD() {
        this.dom.hudScore.textContent = this.score.toLocaleString();
        this.dom.hudSnacks.textContent = this.snacksEaten;
        this.dom.hudBest.textContent = this.highScore.toLocaleString();
        this.dom.globalHighScoreVal.textContent = this.highScore.toLocaleString();
        this.dom.hudTime.textContent = this.formatTime(this.gameTime);
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    // --- Particle and Popups Engine ---
    createExplosion(gridX, gridY, color) {
        const px = gridX * this.cellSize + this.cellSize / 2;
        const py = gridY * this.cellSize + this.cellSize / 2;
        for (let i = 0; i < 16; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 90 + 30;
            this.particles.push({
                x: px,
                y: py,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                color: color,
                size: Math.random() * 3 + 2,
                life: 0.55,
                maxLife: 0.55
            });
        }
    }

    addPopup(gridX, gridY, text, color) {
        const px = gridX * this.cellSize + this.cellSize / 2;
        const py = gridY * this.cellSize;
        this.popups.push({
            x: px,
            y: py,
            text: text,
            color: color,
            life: 0.9,
            maxLife: 0.9
        });
    }

    updateParticles(dt) {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            p.life -= dt;
            if (p.life <= 0) this.particles.splice(i, 1);
        }

        for (let i = this.popups.length - 1; i >= 0; i--) {
            const pop = this.popups[i];
            pop.y -= 25 * dt;
            pop.life -= dt;
            if (pop.life <= 0) this.popups.splice(i, 1);
        }
    }

    // --- Procedural Canvas Rendering ---
    render() {
        this.ctx.save();

        // Screen Shake
        if (this.shakeTimer > 0) {
            const shake = (this.shakeTimer / 0.45) * this.shakeIntensity;
            const offsetX = (Math.random() * 2 - 1) * shake;
            const offsetY = (Math.random() * 2 - 1) * shake;
            this.ctx.translate(offsetX, offsetY);
        }

        // Clear Canvas Background
        this.ctx.fillStyle = '#060911';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Subtle Grid Dots / Lines
        this.renderGrid();

        // Render Snacks
        if (this.regularSnack) {
            this.renderSnack(this.regularSnack);
        }
        if (this.bonusSnack) {
            this.renderSnack(this.bonusSnack);
        }

        // Render Snake
        if (this.snake.length > 0) {
            this.renderSnake();
        }

        // Render Particles & Popups
        this.renderEffects();

        this.ctx.restore();
    }

    renderGrid() {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
        this.ctx.lineWidth = 1;
        for (let x = 0; x <= this.canvas.width; x += this.cellSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.canvas.height; y += this.cellSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }

        // Solid Wall boundary indicator
        if (this.wallMode === 'solid') {
            this.ctx.strokeStyle = 'rgba(0, 240, 255, 0.2)';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(1, 1, this.canvas.width - 2, this.canvas.height - 2);
        }
    }

    renderSnake() {
        const isFrenzy = this.frenzyTimer > 0;

        // Draw body segments
        for (let i = this.snake.length - 1; i >= 1; i--) {
            const seg = this.snake[i];
            const px = seg.x * this.cellSize;
            const py = seg.y * this.cellSize;
            const radius = this.cellSize / 2 - 1;

            if (isFrenzy) {
                const hue = (Date.now() / 5 + i * 15) % 360;
                this.ctx.fillStyle = `hsl(${hue}, 90%, 55%)`;
                this.ctx.shadowColor = `hsl(${hue}, 90%, 55%)`;
                this.ctx.shadowBlur = 6;
            } else {
                // Smooth green gradient
                const ratio = i / this.snake.length;
                const g = Math.floor(210 - ratio * 60);
                this.ctx.fillStyle = `rgb(30, ${g}, 70)`;
                this.ctx.shadowBlur = 0;
            }

            this.ctx.beginPath();
            this.ctx.arc(px + this.cellSize / 2, py + this.cellSize / 2, radius, 0, Math.PI * 2);
            this.ctx.fill();
        }

        // Draw Snake Head
        const head = this.snake[0];
        const hx = head.x * this.cellSize + this.cellSize / 2;
        const hy = head.y * this.cellSize + this.cellSize / 2;
        const headRadius = this.cellSize / 2 + 1;

        if (isFrenzy) {
            this.ctx.fillStyle = '#ff0077';
            this.ctx.shadowColor = '#ff0077';
            this.ctx.shadowBlur = 12;
        } else {
            this.ctx.fillStyle = '#22dd55';
            this.ctx.shadowColor = '#22dd55';
            this.ctx.shadowBlur = 8;
        }

        this.ctx.beginPath();
        this.ctx.arc(hx, hy, headRadius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.shadowBlur = 0;

        // Animated Cartoon Eyes & Pupils
        const eyeOffsetDist = 5;
        const eyeRadius = 3.5;
        const pupilRadius = 1.8;

        // Vector perpendicular to direction for eyes
        const perpX = -this.dir.y;
        const perpY = this.dir.x;

        const leftEyeX = hx + this.dir.x * 3 + perpX * eyeOffsetDist;
        const leftEyeY = hy + this.dir.y * 3 + perpY * eyeOffsetDist;
        const rightEyeX = hx + this.dir.x * 3 - perpX * eyeOffsetDist;
        const rightEyeY = hy + this.dir.y * 3 - perpY * eyeOffsetDist;

        // Eye Whites
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(leftEyeX, leftEyeY, eyeRadius, 0, Math.PI * 2);
        this.ctx.arc(rightEyeX, rightEyeY, eyeRadius, 0, Math.PI * 2);
        this.ctx.fill();

        // Eye Pupils (Looking in direction of movement)
        this.ctx.fillStyle = '#0b0f19';
        this.ctx.beginPath();
        this.ctx.arc(leftEyeX + this.dir.x * 1.5, leftEyeY + this.dir.y * 1.5, pupilRadius, 0, Math.PI * 2);
        this.ctx.arc(rightEyeX + this.dir.x * 1.5, rightEyeY + this.dir.y * 1.5, pupilRadius, 0, Math.PI * 2);
        this.ctx.fill();

        // Animated Flickering Tongue
        if (Math.sin(Date.now() / 80) > 0.4) {
            this.ctx.strokeStyle = '#ff3366';
            this.ctx.lineWidth = 1.8;
            const tipX = hx + this.dir.x * (headRadius + 6);
            const tipY = hy + this.dir.y * (headRadius + 6);
            this.ctx.beginPath();
            this.ctx.moveTo(hx + this.dir.x * headRadius, hy + this.dir.y * headRadius);
            this.ctx.lineTo(tipX, tipY);
            // Fork tip
            this.ctx.lineTo(tipX + perpX * 3, tipY + perpY * 3);
            this.ctx.moveTo(tipX, tipY);
            this.ctx.lineTo(tipX - perpX * 3, tipY - perpY * 3);
            this.ctx.stroke();
        }
    }

    renderSnack(snack) {
        const cx = snack.x * this.cellSize + this.cellSize / 2;
        const cy = snack.y * this.cellSize + this.cellSize / 2;
        const size = this.cellSize;

        this.ctx.save();
        this.ctx.translate(cx, cy);

        // Gentle breathing animation
        const pulse = 1 + Math.sin(Date.now() / 200) * 0.08;
        this.ctx.scale(pulse, pulse);

        switch (snack.type) {
            case 'Apple':
                // Red sphere with leaf
                this.ctx.fillStyle = '#e62832';
                this.ctx.beginPath();
                this.ctx.arc(0, 1, 7, 0, Math.PI * 2);
                this.ctx.fill();
                // Highlight
                this.ctx.fillStyle = '#ff828a';
                this.ctx.beginPath();
                this.ctx.arc(-2, -1, 2.2, 0, Math.PI * 2);
                this.ctx.fill();
                // Stem & Leaf
                this.ctx.strokeStyle = '#5a3214';
                this.ctx.lineWidth = 1.5;
                this.ctx.beginPath();
                this.ctx.moveTo(0, -6);
                this.ctx.lineTo(1, -9);
                this.ctx.stroke();
                this.ctx.fillStyle = '#3cb428';
                this.ctx.beginPath();
                this.ctx.ellipse(3, -7, 3, 1.5, Math.PI / 4, 0, Math.PI * 2);
                this.ctx.fill();
                break;

            case 'Pizza':
                // Pizza Wedge
                this.ctx.fillStyle = '#ffb91e';
                this.ctx.beginPath();
                this.ctx.moveTo(0, -7);
                this.ctx.lineTo(-7, 7);
                this.ctx.lineTo(7, 7);
                this.ctx.closePath();
                this.ctx.fill();
                // Pepperoni dots
                this.ctx.fillStyle = '#d22d1e';
                [-2, 2].forEach(ox => {
                    this.ctx.beginPath();
                    this.ctx.arc(ox, 2, 1.8, 0, Math.PI * 2);
                    this.ctx.fill();
                });
                break;

            case 'Donut':
                // Golden dough with pink frosting
                this.ctx.fillStyle = '#f0b464';
                this.ctx.beginPath();
                this.ctx.arc(0, 0, 7.5, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.fillStyle = '#ff69b4';
                this.ctx.beginPath();
                this.ctx.arc(0, 0, 6.2, 0, Math.PI * 2);
                this.ctx.fill();
                // Center hole
                this.ctx.fillStyle = '#060911';
                this.ctx.beginPath();
                this.ctx.arc(0, 0, 2.5, 0, Math.PI * 2);
                this.ctx.fill();
                break;

            case 'Taco':
                // Golden taco shell
                this.ctx.fillStyle = '#f5c83c';
                this.ctx.beginPath();
                this.ctx.arc(0, 2, 7.5, Math.PI, 0, false);
                this.ctx.closePath();
                this.ctx.fill();
                // Lettuce & meat fillings
                this.ctx.fillStyle = '#46b432';
                this.ctx.fillRect(-5, 0, 10, 2);
                this.ctx.fillStyle = '#d22d1e';
                this.ctx.fillRect(-3, -2, 6, 2);
                break;

            case 'Burger':
                // Burger Buns & patty
                this.ctx.fillStyle = '#d79141';
                this.ctx.beginPath();
                this.ctx.arc(0, -1, 7, Math.PI, 0, false);
                this.ctx.fill();
                // Patty & lettuce
                this.ctx.fillStyle = '#4bb937';
                this.ctx.fillRect(-7, 0, 14, 2);
                this.ctx.fillStyle = '#693719';
                this.ctx.fillRect(-7, 2, 14, 2.5);
                this.ctx.fillStyle = '#d79141';
                this.ctx.fillRect(-6, 4.5, 12, 2.5);
                break;

            case 'Chili':
                // Red curved fiery chili with flames
                this.ctx.shadowColor = '#ff3344';
                this.ctx.shadowBlur = 10;
                this.ctx.fillStyle = '#ff2d14';
                this.ctx.beginPath();
                this.ctx.moveTo(0, -6);
                this.ctx.quadraticCurveTo(6, 2, 1, 8);
                this.ctx.quadraticCurveTo(-4, 2, 0, -6);
                this.ctx.fill();
                // Green stem
                this.ctx.shadowBlur = 0;
                this.ctx.fillStyle = '#3cb428';
                this.ctx.beginPath();
                this.ctx.arc(0, -7, 2, 0, Math.PI * 2);
                this.ctx.fill();
                break;

            case 'Sundae':
                // Golden Sparkling Sundae
                this.ctx.shadowColor = '#ffd700';
                this.ctx.shadowBlur = 12;
                this.ctx.fillStyle = '#ffd700';
                this.ctx.beginPath();
                this.ctx.arc(0, -2, 6.5, 0, Math.PI * 2);
                this.ctx.fill();
                // Cherry on top
                this.ctx.fillStyle = '#f0143c';
                this.ctx.beginPath();
                this.ctx.arc(0, -7.5, 2.5, 0, Math.PI * 2);
                this.ctx.fill();
                // Glass base
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                this.ctx.fillRect(-3, 3, 6, 4);
                break;
        }

        this.ctx.restore();
    }

    renderEffects() {
        // Draw Particles
        for (const p of this.particles) {
            const alpha = p.life / p.maxLife;
            this.ctx.save();
            this.ctx.globalAlpha = alpha;
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        }

        // Draw Floating Text Popups
        this.ctx.font = '11px "Press Start 2P", monospace';
        this.ctx.textAlign = 'center';
        for (const pop of this.popups) {
            const alpha = pop.life / pop.maxLife;
            this.ctx.save();
            this.ctx.globalAlpha = alpha;
            this.ctx.fillStyle = pop.color;
            this.ctx.shadowColor = pop.color;
            this.ctx.shadowBlur = 8;
            this.ctx.fillText(pop.text, pop.x, pop.y);
            this.ctx.restore();
        }
    }

    // --- Flask REST API Integration ---
    async fetchLeaderboard() {
        try {
            const res = await fetch('/api/leaderboard');
            if (!res.ok) throw new Error('Network error');
            const data = await res.json();
            if (data.status === 'success' && Array.isArray(data.leaderboard)) {
                this.renderLeaderboardTable(data.leaderboard);
            }
        } catch (err) {
            console.warn('Could not fetch leaderboard:', err);
            this.dom.leaderboardBody.innerHTML = `<tr><td colspan="4" class="table-loading">Offline mode</td></tr>`;
        }
    }

    renderLeaderboardTable(entries) {
        if (!entries || entries.length === 0) {
            this.dom.leaderboardBody.innerHTML = `<tr><td colspan="4" class="table-loading">No scores recorded yet!</td></tr>`;
            return;
        }

        this.dom.leaderboardBody.innerHTML = entries.map((entry, idx) => {
            const rankClass = idx === 0 ? 'rank-1' : idx === 1 ? 'rank-2' : idx === 2 ? 'rank-3' : '';
            return `
                <tr>
                    <td class="rank-cell ${rankClass}">#${idx + 1}</td>
                    <td class="player-name">${this.escapeHTML(entry.name)}</td>
                    <td class="score-cell">${Number(entry.score).toLocaleString()}</td>
                    <td><span class="diff-badge">${this.escapeHTML(entry.difficulty || 'Classic')}</span></td>
                </tr>
            `;
        }).join('');
    }

    async submitScoreToAPI() {
        const playerName = this.dom.playerNameInput.value.trim() || 'Anonymous';
        const submitBtn = document.getElementById('btnSubmitScore');
        submitBtn.disabled = true;
        this.dom.submitFeedback.textContent = 'Submitting to Flask API...';
        this.dom.submitFeedback.className = 'submit-feedback';

        try {
            const res = await fetch('/api/score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    player: playerName,
                    score: this.score,
                    difficulty: this.difficulty,
                    snacks: this.snacksEaten
                })
            });

            const data = await res.json();
            if (data.status === 'success') {
                this.dom.submitFeedback.textContent = `Score recorded! Rank #${data.rank || 1} on the Hall of Fame!`;
                this.dom.submitFeedback.className = 'submit-feedback success';
                if (data.leaderboard) {
                    this.renderLeaderboardTable(data.leaderboard);
                }
                if (data.high_score) {
                    this.highScore = data.high_score;
                    this.updateHUD();
                }
            } else {
                throw new Error(data.message || 'Submission failed');
            }
        } catch (err) {
            console.error('Error submitting score:', err);
            this.dom.submitFeedback.textContent = 'Could not reach server. Score saved locally!';
            this.dom.submitFeedback.className = 'submit-feedback error';
        } finally {
            submitBtn.disabled = false;
        }
    }

    async fetchSnackDefinitions() {
        try {
            const res = await fetch('/api/snacks');
            if (!res.ok) throw new Error('API request failed');
            const data = await res.json();
            if (data.status === 'success' && Array.isArray(data.snacks)) {
                this.renderSnackMenu(data.snacks);
            }
        } catch (err) {
            console.warn('Could not load snack specs from API:', err);
        }
    }

    renderSnackMenu(snacks) {
        this.dom.snackGrid.innerHTML = snacks.map(s => `
            <div class="snack-card">
                <span class="snack-card-icon">${s.icon}</span>
                <span class="snack-card-name">${s.name}</span>
                <span class="snack-card-pts">+${s.points} PTS</span>
                <span class="snack-card-effect">${s.effect}</span>
            </div>
        `).join('');
    }

    escapeHTML(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
}

// Instantiate game engine on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    window.snackAttack = new SnackAttackGame();
});
