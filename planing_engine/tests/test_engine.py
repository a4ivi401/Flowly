import unittest
from datetime import date, datetime, timedelta
from io import StringIO
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from planing_engine.models import Task, Priority, Status
from planing_engine.engine import plan_day, get_plan_summary


def create_task(
    id: int,
    title: str,
    priority: Priority = Priority.MEDIUM,
    duration_minutes: int = 30,
    status: Status = Status.TODO,
    deadline: date = None,
    is_pinned: bool = False,
    is_blocked: bool = False,
    tags: list = None,
    start_date: date = None
) -> Task:
    """Helper to create test tasks"""
    return Task(
        id=id,
        title=title,
        priority=priority,
        duration_minutes=duration_minutes,
        status=status,
        deadline=deadline,
        is_pinned=is_pinned,
        is_blocked=is_blocked,
        tags=tags or [],
        start_date=start_date,
        created_at=datetime.now() - timedelta(days=id)
    )


class TestPlanDay(unittest.TestCase):
    """Test suite for plan_day function"""
    
    def test_empty_task_list(self):
        """Should return empty plan for empty input"""
        plan = plan_day([])
        self.assertEqual(len(plan), 0)
    
    def test_filters_done_tasks(self):
        """Should exclude tasks with status=DONE"""
        tasks = [
            create_task(1, "Done task", status=Status.DONE),
            create_task(2, "Todo task", status=Status.TODO)
        ]
        plan = plan_day(tasks)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].id, 2)
    
    def test_pinned_tasks_first(self):
        """Pinned tasks should appear first regardless of priority"""
        tasks = [
            create_task(1, "High prio", priority=Priority.HIGH, duration_minutes=30),
            create_task(2, "Pinned low", priority=Priority.LOW, duration_minutes=30, is_pinned=True)
        ]
        plan = plan_day(tasks)
        self.assertEqual(plan[0].id, 2)
    
    def test_priority_sorting(self):
        """Should sort by priority: HIGH > MEDIUM > LOW"""
        tasks = [
            create_task(1, "Low", priority=Priority.LOW, duration_minutes=30),
            create_task(2, "High", priority=Priority.HIGH, duration_minutes=30),
            create_task(3, "Medium", priority=Priority.MEDIUM, duration_minutes=30)
        ]
        plan = plan_day(tasks)
        self.assertEqual(plan[0].priority, Priority.HIGH)
        self.assertEqual(plan[1].priority, Priority.MEDIUM)
        self.assertEqual(plan[2].priority, Priority.LOW)


class TestRealisticScenario(unittest.TestCase):
    """Integration test"""
    
    def test_realistic_daily_planning(self):
        """Test a realistic daily planning scenario"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        tasks = [
            create_task(1, "Critical bug fix", priority=Priority.HIGH, 
                       duration_minutes=60, deadline=today, is_pinned=True),
            create_task(2, "Overdue report", priority=Priority.HIGH,
                       duration_minutes=90, deadline=yesterday),
            create_task(3, "Code review", priority=Priority.HIGH,
                       duration_minutes=30),
            create_task(8, "Done task", status=Status.DONE),
            create_task(9, "Blocked task", is_blocked=True),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        summary = get_plan_summary(plan)
        
        self.assertGreater(len(plan), 0)
        self.assertTrue(plan[0].is_pinned)
        self.assertLessEqual(summary["total_minutes"], 432)
        
        print(f"\n📋 Daily Plan: {summary['total_tasks']} tasks, "
              f"{summary['total_hours']}h ({summary['capacity_used_percent']}%)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
