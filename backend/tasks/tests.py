from datetime import date, timedelta

from django.test import SimpleTestCase

from .scoring import analyze_tasks, STRATEGIES, DEFAULT_STRATEGY


class TaskScoringTests(SimpleTestCase):
    """
    Unit tests for the Smart Task Analyzer scoring algorithm.

    These tests are focused on:
    - Urgency handling (overdue vs future tasks)
    - Strategy behavior (fastest_wins vs high_impact vs deadline_driven)
    - Dependency impact and circular dependency detection
    """

    def test_overdue_tasks_get_higher_priority(self):
        """
        Overdue tasks should score higher urgency than future tasks
        under the smart_balance strategy.
        """
        today = date.today()

        tasks = [
            {
                "id": "overdue",
                "title": "Overdue task",
                "due_date": (today - timedelta(days=2)).isoformat(),
                "estimated_hours": 3,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": "future",
                "title": "Future task",
                "due_date": (today + timedelta(days=5)).isoformat(),
                "estimated_hours": 3,
                "importance": 5,
                "dependencies": [],
            },
        ]

        scored = analyze_tasks(tasks, strategy_name="smart_balance", today=today)

        # First task in the sorted list should be the overdue one
        self.assertEqual(scored[0]["id"], "overdue")
        self.assertGreater(scored[0]["urgency_score"], scored[1]["urgency_score"])

    def test_fastest_wins_prefers_low_effort(self):
        """
        Under fastest_wins, a low-effort task should outrank a high-effort task
        when other factors are similar.
        """
        today = date.today()
        common_due = (today + timedelta(days=3)).isoformat()

        tasks = [
            {
                "id": "low_effort",
                "title": "Quick fix",
                "due_date": common_due,
                "estimated_hours": 1,
                "importance": 6,
                "dependencies": [],
            },
            {
                "id": "high_effort",
                "title": "Big refactor",
                "due_date": common_due,
                "estimated_hours": 12,
                "importance": 6,
                "dependencies": [],
            },
        ]

        scored = analyze_tasks(tasks, strategy_name="fastest_wins", today=today)

        self.assertEqual(scored[0]["id"], "low_effort")
        self.assertGreater(scored[0]["effort_score"], scored[1]["effort_score"])

    def test_high_impact_prefers_important_tasks(self):
        """
        Under high_impact, a high-importance task should outrank a low-importance one
        even if the low-importance task is slightly easier.
        """
        today = date.today()
        common_due = (today + timedelta(days=3)).isoformat()

        tasks = [
            {
                "id": "high_importance",
                "title": "Key feature",
                "due_date": common_due,
                "estimated_hours": 5,
                "importance": 9,
                "dependencies": [],
            },
            {
                "id": "low_importance",
                "title": "Minor cleanup",
                "due_date": common_due,
                "estimated_hours": 3,
                "importance": 3,
                "dependencies": [],
            },
        ]

        scored = analyze_tasks(tasks, strategy_name="high_impact", today=today)

        self.assertEqual(scored[0]["id"], "high_importance")
        self.assertGreater(scored[0]["importance_score"], scored[1]["importance_score"])

    def test_deadline_driven_prefers_earlier_due_date(self):
        """
        Under deadline_driven, the task with the closer deadline
        should come first when importance/effort are similar.
        """
        today = date.today()

        tasks = [
            {
                "id": "due_soon",
                "title": "Soon deadline",
                "due_date": (today + timedelta(days=1)).isoformat(),
                "estimated_hours": 4,
                "importance": 7,
                "dependencies": [],
            },
            {
                "id": "due_later",
                "title": "Later deadline",
                "due_date": (today + timedelta(days=10)).isoformat(),
                "estimated_hours": 4,
                "importance": 7,
                "dependencies": [],
            },
        ]

        scored = analyze_tasks(tasks, strategy_name="deadline_driven", today=today)

        self.assertEqual(scored[0]["id"], "due_soon")
        self.assertGreater(scored[0]["urgency_score"], scored[1]["urgency_score"])

    def test_circular_dependencies_are_flagged(self):
        """
        Tasks involved in a circular dependency should include
        a warning in their reasons list.
        """
        today = date.today()
        due = (today + timedelta(days=3)).isoformat()

        tasks = [
            {
                "id": "A",
                "title": "Task A",
                "due_date": due,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": ["B"],
            },
            {
                "id": "B",
                "title": "Task B",
                "due_date": due,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": ["A"],
            },
        ]

        scored = analyze_tasks(tasks, strategy_name=DEFAULT_STRATEGY, today=today)

        # Both tasks are part of a cycle; each should have a cycle warning
        for t in scored:
            self.assertTrue(
                any(
                    "circular dependency" in reason.lower()
                    for reason in t.get("reasons", [])
                ),
                msg=f"Task {t['id']} should be flagged as circular.",
            )
