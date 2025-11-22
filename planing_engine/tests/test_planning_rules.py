"""
Unit tests for planning engine rules validation.

Tests cover:
1. Time capacity overflow handling
2. Priority-based sorting with same deadlines
3. Tasks with/without deadlines prioritization
"""

import unittest
from datetime import date, datetime, timedelta
import sys
import os

# Add parent directory to path for imports
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
    **kwargs
) -> Task:
    """Helper to create test tasks"""
    return Task(
        id=id,
        title=title,
        priority=priority,
        duration_minutes=duration_minutes,
        status=status,
        deadline=deadline,
        created_at=datetime.now() - timedelta(days=id),
        **kwargs
    )


# ============================================================================
# ТЕСТ 1: Переповнення часу - беруться тільки задачі що встигають
# ============================================================================

class TestTimeCapacityOverflow(unittest.TestCase):
    """Test that only tasks fitting in time budget are selected"""
    
    def test_tasks_exceeding_capacity_are_skipped(self):
        """When total task time > 432 min, only fitting tasks are included"""
        tasks = [
            create_task(1, "Task 1", priority=Priority.HIGH, duration_minutes=150),
            create_task(2, "Task 2", priority=Priority.HIGH, duration_minutes=150),
            create_task(3, "Task 3", priority=Priority.HIGH, duration_minutes=150),
            create_task(4, "Task 4", priority=Priority.HIGH, duration_minutes=150),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        summary = get_plan_summary(plan)
        
        # Should include only 2 tasks (300 min total)
        self.assertEqual(len(plan), 2, "Should select exactly 2 tasks")
        self.assertEqual(summary["total_minutes"], 300, "Total should be 300 minutes")
        self.assertLessEqual(summary["total_minutes"], 432, "Should not exceed capacity")
    
    def test_exactly_at_capacity_limit(self):
        """Tasks that exactly fill capacity should all be included"""
        tasks = [
            create_task(1, "Task 1", duration_minutes=216),
            create_task(2, "Task 2", duration_minutes=216),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        summary = get_plan_summary(plan)
        
        self.assertEqual(len(plan), 2)
        self.assertEqual(summary["total_minutes"], 432)
        self.assertEqual(summary["capacity_used_percent"], 100.0)
    
    def test_gap_filling_with_smaller_tasks(self):
        """Should skip large tasks and continue with smaller ones"""
        tasks = [
            create_task(1, "Small 1", priority=Priority.HIGH, duration_minutes=100),
            create_task(2, "Huge task", priority=Priority.HIGH, duration_minutes=400),
            create_task(3, "Small 2", priority=Priority.HIGH, duration_minutes=100),
            create_task(4, "Small 3", priority=Priority.HIGH, duration_minutes=100),
            create_task(5, "Small 4", priority=Priority.HIGH, duration_minutes=100),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        
        # Should get 4 small tasks (400 min), skipping the huge one
        self.assertEqual(len(plan), 4)
        self.assertNotIn(2, [t.id for t in plan])
        self.assertEqual(sum(t.duration_minutes for t in plan), 400)
    
    def test_multiple_tasks_dont_fit_after_first(self):
        """Multiple large tasks that don't fit should all be skipped"""
        tasks = [
            create_task(1, "Fits", priority=Priority.HIGH, duration_minutes=200),
            create_task(2, "Too big 1", priority=Priority.HIGH, duration_minutes=300),
            create_task(3, "Too big 2", priority=Priority.HIGH, duration_minutes=300),
            create_task(4, "Small", priority=Priority.HIGH, duration_minutes=50),
        ]
        
        plan = plan_day(tasks)
        
        # Should get task 1 (200) and task 4 (50) = 250 min
        self.assertEqual(len(plan), 2)
        self.assertIn(1, [t.id for t in plan])
        self.assertIn(4, [t.id for t in plan])
        self.assertEqual(sum(t.duration_minutes for t in plan), 250)


# ============================================================================
# ТЕСТ 2: Пріоритети - вища пріоритетна задача завжди раніше при однакових дедлайнах
# ============================================================================

class TestPriorityOrdering(unittest.TestCase):
    """Test that higher priority tasks come before lower priority ones"""
    
    def test_high_before_medium_same_deadline(self):
        """HIGH priority should come before MEDIUM with same deadline"""
        today = date.today()
        tasks = [
            create_task(1, "Medium prio", priority=Priority.MEDIUM, 
                       duration_minutes=30, deadline=today),
            create_task(2, "High prio", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=today),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0].priority, Priority.HIGH)
        self.assertEqual(plan[0].id, 2)
        self.assertEqual(plan[1].priority, Priority.MEDIUM)
        self.assertEqual(plan[1].id, 1)
    
    def test_medium_before_low_same_deadline(self):
        """MEDIUM priority should come before LOW with same deadline"""
        today = date.today()
        tasks = [
            create_task(1, "Low prio", priority=Priority.LOW, 
                       duration_minutes=30, deadline=today),
            create_task(2, "Medium prio", priority=Priority.MEDIUM, 
                       duration_minutes=30, deadline=today),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0].priority, Priority.MEDIUM)
        self.assertEqual(plan[1].priority, Priority.LOW)
    
    def test_all_three_priorities_same_deadline(self):
        """Test full priority ordering: HIGH > MEDIUM > LOW"""
        tomorrow = date.today() + timedelta(days=1)
        tasks = [
            create_task(1, "Low", priority=Priority.LOW, deadline=tomorrow),
            create_task(2, "High", priority=Priority.HIGH, deadline=tomorrow),
            create_task(3, "Medium", priority=Priority.MEDIUM, deadline=tomorrow),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 3)
        priorities = [t.priority for t in plan]
        self.assertEqual(priorities, [Priority.HIGH, Priority.MEDIUM, Priority.LOW])
    
    def test_priority_overrides_creation_date(self):
        """Higher priority task should come first even if created later"""
        today = date.today()
        tasks = [
            create_task(1, "Old low", priority=Priority.LOW, 
                       duration_minutes=30, deadline=today),
            create_task(5, "Recent high", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=today),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(plan[0].priority, Priority.HIGH)
        self.assertEqual(plan[0].id, 5)
    
    def test_same_priority_sorted_by_duration(self):
        """Same priority tasks should be sorted by duration (shortest first)"""
        today = date.today()
        tasks = [
            create_task(1, "Long", priority=Priority.HIGH, 
                       duration_minutes=120, deadline=today),
            create_task(2, "Short", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=today),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(plan[0].duration_minutes, 30)
        self.assertEqual(plan[1].duration_minutes, 120)


# ============================================================================
# ТЕСТ 3: Дедлайни - задача без дедлайну менш пріоритетна за задачу з дедлайном
# ============================================================================

class TestDeadlinePrioritization(unittest.TestCase):
    """Test that tasks with deadlines come before tasks without deadlines"""
    
    def test_with_deadline_before_without_deadline(self):
        """Task with deadline should come before task without deadline"""
        today = date.today()
        tasks = [
            create_task(1, "No deadline", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=None),
            create_task(2, "Has deadline", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=today),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 2)
        self.assertIsNotNone(plan[0].deadline)
        self.assertEqual(plan[0].id, 2)
        self.assertIsNone(plan[1].deadline)
        self.assertEqual(plan[1].id, 1)
    
    def test_overdue_before_no_deadline(self):
        """Overdue task should come before task with no deadline"""
        yesterday = date.today() - timedelta(days=1)
        tasks = [
            create_task(1, "No deadline", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=None),
            create_task(2, "Overdue", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=yesterday),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 2)
        self.assertTrue(plan[0].is_overdue())
        self.assertEqual(plan[0].id, 2)
    
    def test_future_deadline_before_no_deadline(self):
        """Task with future deadline should still come before no deadline"""
        tomorrow = date.today() + timedelta(days=1)
        tasks = [
            create_task(1, "No deadline", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=None),
            create_task(2, "Future deadline", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=tomorrow),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0].deadline, tomorrow)
        self.assertEqual(plan[0].id, 2)
    
    def test_multiple_deadlines_vs_no_deadline(self):
        """Multiple deadline tasks should all come before no-deadline task"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        tasks = [
            create_task(1, "No deadline", priority=Priority.HIGH, duration_minutes=30),
            create_task(2, "Today", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=today),
            create_task(3, "Tomorrow", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=tomorrow),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 3)
        self.assertIsNotNone(plan[0].deadline)
        self.assertIsNotNone(plan[1].deadline)
        self.assertIsNone(plan[2].deadline)
        self.assertEqual(plan[2].id, 1)
    
    def test_deadline_priority_interaction(self):
        """Low priority with deadline should beat high priority without deadline"""
        today = date.today()
        tasks = [
            create_task(1, "High no deadline", priority=Priority.HIGH, 
                       duration_minutes=30, deadline=None),
            create_task(2, "Low with deadline", priority=Priority.LOW, 
                       duration_minutes=30, deadline=today),
        ]
        
        plan = plan_day(tasks)
        
        self.assertEqual(len(plan), 2)
        self.assertIsNotNone(plan[0].deadline)
        self.assertEqual(plan[0].priority, Priority.LOW)
        self.assertEqual(plan[0].id, 2)


# ============================================================================
# Комплексні інтеграційні тести
# ============================================================================

class TestComplexScenarios(unittest.TestCase):
    """Integration tests combining multiple rules"""
    
    def test_realistic_mixed_scenario(self):
        """Test realistic scenario with mixed priorities, deadlines, and durations"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        tasks = [
            create_task(1, "Pinned critical", priority=Priority.HIGH, 
                       duration_minutes=60, deadline=today, is_pinned=True),
            create_task(2, "Overdue high", priority=Priority.HIGH, 
                       duration_minutes=90, deadline=yesterday),
            create_task(3, "Today high", priority=Priority.HIGH, 
                       duration_minutes=45, deadline=today),
            create_task(4, "Tomorrow medium", priority=Priority.MEDIUM, 
                       duration_minutes=60, deadline=tomorrow),
            create_task(5, "High no deadline", priority=Priority.HIGH, 
                       duration_minutes=90),
            create_task(6, "Low no deadline", priority=Priority.LOW, 
                       duration_minutes=30),
            create_task(7, "Extra task", priority=Priority.HIGH, 
                       duration_minutes=200),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        summary = get_plan_summary(plan)
        
        self.assertGreater(len(plan), 0)
        self.assertTrue(plan[0].is_pinned)
        self.assertLessEqual(summary["total_minutes"], 432)
        
        no_deadline_tasks = [t for t in plan if t.deadline is None]
        if no_deadline_tasks:
            last_tasks = plan[-len(no_deadline_tasks):]
            self.assertTrue(any(t.deadline is None for t in last_tasks))
    
    def test_capacity_forces_priority_trade_off(self):
        """Test that capacity limits force choosing between priorities"""
        tasks = [
            create_task(1, "High 1", priority=Priority.HIGH, duration_minutes=200),
            create_task(2, "High 2", priority=Priority.HIGH, duration_minutes=200),
            create_task(3, "High 3", priority=Priority.HIGH, duration_minutes=200),
            create_task(4, "Medium", priority=Priority.MEDIUM, duration_minutes=50),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        
        self.assertEqual(len(plan), 2)
        self.assertTrue(all(t.priority == Priority.HIGH for t in plan))
        self.assertNotIn(4, [t.id for t in plan])
    
    def test_all_rules_combined(self):
        """Test all rules working together: capacity + priority + deadline"""
        today = date.today()
        
        tasks = [
            create_task(1, "High w/ deadline", priority=Priority.HIGH, 
                       duration_minutes=100, deadline=today),
            create_task(2, "Med w/ deadline", priority=Priority.MEDIUM, 
                       duration_minutes=100, deadline=today),
            create_task(3, "High no deadline", priority=Priority.HIGH, 
                       duration_minutes=100),
            create_task(4, "Low w/ deadline", priority=Priority.LOW, 
                       duration_minutes=100, deadline=today),
            create_task(5, "Extra", priority=Priority.HIGH, 
                       duration_minutes=200, deadline=today),
        ]
        
        plan = plan_day(tasks, workday_hours=8)
        
        self.assertGreaterEqual(len(plan), 3)
        
        for i in range(min(3, len(plan))):
            self.assertIsNotNone(plan[i].deadline, 
                               f"Task {i} should have deadline")


if __name__ == "__main__":
    unittest.main(verbosity=2)