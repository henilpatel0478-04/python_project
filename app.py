"""
Study Planner - Web Application Server
Flask server hosting API and serving interactive UI.
"""

import os
from flask import Flask, render_template, request, jsonify
from datetime import date, timedelta
import planner_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

# Sample Pre-configured Study Presets for students & AIML learners
def get_presets():
    today = date.today()
    return {
        "aiml": {
            "title": "🤖 AIML Semester Exam Prep",
            "available_hours": 6.0,
            "start_time": "09:00",
            "session_length": 50,
            "break_length": 10,
            "subjects": [
                {
                    "name": "Machine Learning",
                    "exam_date": (today + timedelta(days=4)).strftime("%Y-%m-%d"),
                    "current_marks": 52,
                    "difficulty": "weak"
                },
                {
                    "name": "Linear Algebra & Vectors",
                    "exam_date": (today + timedelta(days=8)).strftime("%Y-%m-%d"),
                    "current_marks": 64,
                    "difficulty": "neutral"
                },
                {
                    "name": "Python for Data Science",
                    "exam_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
                    "current_marks": 88,
                    "difficulty": "strong"
                },
                {
                    "name": "Deep Learning & Neural Nets",
                    "exam_date": (today + timedelta(days=6)).strftime("%Y-%m-%d"),
                    "current_marks": 45,
                    "difficulty": "weak"
                },
                {
                    "name": "Probability & Statistics",
                    "exam_date": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
                    "current_marks": 72,
                    "difficulty": "neutral"
                }
            ]
        },
        "cs_core": {
            "title": "⚡ CS Core Crunch Week",
            "available_hours": 5.0,
            "start_time": "10:00",
            "session_length": 45,
            "break_length": 10,
            "subjects": [
                {
                    "name": "Data Structures & Algorithms",
                    "exam_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "current_marks": 58,
                    "difficulty": "weak"
                },
                {
                    "name": "Operating Systems",
                    "exam_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "current_marks": 70,
                    "difficulty": "neutral"
                },
                {
                    "name": "Database Management (SQL)",
                    "exam_date": (today + timedelta(days=11)).strftime("%Y-%m-%d"),
                    "current_marks": 85,
                    "difficulty": "strong"
                }
            ]
        },
        "python_essentials": {
            "title": "🐍 Python Essentials Bootcamp",
            "available_hours": 4.0,
            "start_time": "08:30",
            "session_length": 50,
            "break_length": 10,
            "subjects": [
                {
                    "name": "Functions & Modular Code",
                    "exam_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "current_marks": 60,
                    "difficulty": "neutral"
                },
                {
                    "name": "OOP & Data Structures",
                    "exam_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                    "current_marks": 48,
                    "difficulty": "weak"
                },
                {
                    "name": "File Handling & Regex",
                    "exam_date": (today + timedelta(days=9)).strftime("%Y-%m-%d"),
                    "current_marks": 82,
                    "difficulty": "strong"
                }
            ]
        }
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/presets", methods=["GET"])
def api_presets():
    return jsonify({
        "success": True,
        "presets": get_presets()
    })


@app.route("/api/generate-plan", methods=["POST"])
def api_generate_plan():
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"success": False, "error": "Invalid request payload"}), 400

        plan = planner_engine.generate_study_plan(payload)
        return jsonify(plan)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Study Planner"})


if __name__ == "__main__":
    print("Starting Study Planner Web App on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
