from typing import List
from datetime import date, datetime
from .models import Task, Status


def plan_day(tasks: List[Task], workday_hours: int = 8) -> List[Task]:
    """
    Rule-based day planning function.
    
    Implements the algorithm from rules.md:
    1. Filter tasks (status ≠ done, not blocked, within start date, no someday/on_hold tags)
    2. Sort by: pinned → overdue/today → priority → duration → created_at
    3. Greedy allocation within time budget (with 10% buffer)
    
    Args:
        tasks: List of all tasks
        workday_hours: Available working hours (default 8)
    
    Returns:
        List of tasks planned for the day
    """
    # Constants
    BUFFER_PERCENT = 0.10
    total_minutes = workday_hours * 60
    buffer_minutes = int(total_minutes * BUFFER_PERCENT)
    effective_minutes = total_minutes - buffer_minutes  # 432 min for 8h
    
    today = date.today()
    
    # Step 1: Filter tasks (Input Scope)
    filtered_tasks = []
    for task in tasks:
        # Skip done tasks
        if task.status == Status.DONE:
            continue
        
        # Skip blocked tasks
        if task.is_blocked:
            continue
        
        # Skip if start_date is in future
        if task.start_date and task.start_date > today:
            continue
        
        # Skip someday/on_hold tags
        if 'someday' in task.tags or 'on_hold' in task.tags:
            continue
        
        filtered_tasks.append(task)
    
    # Step 2: Sorting (Ranking Strategy)
    def sort_key(task: Task):
        """
        Waterfall sort:
        1. Pinned tasks (priority 0)
        2. Overdue & Today deadlines
        3. Priority (High > Medium > Low)
        4. Estimated Effort (Shortest Job First)
        5. Created At (older first)
        """
        # Pinned flag (0 for pinned, 1 for not pinned)
        pinned_flag = 0 if task.is_pinned else 1
        
        # Check urgency (overdue or due today)
        is_urgent = 0 if task.is_urgent(today) else 1
        
        # Priority value (inverted for descending: HIGH=3, MEDIUM=2, LOW=1)
        priority_map = {"high": 3, "medium": 2, "low": 1}
        # task.priority is already a string due to use_enum_values=True
        priority_val = -priority_map.get(task.priority, 0)
        
        # Duration (shortest first)
        duration = task.duration_minutes or 30
        
        # Created at (older first)
        created = task.created_at or datetime.max
        
        return (pinned_flag, is_urgent, priority_val, duration, created)
    
    sorted_tasks = sorted(filtered_tasks, key=sort_key)
    
    # Step 3: Greedy allocation
    daily_plan = []
    remaining_time = effective_minutes
    
    for task in sorted_tasks:
        task_duration = task.duration_minutes or 30
        
        # Edge case: task > effective_minutes (takes full day)
        if task_duration > effective_minutes:
            daily_plan.append(task)
            print(f"⚠️ Warning: Task '{task.title}' takes the full day ({task_duration} min)")
            break
        
        # Try to fit task (gap-filling strategy)
        if task_duration <= remaining_time:
            daily_plan.append(task)
            remaining_time -= task_duration
        # else: skip and try next task
    
    # Edge case: empty plan
    if not daily_plan:
        print("✅ All clear for today!")
    
    return daily_plan


def get_plan_summary(plan: List[Task]) -> dict:
    """
    Generate summary statistics for a daily plan.
    
    Returns:
        dict with total_tasks, total_minutes, total_hours, capacity_used_percent
    """
    if not plan:
        return {
            "total_tasks": 0,
            "total_minutes": 0,
            "total_hours": 0.0,
            "capacity_used_percent": 0.0
        }
    
    total_minutes = sum(task.duration_minutes or 30 for task in plan)
    effective_capacity = 432  # 8h with 10% buffer
    
    return {
        "total_tasks": len(plan),
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 1),
        "capacity_used_percent": round((total_minutes / effective_capacity) * 100, 1)
    }