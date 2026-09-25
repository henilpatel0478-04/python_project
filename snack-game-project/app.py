"""
Snack Attack! - Flask Web Application & REST API
Integrates Flask web server with the Snack Attack arcade game ecosystem.
"""
import os
import json
from datetime import datetime
from flask import Flask, jsonify, request, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Initialize Flask App with absolute template and static directories
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# File paths (handle Vercel serverless read-only filesystem by using /tmp when deployed)
IS_VERCEL = bool(os.environ.get("VERCEL"))

def get_read_path(filename: str) -> str:
    """Return file path for reading, preferring /tmp on Vercel if updated."""
    if IS_VERCEL:
        tmp_file = os.path.join("/tmp", filename)
        if os.path.exists(tmp_file):
            return tmp_file
    return os.path.join(BASE_DIR, filename)

def get_write_path(filename: str) -> str:
    """Return file path for writing (use /tmp on Vercel to avoid read-only errors)."""
    if IS_VERCEL:
        return os.path.join("/tmp", filename)
    return os.path.join(BASE_DIR, filename)

# Snack metadata definitions for web client and API
SNACK_METADATA = [
    {
        "id": "Apple",
        "name": "Crispy Apple",
        "icon": "🍎",
        "points": 10,
        "growth": 1,
        "description": "Standard juicy crunch. Increases length by 1.",
        "badge": "Standard",
        "colors": ["#E62832", "#FF646E", "#78C832"],
        "effect": "None"
    },
    {
        "id": "Pizza",
        "name": "Pizza Slice",
        "icon": "🍕",
        "points": 25,
        "growth": 2,
        "description": "Savory cheese & pepperoni bite. Increases length by 2.",
        "badge": "Savory",
        "colors": ["#FFB91E", "#D22D1E", "#C88232"],
        "effect": "+2 Segments"
    },
    {
        "id": "Donut",
        "name": "Glazed Donut",
        "icon": "🍩",
        "points": 35,
        "growth": 2,
        "description": "Frosted pastry with rainbow sprinkles.",
        "badge": "Sweet",
        "colors": ["#FF69B4", "#F0B464", "#00F0FF"],
        "effect": "+2 Segments"
    },
    {
        "id": "Taco",
        "name": "Crispy Taco",
        "icon": "🌮",
        "points": 40,
        "growth": 2,
        "description": "Crunchy golden shell loaded with spicy seasoning.",
        "badge": "Crunchy",
        "colors": ["#F5C83C", "#46B432", "#D22D1E"],
        "effect": "+2 Segments"
    },
    {
        "id": "Burger",
        "name": "Cheeseburger",
        "icon": "🍔",
        "points": 50,
        "growth": 3,
        "description": "Double patty deluxe burger with crisp lettuce.",
        "badge": "Hearty",
        "colors": ["#D79141", "#4BB937", "#693719"],
        "effect": "+3 Segments"
    },
    {
        "id": "Chili",
        "name": "Hot Chili Pepper",
        "icon": "🌶️",
        "points": 30,
        "growth": 1,
        "description": "SUPERCHARGE! 2X points multiplier & rainbow speed aura for 8s!",
        "badge": "Frenzy Powerup",
        "colors": ["#FF2D14", "#FF8C00", "#3CB428"],
        "effect": "2X Points Frenzy (8s)"
    },
    {
        "id": "Sundae",
        "name": "Golden Sundae",
        "icon": "🍦",
        "points": 100,
        "growth": 2,
        "description": "MEGA BONUS! Rare dessert that sparkles with gold coins!",
        "badge": "Rare Bonus",
        "colors": ["#FFD700", "#FFF0B4", "#F0143C"],
        "effect": "+100 Bonus Points"
    }
]


