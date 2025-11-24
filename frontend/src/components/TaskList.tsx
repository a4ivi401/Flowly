import { type Task } from '../api/client'

type TaskListProps = {
  tasks: Task[]
  onEdit?: (task: Task) => void
  onDelete?: (id: number) => void
}

const statusLabel: Record<Task['status'], string> = {
  pending: 'Pending',
  in_progress: 'In progress',
  completed: 'Completed',
  cancelled: 'Cancelled',
}

const statusTone: Record<Task['status'], string> = {
  pending: 'todo',
  in_progress: 'in-progress',
  completed: 'done',
  cancelled: 'todo',
}

const priorityLabel: Record<number, string> = {
  1: 'High',
  2: 'High',
  3: 'Medium',
  4: 'Low',
  5: 'Low',
}

const priorityTone: Record<number, string> = {
  1: 'high',
  2: 'high',
  3: 'medium',
  4: 'low',
  5: 'low',
}

const formatDate = (isoDate: string | null) => {
  if (!isoDate) return '—'
  const date = new Date(isoDate)
  return isNaN(date.getTime()) ? '—' : date.toLocaleDateString()
}

const TaskList = ({ tasks, onEdit, onDelete }: TaskListProps) => {
  if (!tasks.length) {
    return <p className="muted">Список порожній.</p>
  }

  return (
    <div className="task-table">
      <div className="task-table__head">
        <span>Назва</span>
        <span>Пріоритет</span>
        <span>Тривалість</span>
        <span>Дедлайн</span>
        <span>Статус</span>
        <span>Дії</span>
      </div>
      <div className="task-table__body">
        {tasks.map((task) => (
          <div className="task-row" key={task.id}>
            <div className="cell title">
              <p className="task-title">{task.title}</p>
              {task.description ? <p className="muted small">{task.description}</p> : null}
            </div>
            <div className="cell priority">
              <span className={`pill priority-${priorityTone[task.priority ?? 3]}`}>
                {priorityLabel[task.priority ?? 3]}
              </span>
            </div>
            <div className="cell">{task.duration_minutes ? `${task.duration_minutes} хв` : '—'}</div>
            <div className="cell">{formatDate(task.deadline)}</div>
            <div className="cell">
              <span className={`pill ${statusTone[task.status]}`}>{statusLabel[task.status]}</span>
            </div>
            <div className="cell actions">
              <button className="button ghost small" type="button" onClick={() => onEdit?.(task)}>
                Редагувати
              </button>
              <button className="button danger small" type="button" onClick={() => onDelete?.(task.id)}>
                Видалити
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TaskList
