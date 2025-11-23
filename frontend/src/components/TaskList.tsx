export type Task = {
  id: number
  title: string
  status: 'todo' | 'in-progress' | 'done'
}

type TaskListProps = {
  tasks: Task[]
  onToggle?: (id: number) => void
}

const statusLabel: Record<Task['status'], string> = {
  todo: 'To do',
  'in-progress': 'In progress',
  done: 'Done',
}

const TaskList = ({ tasks, onToggle }: TaskListProps) => {
  if (!tasks.length) {
    return <p className="muted">No tasks yet. Add your first one to get going.</p>
  }

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id} className={`task-card ${task.status}`}>
          <div className="task-main">
            <input
              type="checkbox"
              checked={task.status === 'done'}
              onChange={() => onToggle?.(task.id)}
              aria-label={`Mark ${task.title} as done`}
            />
            <div>
              <p className="task-title">{task.title}</p>
              <span className={`pill ${task.status}`}>{statusLabel[task.status]}</span>
            </div>
          </div>
          <div className="task-actions">
            <button
              type="button"
              className="button ghost small"
              onClick={() => onToggle?.(task.id)}
            >
              {task.status === 'done' ? 'Reopen' : 'Complete'}
            </button>
          </div>
        </li>
      ))}
    </ul>
  )
}

export default TaskList
