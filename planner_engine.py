"""
Study Planner - Recommendation Engine
Designed for Python Essentials & AIML Foundations
Uses pure Python functions, conditions, lists, and dictionaries.
"""

from datetime import datetime, date
import math


def calculate_days_left(exam_date_str: str, base_date: date = None) -> int:
    """
    Calculates number of days between base_date and exam_date_str (YYYY-MM-DD).
    Returns 0 if exam is today or in the past.
    """
    if base_date is None:
        base_date = date.today()
    try:
        exam_dt = datetime.strptime(exam_date_str.strip(), "%Y-%m-%d").date()
        delta = (exam_dt - base_date).days
        return max(0, delta)
    except Exception:
        # Default fallback if format parsing fails: assume 14 days
        return 14


def get_difficulty_multiplier(level: str) -> float:
    """
    Returns difficulty weighting multiplier using conditional logic:
    - 'weak': 1.55 (requires extra focus and repetition)
    - 'neutral': 1.00 (standard pace)
    - 'strong': 0.70 (revision and practice only)
    """
    level = level.lower().strip()
    if level == "weak":
        return 1.55
    elif level == "strong":
        return 0.70
    else:
        return 1.00


def calculate_priority_score(subject: dict, base_date: date = None) -> dict:
    """
    Computes priority score using Python conditions and weighted factors:
    1. Days until exam (urgency factor)
    2. Current marks deficit (mastery gap factor)
    3. Weak/strong multiplier (cognitive load factor)
    """
    name = subject.get("name", "Unnamed Subject")
    exam_date_str = subject.get("exam_date", "")
    current_marks = float(subject.get("current_marks", 50))
    difficulty = subject.get("difficulty", "neutral").lower()

    days_left = calculate_days_left(exam_date_str, base_date)

    # 1. Urgency Component (inverse of days left, capped for stability)
    if days_left <= 1:
        urgency_score = 100.0
    elif days_left <= 3:
        urgency_score = 90.0
    elif days_left <= 7:
        urgency_score = 75.0
    elif days_left <= 14:
        urgency_score = 55.0
    elif days_left <= 30:
        urgency_score = 35.0
    else:
        urgency_score = max(10.0, 30.0 - (days_left - 30) * 0.5)

    # 2. Mark Deficit Component (100 - marks)
    # Higher gap from target 95% = higher need for study
    mark_gap = max(5.0, 95.0 - current_marks)

    # 3. Difficulty Multiplier
    multiplier = get_difficulty_multiplier(difficulty)

    # 4. Composite raw score
    raw_priority = ((urgency_score * 0.50) + (mark_gap * 0.50)) * multiplier

    # Priority category tag based on score
    if raw_priority >= 95 or (days_left <= 2 and current_marks < 60):
        priority_level = "Critical"
        badge_color = "danger"
        study_strategy = "Active Recall & High-yield Exam Questions"
    elif raw_priority >= 70:
        priority_level = "High"
        badge_color = "warning"
        study_strategy = "Core Concepts & Deep Problem Solving"
    elif raw_priority >= 45:
        priority_level = "Moderate"
        badge_color = "primary"
        study_strategy = "Structured Revision & Note Condensation"
    else:
        priority_level = "Maintenance"
        badge_color = "success"
        study_strategy = "Quick Practice Drills & Flashcard Review"

    return {
        "name": name,
        "days_left": days_left,
        "exam_date": exam_date_str,
        "current_marks": current_marks,
        "difficulty": difficulty,
        "urgency_score": round(urgency_score, 1),
        "mark_gap": round(mark_gap, 1),
        "multiplier": multiplier,
        "raw_priority": round(raw_priority, 2),
        "priority_level": priority_level,
        "badge_color": badge_color,
        "study_strategy": study_strategy
    }


