import { useEffect, useMemo, useState } from 'react'
import { deleteTask, getTasks, updateTask, type Task, type TaskStatus } from '../api/client'
import TaskList from '../components/TaskList'

const TasksPage = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<Task | null>(null)

  useEffect(() => {
    let isMounted = true

    const fetchTasks = async () => {
      try {
        const remoteTasks = await getTasks()
        if (isMounted) {
          setTasks(remoteTasks)
        }
      } catch (err) {
        console.error('Не вдалося завантажити задачі', err)
        if (isMounted) {
          setError('Не вдалося завантажити задачі')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchTasks()

    return () => {
      isMounted = false
    }
  }, [])

  const stats = useMemo(() => {
    const completed = tasks.filter((task) => task.status === 'completed').length
    return { total: tasks.length, completed }
  }, [tasks])

  const handleDelete = async (id: number) => {
    const target = tasks.find((task) => task.id === id)
    if (!target) return
    const confirmed = window.confirm(`Видалити задачу "${target.title}"?`)
    if (!confirmed) return

    try {
      await deleteTask(id)
      setTasks((current) => current.filter((task) => task.id !== id))
    } catch (err) {
      console.error('Не вдалося видалити задачу', err)
      setError('Не вдалося видалити задачу')
    }
  }

  const handleEditSave = async (updated: Partial<Task> & { id: number }) => {
    try {
      const result = await updateTask(updated.id, updated)
      setTasks((current) => current.map((task) => (task.id === updated.id ? result : task)))
      setEditing(null)
    } catch (err) {
      console.error('Не вдалося оновити задачу', err)
      setError('Не вдалося оновити задачу')
    }
  }

  const formatValue = (value: string | number | null | undefined) => {
    if (value === null || value === undefined) return ''
    return String(value)
  }

  const formatDateTimeLocal = (value: string | null) => {
    if (!value) return ''
    const date = new Date(value)
    if (isNaN(date.getTime())) return ''
    const pad = (n: number) => String(n).padStart(2, '0')
    const year = date.getFullYear()
    const month = pad(date.getMonth() + 1)
    const day = pad(date.getDate())
    const hours = pad(date.getHours())
    const minutes = pad(date.getMinutes())
    return `${year}-${month}-${day}T${hours}:${minutes}`
  }

  return (
    <section id="tasks" className="panel">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Tasks</p>
          <h2>Plan and track your work</h2>
          <p className="muted">
            Capture tasks, flip them to done, and keep the AI manager aligned with your day.
          </p>
        </div>
        <div className="stat">
          <span className="stat-label">Complete</span>
          <span className="stat-value">
            {stats.completed}/{stats.total}
          </span>
        </div>
      </header>

      {editing ? (
        <div className="edit-form">
          <h3>Редагувати задачу</h3>
          <form
            onSubmit={(event) => {
              event.preventDefault()
              const formData = new FormData(event.currentTarget)
              handleEditSave({
                id: editing.id,
                title: formData.get('title') as string,
                description: (formData.get('description') as string) || null,
                priority: formData.get('priority') ? Number(formData.get('priority')) : null,
                duration_minutes: formData.get('duration') ? Number(formData.get('duration')) : null,
                deadline: (formData.get('deadline') as string) || null,
                status: (formData.get('status') as TaskStatus) || editing.status,
              })
            }}
          >
            <div className="form-grid">
              <label>
                Назва
                <input name="title" defaultValue={formatValue(editing.title)} required />
              </label>
              <label>
                Опис
                <input name="description" defaultValue={formatValue(editing.description)} />
              </label>
              <label>
                Пріоритет (1-5)
                <input
                  name="priority"
                  type="number"
                  min={1}
                  max={5}
                  defaultValue={formatValue(editing.priority)}
                />
              </label>
              <label>
                Тривалість (хв)
                <input
                  name="duration"
                  type="number"
                  min={1}
                  defaultValue={formatValue(editing.duration_minutes)}
                />
              </label>
              <label>
                Дедлайн
                <input name="deadline" type="datetime-local" defaultValue={formatDateTimeLocal(editing.deadline)} />
              </label>
              <label>
                Статус
                <select name="status" defaultValue={editing.status}>
                  <option value="pending">Pending</option>
                  <option value="in_progress">In progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </label>
            </div>
            <div className="cta-row">
              <button type="submit" className="button primary">
                Зберегти
              </button>
              <button type="button" className="button ghost" onClick={() => setEditing(null)}>
                Скасувати
              </button>
            </div>
          </form>
        </div>
      ) : null}

      {loading ? <p className="muted">Завантаження задач...</p> : null}
      {error ? <p className="muted">{error}</p> : null}
      {!loading && !error ? (
        <TaskList tasks={tasks} onEdit={setEditing} onDelete={handleDelete} />
      ) : null}
    </section>
  )
}

export default TasksPage
