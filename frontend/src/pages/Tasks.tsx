import { useEffect, useMemo, useState } from 'react'
import { getTasks, type Task } from '../api/client'
import flowlyLogo from '../assets/flowly-logo.svg'

const priorityTone = (priority: number | null) => {
  if (priority === null || priority === undefined) return 'medium'
  if (priority <= 2) return 'high'
  if (priority === 3) return 'medium'
  return 'low'
}

const priorityLabel = (priority: number | null) => {
  if (priority === null || priority === undefined) return 'Medium'
  if (priority <= 2) return 'High'
  if (priority === 3) return 'Medium'
  return 'Low'
}

const formatDate = (iso: string | null) => {
  if (!iso) return '—'
  const date = new Date(iso)
  return isNaN(date.getTime()) ? '—' : date.toLocaleDateString()
}

const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const fetchTasks = async () => {
      try {
        const data = await getTasks()
        if (mounted) setTasks(data)
      } catch (err) {
        console.error('Не вдалося завантажити задачі', err)
        if (mounted) setError('Не вдалося завантажити задачі')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    fetchTasks()
    return () => {
      mounted = false
    }
  }, [])

  const grouped = useMemo(() => {
    const grid: Task[][] = [[], [], [], [], [], []]
    tasks.forEach((task, index) => {
      const column = index % 2
      const row = Math.floor(index / 2)
      if (!grid[row]) grid[row] = []
      grid[row][column] = task
    })
    return grid
  }, [tasks])

  return (
    <div className="tasks-screen">
      <header className="tasks-topbar">
        <div className="tasks-brand">
          <img src={flowlyLogo} alt="Flowly" />
        </div>
        <div className="tasks-title">
          <span>MY task</span>
          <span className="tasks-plus">+</span>
        </div>
      </header>

      <main className="tasks-layout">
        {loading && <p className="muted">Завантаження задач...</p>}
        {error && <p className="muted">{error}</p>}
        {!loading && !error && !tasks.length && <p className="muted">Список порожній.</p>}

        <div className="tasks-grid">
          {grouped.map((row, rowIndex) => (
            <div className="tasks-row" key={rowIndex}>
              {row.map((task, colIndex) =>
                task ? (
                  <article
                    key={task.id}
                    className={`task-card-pill priority-${priorityTone(task.priority)}`}
                  >
                    <div>
                      <p className="task-pill-title">{task.title}</p>
                      {task.description ? (
                        <p className="task-pill-desc">{task.description}</p>
                      ) : (
                        <p className="task-pill-desc muted">Опис відсутній</p>
                      )}
                      <div className="task-pill-meta">
                        <span className={`priority-text ${priorityTone(task.priority)}`}>
                          {priorityLabel(task.priority)}
                        </span>
                        <span className="deadline">{formatDate(task.deadline)}</span>
                      </div>
                    </div>
                    <div className="duration">{task.duration_minutes ? `${task.duration_minutes} min` : '—'}</div>
                  </article>
                ) : (
                  <div className="task-placeholder" key={`${rowIndex}-${colIndex}`} />
                ),
              )}
            </div>
          ))}
        </div>

        <div className="tasks-footer">
          <div className="coach-card">
            <p>
              Ваш Особистий AI-Порадник вже тут!
              <br />
              Потрібна допомога з плануванням?
              <br />
              Отримайте індивідуальні поради, ефективні стратегії та експертні підказки щодо виконання
              поточних завдань!
            </p>
          </div>
          <div className="tasks-search">
            <span className="search-icon">🔍</span>
            <input placeholder="Search Here" />
            <span className="mic-icon">🎤</span>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Tasks