def allocate_study_hours(scored_subjects: list, total_available_hours: float) -> list:
    """
    Distributes available study hours among subjects proportionally to priority.
    Applies minimum study slice thresholds (min 0.5h per subject if time permits).
    """
    if not scored_subjects:
        return []

    total_priority = sum(s["raw_priority"] for s in scored_subjects)
    if total_priority <= 0:
        total_priority = 1.0

    allocated_list = []
    accumulated_hours = 0.0

    for s in scored_subjects:
        proportion = s["raw_priority"] / total_priority
        # Preliminary allocation
        raw_hours = proportion * total_available_hours
        
        # Round to 1 decimal place or quarter hours
        rounded_hours = round(raw_hours * 2) / 2 # nearest 0.5 hour
        if rounded_hours < 0.5 and total_available_hours >= len(scored_subjects) * 0.5:
            rounded_hours = 0.5
        
        allocated_item = dict(s)
        allocated_item["recommended_hours"] = rounded_hours
        allocated_item["hours_percent"] = round((rounded_hours / total_available_hours) * 100, 1) if total_available_hours > 0 else 0
        allocated_list.append(allocated_item)
        accumulated_hours += rounded_hours

    # Adjust rounding discrepancy to match total_available_hours exactly
    diff = round(total_available_hours - accumulated_hours, 2)
    if abs(diff) >= 0.25 and allocated_list:
        # Give or subtract discrepancy from highest priority subject
        allocated_list[0]["recommended_hours"] = max(0.5, round((allocated_list[0]["recommended_hours"] + diff) * 2) / 2)
        allocated_list[0]["hours_percent"] = round((allocated_list[0]["recommended_hours"] / total_available_hours) * 100, 1)

    return allocated_list


def generate_daily_timetable(allocated_subjects: list, start_time_str: str = "09:00", session_length_min: int = 50, break_length_min: int = 10) -> list:
    """
    Generates a realistic daily study timetable with:
    - Dedicated subject blocks
    - Pomodoro-style breaks (e.g. 50 min study + 10 min break)
    - Actionable session tasks (theory, practice, self-quiz)
    """
    try:
        start_hour, start_minute = map(int, start_time_str.split(":"))
    except Exception:
        start_hour, start_minute = 9, 0

    timetable_slots = []
    current_minutes = start_hour * 60 + start_minute

    # Sort subjects: Critical/High first, alternating with lighter ones to prevent fatigue
    critical_subjects = [s for s in allocated_subjects if s["priority_level"] in ["Critical", "High"]]
    other_subjects = [s for s in allocated_subjects if s["priority_level"] not in ["Critical", "High"]]

    # Interleave subjects if multiple exist
    interleaved_queue = []
    c_idx, o_idx = 0, 0
    while c_idx < len(critical_subjects) or o_idx < len(other_subjects):
        if c_idx < len(critical_subjects):
            interleaved_queue.append(critical_subjects[c_idx])
            c_idx += 1
        if o_idx < len(other_subjects):
            interleaved_queue.append(other_subjects[o_idx])
            o_idx += 1

    if not interleaved_queue:
        interleaved_queue = allocated_subjects

    slot_counter = 1
    for subject in interleaved_queue:
        total_subject_min = int(round(subject.get("recommended_hours", 1.0) * 60))
        remaining_min = total_subject_min

        part_num = 1
        while remaining_min > 0:
            current_session = min(session_length_min, remaining_min)
            if current_session < 25 and timetable_slots:
                # If tiny remnant, merge into previous session or stretch
                timetable_slots[-1]["duration_min"] += current_session
                break

            end_minutes = current_minutes + current_session

            # Time formatting
            slot_start_time = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
            slot_end_time = f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"

            # Specific session goal
            if subject["difficulty"] == "weak":
                task_focus = f"Deep Dive Part {part_num}: Tackle core formulas, work through 3 challenging textbook problems."
            elif subject["current_marks"] < 50:
                task_focus = f"Foundation Building Part {part_num}: Review summary lecture slides and create active recall flashcards."
            elif subject["days_left"] <= 3:
                task_focus = f"Exam Sprint Part {part_num}: Timed past-paper questions & error analysis."
            else:
                task_focus = f"Mastery & Application Part {part_num}: Solve standard practice questions & verify derivations."

            timetable_slots.append({
                "slot_id": f"slot_{slot_counter}",
                "slot_number": slot_counter,
                "start_time": slot_start_time,
                "end_time": slot_end_time,
                "duration_min": current_session,
                "subject": subject["name"],
                "difficulty": subject["difficulty"],
                "priority_level": subject["priority_level"],
                "badge_color": subject["badge_color"],
                "strategy": subject["study_strategy"],
                "task_focus": task_focus,
                "is_break": False
            })
            slot_counter += 1
            remaining_min -= current_session
            current_minutes = end_minutes
            part_num += 1

            # Insert a healthy Pomodoro break
            if remaining_min > 0 or subject != interleaved_queue[-1]:
                break_start = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
                break_end_minutes = current_minutes + break_length_min
                break_end = f"{break_end_minutes // 60:02d}:{break_end_minutes % 60:02d}"

                timetable_slots.append({
                    "slot_id": f"break_{slot_counter}",
                    "slot_number": slot_counter,
                    "start_time": break_start,
                    "end_time": break_end,
                    "duration_min": break_length_min,
                    "subject": "Mind Refresh & Rest",
                    "difficulty": "none",
                    "priority_level": "Rest",
                    "badge_color": "secondary",
                    "strategy": "Hydration, stretching, or brief walk away from screens",
                    "task_focus": "Take 5 deep breaths, drink water, stay relaxed.",
                    "is_break": True
                })
                slot_counter += 1
                current_minutes = break_end_minutes

    return timetable_slots


