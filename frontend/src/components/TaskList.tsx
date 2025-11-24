import { type Task } from '../api/client'

type TaskListProps = {
  tasks: Task[]
  onToggle?: (id: number) => void
}

const statusLabel: Record<Task['status'], string> = {
  pending: 'Pending',
  in_progress: 'In progress',
  completed: 'Completed',
  cancelled: 'Cancelled',
}

const statusClass: Record<Task['status'], string> = {
  pending: 'todo',
  in_progress: 'in-progress',
  completed: 'done',
  cancelled: 'todo',
}

const TaskList = ({ tasks, onToggle }: TaskListProps) => {
  if (!tasks.length) {
    return <p className="muted">No tasks yet. Add your first one to get going.</p>
  }

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id} className={`task-card ${statusClass[task.status]}`}>
          <div className="task-main">
            <input
              type="checkbox"
              checked={task.status === 'completed'}
              onChange={() => onToggle?.(task.id)}
              aria-label={`Mark ${task.title} as done`}
            />
            <div>
              <p className="task-title">{task.title}</p>
              <span className={`pill ${statusClass[task.status]}`}>{statusLabel[task.status]}</span>
            </div>
          </div>
          <div className="task-actions">
            <button
              type="button"
              className="button ghost small"
              onClick={() => onToggle?.(task.id)}
            >
              {task.status === 'completed' ? 'Reopen' : 'Complete'}
            </button>
          </div>
        </li>
      ))}
    </ul>
  )
}

export default TaskList
