# 🎓 Study Planner — Intelligent Schedule & Hour Recommendation Engine

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-5%2F5%20Passing-brightgreen.svg)]()
[![UI Theme](https://img.shields.io/badge/UI-Dark%20%2F%20Light%20Modes-orange.svg)]()

> **An algorithmic, evidence-based study planner tailored for AIML, Computer Science, and STEM students.** The Study Planner dynamically calculates subject urgency, mastery deficits, and cognitive difficulty to allocate daily study hours and generate structured, interleaved Pomodoro timetables.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Algorithmic Core & Mathematical Logic](#-algorithmic-core--mathematical-logic)
- [System Architecture](#-system-architecture)
- [Project File Structure](#-project-file-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
  - [Running the Application](#running-the-application)
- [API Documentation](#-api-documentation)
- [Running Automated Tests](#-running-automated-tests)
- [UI & Interactive Capabilities](#-ui--interactive-capabilities)
- [Preset Curriculum Templates](#-preset-curriculum-templates)
- [Contributing & License](#-contributing--license)

---

## 🌟 Overview

Students preparing for high-stakes technical exams often struggle with **cognitive fatigue**, **poor time allocation**, and **cramming**. Traditional planners treat all subjects equally or leave prioritization entirely to guesswork.

**Study Planner** solves this by combining **computational heuristics** with established pedagogical principles (Cognitive Load Theory, Spaced Interleaving, and the Pomodoro Technique):
- **Weighted Multi-Factor Scoring**: Evaluates proximity of exam dates, current test scores, and student-reported grasp levels.
- **Proportional Hour Distribution**: Automatically converts daily available hours into balanced study blocks without manual math.
- **Fatigue-Minimizing Timetable**: Interleaves high-intensity (weak/critical) subjects with maintenance subjects and structured breaks.
- **Embedded Focus Timer**: Built-in Pomodoro timer featuring synthesized Web Audio feedback to keep learners in deep flow.

---

## ✨ Key Features

- **🧠 Algorithmic Recommendation Engine**: Pure Python analytical pipeline (`planner_engine.py`) calculating exact priority metrics and recommended hour quotas.
- **📊 Dynamic Visual Allocation Bar**: Responsive multi-colored proportion bar visually displaying each subject's share of study time.
- **📅 Actionable Daily Timetable**: Granular, time-slotted study blocks with contextual pedagogical objectives (e.g., active recall, formula drills, past papers).
- **⏱️ Integrated Pomodoro Focus Clock**: Modeless and modal Pomodoro timer with preset sprint durations (25m / 50m work, 5m / 15m break) and browser Web Audio tones.
- **🌓 Dual-Theme Interface (Dark & Light Mode)**: Sleek glassmorphism dark mode paired with a clean daytime palette, persisted via `localStorage`.
- **✅ Interactive Session Checklist**: Real-time progress tracking allowing students to check off completed study blocks and monitor today's completion rate.
- **🖨️ Clean Print / PDF Export**: Dedicated `@media print` CSS stylesheet for one-click clean PDF generation and physical printing.
- **⚡ Zero External Database Requirement**: Completely lightweight, stateless REST API architecture running instantly on any standard Python environment.

---

## 📐 Algorithmic Core & Mathematical Logic

The recommendation engine in [`planner_engine.py`](file:///c:/Users/abc/OneDrive/Desktop/Project/planner_engine.py) computes priorities through a 4-stage analytical model:

```
[ Input Subjects ] 
       │
       ▼
 1. Urgency Decay Function (Days to Exam)
       │
       ├─► 2. Mastery Gap Deficit (Target 95% - Current Marks)
       │
       ▼
 3. Cognitive Multiplier (Weak: 1.55x, Neutral: 1.00x, Strong: 0.70x)
       │
       ▼
 4. Composite Priority Score & Proportional Hour Allocation
       │
       ▼
 5. Interleaved Pomodoro Timetable Generation
```

### 1. Urgency Component ($U$)
Urgency follows a non-linear stepped decay curve based on remaining days $d$:

$$
U(d) = \begin{cases} 
100.0 & \text{if } d \le 1 \\ 
90.0 & \text{if } 1 < d \le 3 \\ 
75.0 & \text{if } 3 < d \le 7 \\ 
55.0 & \text{if } 7 < d \le 14 \\ 
35.0 & \text{if } 14 < d \le 30 \\ 
\max(10.0, 30.0 - 0.5 \times (d - 30)) & \text{if } d > 30 
\end{cases}
$$

### 2. Mastery Gap Deficit ($G$)
Targeting comprehensive mastery ($95\%$), the gap is bounded by:

$$
G(m) = \max(5.0, 95.0 - m)
$$

*where $m$ is the student's current mark (0–100).*

### 3. Cognitive Load Multiplier ($\mu$)
Based on self-assessed comprehension:
- **Weak grasp**: $\mu = 1.55$ *(increased repetition and deliberate practice required)*
- **Neutral grasp**: $\mu = 1.00$ *(standard progression)*
- **Strong grasp**: $\mu = 0.70$ *(active recall and maintenance drills only)*

### 4. Composite Priority Score ($P$)

$$
P = \Big( (0.50 \times U) + (0.50 \times G) \Big) \times \mu
$$

| Priority Tier | Score Range / Condition | Strategic Recommendation |
|---|---|---|
| **Critical** | $P \ge 95$ OR ($d \le 2$ and $m < 60$) | Active Recall & High-yield Exam Questions |
| **High** | $70 \le P < 95$ | Core Concepts & Deep Problem Solving |
| **Moderate** | $45 \le P < 70$ | Structured Revision & Note Condensation |
| **Maintenance** | $P < 45$ | Quick Practice Drills & Flashcard Review |

### 5. Proportional Hours Allocation ($H_i$)

$$
H_i = \text{round}_{0.5}\left( \frac{P_i}{\sum_{j=1}^{N} P_j} \times H_{\text{available}} \right)
$$

*(Residual discrepancies are reconciled to ensure $\sum H_i = H_{\text{available}}$ exactly).*

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Client Browser                       │
│  - Vanilla JavaScript State Manager (main.js)          │
│  - Web Audio API Sound Synthesizer                     │
│  - Dual-Theme Glassmorphic CSS (style.css)             │
│  - Reactive DOM Renderer (index.html)                  │
└───────────────────────▲────────────────────────────────┘
                        │
                        │ HTTP / JSON REST Requests
                        ▼
┌────────────────────────────────────────────────────────┐
│               Flask Application Server (app.py)        │
│  - Route: /                 -> Serves HTML UI          │
│  - Route: /api/presets      -> Returns Preset Data     │
│  - Route: /api/generate-plan-> Executes Engine API     │
│  - Route: /api/health       -> Health Monitoring       │
└───────────────────────▲────────────────────────────────┘
                        │
                        │ In-Memory Function Calls
                        ▼
┌────────────────────────────────────────────────────────┐
│       Core Recommendation Engine (planner_engine.py)   │
│  - calculate_days_left()                               │
│  - calculate_priority_score()                          │
│  - allocate_study_hours()                              │
│  - generate_daily_timetable()                          │
│  - generate_study_plan()                               │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Project File Structure

```
c:/Users/abc/OneDrive/Desktop/Project/
├── app.py                  # Flask web server & REST API controller
├── planner_engine.py       # Core mathematical recommendation & scheduling engine
├── test_planner.py         # Automated unit test suite (unittest)
├── requirements.txt        # Python dependency manifest
├── README.md               # Project documentation and quickstart guide
├── PROJECT_REPORT.md       # Comprehensive academic & engineering technical report
├── templates/
│   └── index.html          # Semantic HTML5 single-page application markup
└── static/
    ├── css/
    │   └── style.css       # Premium styling, animations, responsive design & print CSS
    └── js/
        └── main.js         # Frontend controller, timer, audio synthesis & local state
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (verify with `python --version`)
- Modern web browser (Chrome, Edge, Firefox, Safari, or Brave)

### Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd c:/Users/abc/OneDrive/Desktop/Project
   ```

2. **(Optional but recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Launch the local web server:
```bash
python app.py
```

The terminal will confirm:
```
Starting Study Planner Web App on http://127.0.0.1:5000 ...
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### ☁️ Deploying to Vercel (Production)

The project includes all files needed for zero-configuration deployment on **Vercel**:
- **Serverless Entrypoint**: [`api/index.py`](file:///c:/Users/abc/OneDrive/Desktop/Project/api/index.py) bridges Flask to Vercel Serverless Functions.
- **Routing Rules**: [`vercel.json`](file:///c:/Users/abc/OneDrive/Desktop/Project/vercel.json) routes incoming requests directly to the app, resolving `404 NOT_FOUND` errors.
- **Python Version**: [`.python-version`](file:///c:/Users/abc/OneDrive/Desktop/Project/.python-version) locks the runtime to Python 3.11.

To deploy via Vercel CLI:
```bash
npx vercel
```
Or connect your GitHub repository to Vercel and deploy with standard default settings.

---

## 📡 API Documentation

### 1. Generate Study Plan
- **Endpoint**: `POST /api/generate-plan`
- **Headers**: `Content-Type: application/json`

#### Request Body Example:
```json
{
  "available_hours": 6.0,
  "start_time": "09:00",
  "session_length": 50,
  "break_length": 10,
  "subjects": [
    {
      "name": "Machine Learning",
      "exam_date": "2026-09-24",
      "current_marks": 52,
      "difficulty": "weak"
    },
    {
      "name": "Python for Data Science",
      "exam_date": "2026-10-04",
      "current_marks": 88,
      "difficulty": "strong"
    }
  ]
}
```

#### Response Example (`200 OK`):
```json
{
  "success": true,
  "summary": {
    "total_subjects": 2,
    "available_hours": 6.0,
    "critical_count": 1,
    "weak_count": 1,
    "average_marks": 70.0,
    "total_sessions": 6,
    "total_breaks": 5,
    "study_tips": [
      "⚠️ You have critical exams approaching with score gaps. Focus your prime morning hours on these topics!",
      "🧠 Practice the Feynman Technique: Explain complex concepts from your weak subjects in simple terms out loud.",
      "⏱️ Use the embedded Pomodoro timer for each study block to maintain peak dopamine and focus."
    ]
  },
  "priority_subjects": [
    {
      "name": "Machine Learning",
      "days_left": 4,
      "current_marks": 52,
      "difficulty": "weak",
      "raw_priority": 91.45,
      "priority_level": "High",
      "recommended_hours": 4.5,
      "hours_percent": 75.0,
      "study_strategy": "Core Concepts & Deep Problem Solving"
    }
  ],
  "timetable": [
    {
      "slot_id": "slot_1",
      "slot_number": 1,
      "start_time": "09:00",
      "end_time": "09:50",
      "duration_min": 50,
      "subject": "Machine Learning",
      "difficulty": "weak",
      "priority_level": "High",
      "task_focus": "Deep Dive Part 1: Tackle core formulas, work through 3 challenging textbook problems.",
      "is_break": false
    },
    {
      "slot_id": "break_2",
      "slot_number": 2,
      "start_time": "09:50",
      "end_time": "10:00",
      "duration_min": 10,
      "subject": "Mind Refresh & Rest",
      "is_break": true
    }
  ]
}
```

---

### 2. Fetch Curriculum Presets
- **Endpoint**: `GET /api/presets`
- **Response**: Pre-configured subject templates with dates calculated relative to current system date.

### 3. Health Check
- **Endpoint**: `GET /api/health`
- **Response**: `{"service": "Study Planner", "status": "healthy"}`

---

## 🧪 Running Automated Tests

A dedicated suite of unit tests validates core mathematical logic, edge boundary values, and schedule allocation:

```bash
python test_planner.py
```

Expected output:
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.008s

OK
```

### Covered Test Scenarios:
1. `test_days_left`: Correct date delta calculation, zero clamping for past/same-day dates.
2. `test_multipliers`: Difficulty multiplier mappings (`weak` = 1.55, `neutral` = 1.00, `strong` = 0.70).
3. `test_priority_score`: Validation that high-urgency and low-mark subjects receive elevated scores and Critical/High tier badges.
4. `test_hour_allocation`: Proportional distribution verification and sum equality with available hours.
5. `test_full_plan_generation`: End-to-end integration test verifying complete schema output.

---

## 🖥️ UI & Interactive Capabilities

| Feature | Description |
|---|---|
| **Theme Switcher** | Toggle seamlessly between sleek dark glassmorphism and crisp high-contrast light mode with auditory click feedback. |
| **Live Hours Slider** | Adjust study availability from 1.0 hour to 14.0 hours with instant badge feedback. |
| **Pomodoro Clock** | Focus timer with configurable intervals (25m/50m study, 5m/15m breaks), synchronized title bar preview, and completion audio alerts. |
| **Dynamic Subject Cards** | Add, remove, and adjust subjects with live input bounds on marks (0–100%) and exam date pickers. |
| **Checklist Tracking** | Clickable checkboxes on timetable slots that recalculate completion percentage and update visual status in real time. |
| **One-Click Print / PDF** | Formats the timetable and priority metrics for clean standard A4 print or digital export. |

---

## 📚 Preset Curriculum Templates

The application includes built-in presets for quick evaluation:
1. **🤖 AIML Semester Exam Prep**: Focuses on *Machine Learning*, *Linear Algebra & Vectors*, *Python for Data Science*, *Deep Learning & Neural Nets*, and *Probability & Statistics*.
2. **⚡ CS Core Crunch Week**: Targets *Data Structures & Algorithms*, *Operating Systems*, and *Database Management (SQL)*.
3. **🐍 Python Essentials Bootcamp**: Covers *Functions & Modular Code*, *OOP & Data Structures*, and *File Handling & Regex*.

---

## 🤝 Contributing & License

Contributions, feature requests, and bug reports are welcome!
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/smart-calendar-sync`)
3. Commit changes (`git commit -m "Add calendar export feature"`)
4. Push to branch (`git push origin feature/smart-calendar-sync`)
5. Open a Pull Request

This project is licensed under the **MIT License**.
#   p y t h o n _ p r o j e c t  
 #   p y t h o n _ p r o j e c t  
 