def generate_study_plan(payload: dict) -> dict:
    """
    Main entry point for generating the complete Study Plan.
    Accepts:
    {
        "subjects": [
            {"name": "Machine Learning", "exam_date": "2026-10-05", "current_marks": 58, "difficulty": "weak"}
        ],
        "available_hours": 6.0,
        "start_time": "09:00",
        "session_length": 50,
        "break_length": 10
    }
    """
    raw_subjects = payload.get("subjects", [])
    available_hours = float(payload.get("available_hours", 4.0))
    start_time = payload.get("start_time", "09:00")
    session_length = int(payload.get("session_length", 50))
    break_length = int(payload.get("break_length", 10))

    if not raw_subjects:
        return {
            "success": False,
            "error": "No subjects provided. Please add at least one subject."
        }

    # 1. Calculate Priority Scores
    scored_subjects = []
    for subj in raw_subjects:
        scored = calculate_priority_score(subj)
        scored_subjects.append(scored)

    # Sort descending by priority score
    scored_subjects.sort(key=lambda x: x["raw_priority"], reverse=True)

    # 2. Allocate Hours
    allocated_subjects = allocate_study_hours(scored_subjects, available_hours)

    # 3. Generate Timetable
    timetable = generate_daily_timetable(
        allocated_subjects,
        start_time_str=start_time,
        session_length_min=session_length,
        break_length_min=break_length
    )

    # 4. Compile Overview Stats & Recommendations
    total_subjects = len(allocated_subjects)
    critical_count = sum(1 for s in allocated_subjects if s["priority_level"] == "Critical")
    weak_count = sum(1 for s in allocated_subjects if s["difficulty"] == "weak")
    avg_marks = round(sum(s["current_marks"] for s in allocated_subjects) / total_subjects, 1)

    study_tips = []
    if critical_count > 0:
        study_tips.append("⚠️ You have critical exams approaching with score gaps. Focus your prime morning hours on these topics!")
    if weak_count > 0:
        study_tips.append("🧠 Practice the Feynman Technique: Explain complex concepts from your weak subjects in simple terms out loud.")
    study_tips.append("⏱️ Use the embedded Pomodoro timer for each study block to maintain peak dopamine and focus.")
    study_tips.append("📝 Review the day's timetable entries before bed for 10 minutes to trigger memory consolidation during sleep.")

    return {
        "success": True,
        "summary": {
            "total_subjects": total_subjects,
            "available_hours": available_hours,
            "critical_count": critical_count,
            "weak_count": weak_count,
            "average_marks": avg_marks,
            "total_sessions": sum(1 for t in timetable if not t["is_break"]),
            "total_breaks": sum(1 for t in timetable if t["is_break"]),
            "study_tips": study_tips
        },
        "priority_subjects": allocated_subjects,
        "timetable": timetable
    }
