"""
Compass AI - Phase 7 Roadmap Engine Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile import UserProfile
from core.roadmap import generate_roadmap


def test_data_engineer_roadmap_generation():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Engineer",
        skills={
            "Python": "intermediate",
            "SQL": "beginner"
        },
        deadline_weeks=12,
        hours_per_week=10
    )
    
    report = generate_roadmap(profile)
    
    print(f"✓ Goal: {report.goal}")
    print(f"✓ Deadline: {report.deadline_weeks} weeks ({report.hours_per_week}h/week)")
    print(f"✓ Total Allocated Weeks: {report.total_weeks_allocated} weeks")
    print(f"✓ Total Estimated Hours: {report.total_estimated_hours} hours")
    print(f"✓ Scheduled Items Count: {len(report.items)}")
    print(f"✓ Overflow Items Count: {len(report.overflow_items)}")
    
    for item in report.items:
        print(f"   Week {item.week_start}-{item.week_end}: [{item.priority_category}] {item.skill} ({item.estimated_hours}h) - Milestone: {item.milestone[:45]}...")
    
    assert len(report.items) > 0, "Roadmap should have scheduled items"
    assert report.total_weeks_allocated <= report.deadline_weeks, f"Allocated weeks ({report.total_weeks_allocated}) must fit deadline ({report.deadline_weeks})"
    
    first_item = report.items[0]
    assert first_item.week_start == 1, "First item must start on week 1"
    
    print("✓ Roadmap generation test passed successfully.")

if __name__ == "__main__":
    test_data_engineer_roadmap_generation()
    print("✓ ALL ROADMAP ENGINE TESTS PASSED SUCCESSFULLY!")