def load_high_score() -> int:
    """Read the current global high score from highscore.json."""
    read_file = get_read_path("highscore.json")
    if os.path.exists(read_file):
        try:
            with open(read_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
        except (json.JSONDecodeError, ValueError, IOError):
            return 0
    return 0


def save_high_score(score: int) -> bool:
    """Save high score to highscore.json if beaten."""
    current = load_high_score()
    if score > current:
        try:
            write_file = get_write_path("highscore.json")
            with open(write_file, "w", encoding="utf-8") as f:
                json.dump({"high_score": score}, f, indent=2)
            return True
        except IOError:
            return False
    return False


def load_leaderboard():
    """Retrieve leaderboard entries or initialize defaults."""
    read_file = get_read_path("leaderboard.json")
    if os.path.exists(read_file):
        try:
            with open(read_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Initialize with default arcade champions if none exist
    high = max(load_high_score(), 999)
    default_entries = [
        {"name": "SnackMaster", "score": high, "date": "2026-09-25", "difficulty": "Speedy", "snacks": 28},
        {"name": "PixelViper", "score": int(high * 0.75), "date": "2026-09-25", "difficulty": "Classic", "snacks": 19},
        {"name": "ChiliKing", "score": int(high * 0.55), "date": "2026-09-24", "difficulty": "Frenzy", "snacks": 14},
        {"name": "RetroCoder", "score": int(high * 0.35), "date": "2026-09-23", "difficulty": "Chill", "snacks": 9},
    ]
    try:
        write_file = get_write_path("leaderboard.json")
        with open(write_file, "w", encoding="utf-8") as f:
            json.dump(default_entries, f, indent=2)
    except IOError:
        pass
    return default_entries


def add_leaderboard_entry(name: str, score: int, difficulty: str = "Classic", snacks_eaten: int = 0):
    """Add a new score record and keep top 15 entries sorted."""
    entries = load_leaderboard()
    cleaned_name = (name or "Anonymous").strip()[:16] or "Anonymous"
    new_entry = {
        "name": cleaned_name,
        "score": int(score),
        "difficulty": difficulty,
        "snacks": int(snacks_eaten),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    entries.append(new_entry)
    entries.sort(key=lambda x: x["score"], reverse=True)
    entries = entries[:15]

    try:
        write_file = get_write_path("leaderboard.json")
        with open(write_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except IOError:
        pass
    
    # Check ranking
    rank = next((i + 1 for i, e in enumerate(entries) if e is new_entry), None)
    return rank, entries


@app.route("/")
def index():
    """Render the Snack Attack web portal & playable arcade game."""
    high_score = load_high_score()
    return render_template("index.html", high_score=high_score)


@app.route("/api/highscore", methods=["GET"])
def get_high_score():
    """API endpoint to get the current high score."""
    return jsonify({
        "status": "success",
        "high_score": load_high_score()
    })


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """API endpoint to retrieve the top arcade scores."""
    return jsonify({
        "status": "success",
        "leaderboard": load_leaderboard()
    })


@app.route("/api/score", methods=["POST"])
def submit_score():
    """
    API endpoint to submit a player score.
    Updates highscore.json and the leaderboard.
    """
    data = request.get_json(silent=True) or {}
    try:
        score = int(data.get("score", 0))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid score"}), 400

    player = str(data.get("player", "Player")).strip() or "Player"
    difficulty = str(data.get("difficulty", "Classic"))
    snacks = int(data.get("snacks", 0))

    is_new_high = save_high_score(score)
    rank, top_entries = add_leaderboard_entry(player, score, difficulty, snacks)

    return jsonify({
        "status": "success",
        "is_new_high_score": is_new_high,
        "high_score": load_high_score(),
        "rank": rank,
        "leaderboard": top_entries
    })


@app.route("/api/snacks", methods=["GET"])
def get_snacks():
    """API endpoint to get information about all snack types."""
    return jsonify({
        "status": "success",
        "snacks": SNACK_METADATA
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Snack Attack Flask Web API",
        "version": "1.0.0"
    })


if __name__ == "__main__":
    print("==================================================")
    print(">>> Snack Attack! Flask Web Server Starting...")
    print(">>> Open your browser at: http://127.0.0.1:5000")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
