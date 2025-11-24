from typing import List
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class Status(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@dataclass
class Task:
    id: str
    title: str
    status: Status
    priority: Priority
    duration_minutes: int = 30  # Default 30 min
    deadline: date = None
    created_at: datetime = None
    is_blocked: bool = False
    start_date: date = None
    tags: List[str] = None
    is_pinned: bool = False

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()


def plan_day(tasks: List[Task], workday_hours: int = 8) -> List[Task]:
    """
    Rule-based day planning function.
    
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
    effective_minutes = total_minutes - buffer_minutes
    
    today = date.today()
    tomorrow = date.today().replace(day=today.day + 1) if today.day < 28 else today
    
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
        # Pinned tasks go first (priority 0)
        if task.is_pinned:
            return (0, 0, 0, task.created_at or datetime.min)
        
        # Check if overdue or due today
        is_urgent = 0
        if task.deadline:
            if task.deadline < tomorrow:
                is_urgent = 1  # Urgent = higher priority in sort
        
        # Priority value (inverted for descending)
        priority_val = -task.priority.value
        
        # Duration (shortest first)
        duration = task.duration_minutes or 30
        
        # Created at (older first)
        created = task.created_at or datetime.max
        
        return (-is_urgent, priority_val, duration, created)
    
    sorted_tasks = sorted(filtered_tasks, key=sort_key)
    
    # Step 3: Greedy allocation
    daily_plan = []
    remaining_time = effective_minutes
    
    for task in sorted_tasks:
        task_duration = task.duration_minutes or 30
        
        # Edge case: task > effective_minutes
        if task_duration > effective_minutes:
            daily_plan.append(task)
            print(f"⚠️ Warning: Task '{task.title}' takes the full day ({task_duration} min)")
            break
        
        # Try to fit task
        if task_duration <= remaining_time:
            daily_plan.append(task)
            remaining_time -= task_duration
        # else: skip and try next (gap-filling strategy)
    
    # Edge case: empty plan
    if not daily_plan:
        print("✅ All clear for today!")
    
    return daily_plan


# === TEST SCRIPT ===
if __name__ == "__main__":
    print("🧪 Testing Day Planning Algorithm\n")
    
    # Create test tasks
    test_tasks = [
        Task(id="1", title="Fix critical bug", status=Status.TODO, 
             priority=Priority.HIGH, duration_minutes=60, 
             deadline=date.today(), is_pinned=True),
        
        Task(id="2", title="Code review", status=Status.TODO,
             priority=Priority.MEDIUM, duration_minutes=45),
        
        Task(id="3", title="Update docs", status=Status.TODO,
             priority=Priority.LOW, duration_minutes=30),
        
        Task(id="4", title="Team meeting", status=Status.TODO,
             priority=Priority.HIGH, duration_minutes=90),
        
        Task(id="5", title="Refactor module", status=Status.TODO,
             priority=Priority.MEDIUM, duration_minutes=120),
        
        Task(id="6", title="Write tests", status=Status.TODO,
             priority=Priority.HIGH, duration_minutes=75),
        
        Task(id="7", title="Completed task", status=Status.DONE,
             priority=Priority.HIGH, duration_minutes=30),
        
        Task(id="8", title="Blocked task", status=Status.TODO,
             priority=Priority.HIGH, duration_minutes=30, is_blocked=True),
        
        Task(id="9", title="Future task", status=Status.TODO,
             priority=Priority.HIGH, duration_minutes=30,
             start_date=date(2025, 12, 31)),
        
        Task(id="10", title="Someday maybe", status=Status.TODO,
             priority=Priority.MEDIUM, duration_minutes=60, tags=["someday"]),
    ]
    
    # Run planning
    plan = plan_day(test_tasks, workday_hours=8)
    
    # Display results
    print(f"📋 Daily Plan ({len(plan)} tasks):\n")
    total_planned = 0
    for i, task in enumerate(plan, 1):
        pin_icon = "📌 " if task.is_pinned else ""
        print(f"{i}. {pin_icon}{task.title}")
        print(f"   Priority: {task.priority.name} | Duration: {task.duration_minutes} min")
        total_planned += task.duration_minutes
    
    print(f"\n⏱️ Total planned time: {total_planned} min ({total_planned/60:.1f} hours)")
    print(f"💡 Effective capacity used: {total_planned}/432 min ({total_planned/432*100:.1f}%)")