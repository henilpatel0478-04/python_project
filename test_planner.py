"""
Unit tests for Study Planner engine
"""
import unittest
from datetime import date, timedelta
from planner_engine import (
    calculate_days_left,
    get_difficulty_multiplier,
    calculate_priority_score,
    allocate_study_hours,
    generate_daily_timetable,
    generate_study_plan
)

class TestPlannerEngine(unittest.TestCase):
    def test_days_left(self):
        today = date(2026, 9, 20)
        future_5 = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        past_2 = (today - timedelta(days=2)).strftime("%Y-%m-%d")
        
        self.assertEqual(calculate_days_left(future_5, base_date=today), 5)
        self.assertEqual(calculate_days_left(past_2, base_date=today), 0)

    def test_multipliers(self):
        self.assertEqual(get_difficulty_multiplier("weak"), 1.55)
        self.assertEqual(get_difficulty_multiplier("neutral"), 1.00)
        self.assertEqual(get_difficulty_multiplier("strong"), 0.70)

    def test_priority_score(self):
        today = date(2026, 9, 20)
        urgent_weak = {
            "name": "Machine Learning",
            "exam_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "current_marks": 42,
            "difficulty": "weak"
        }
        res = calculate_priority_score(urgent_weak, base_date=today)
        self.assertIn(res["priority_level"], ["Critical", "High"])
        self.assertGreater(res["raw_priority"], 80)

    def test_hour_allocation(self):
        scored = [
            {"name": "ML", "raw_priority": 120, "difficulty": "weak", "priority_level": "Critical"},
            {"name": "Python", "raw_priority": 40, "difficulty": "strong", "priority_level": "Moderate"}
        ]
        allocated = allocate_study_hours(scored, total_available_hours=4.0)
        total_allocated = sum(s["recommended_hours"] for s in allocated)
        self.assertAlmostEqual(total_allocated, 4.0, delta=0.5)
        self.assertGreater(allocated[0]["recommended_hours"], allocated[1]["recommended_hours"])

    def test_full_plan_generation(self):
        payload = {
            "subjects": [
                {"name": "Deep Learning", "exam_date": "2026-09-28", "current_marks": 50, "difficulty": "weak"},
                {"name": "Linear Algebra", "exam_date": "2026-10-02", "current_marks": 75, "difficulty": "neutral"},
                {"name": "Python Essentials", "exam_date": "2026-10-15", "current_marks": 90, "difficulty": "strong"}
            ],
            "available_hours": 5.0,
            "start_time": "09:00",
            "session_length": 50,
            "break_length": 10
        }
        plan = generate_study_plan(payload)
        self.assertTrue(plan["success"])
        self.assertEqual(len(plan["priority_subjects"]), 3)
        self.assertGreater(len(plan["timetable"]), 0)
        self.assertIn("summary", plan)

if __name__ == "__main__":
    unittest.main()
