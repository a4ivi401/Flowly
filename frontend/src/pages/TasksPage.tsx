import { useEffect, useMemo, useState } from 'react'
import { createTask, getTasks, updateTask, type Task } from '../api/client'
import TaskForm from '../components/TaskForm'
import TaskList from '../components/TaskList'

const TasksPage = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  const handleAdd = async (title: string) => {
    try {
      const created = await createTask({ title, status: 'pending' })
      setTasks((current) => [created, ...current])
    } catch (err) {
      console.error('Не вдалося створити задачу', err)
      const fallback: Task = {
        id: Date.now(),
        title,
        status: 'pending',
        description: null,
        priority: null,
        duration_minutes: null,
        deadline: null,
      }
      setTasks((current) => [fallback, ...current])
    }
  }

  const handleToggle = async (id: number) => {
    const existing = tasks.find((task) => task.id === id)
    if (!existing) return

    const nextStatus = existing.status === 'completed' ? 'pending' : 'completed'

    try {
      const updated = await updateTask(id, { status: nextStatus })
      setTasks((current) => current.map((task) => (task.id === id ? updated : task)))
    } catch (err) {
      console.error('Не вдалося оновити задачу', err)
      setTasks((current) =>
        current.map((task) => (task.id === id ? { ...task, status: nextStatus } : task)),
      )
    }
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

      <TaskForm onAdd={handleAdd} />
      {loading ? (
        <p className="muted">Завантаження задач...</p>
      ) : error ? (
        <p className="muted">{error}</p>
      ) : (
        <TaskList tasks={tasks} onToggle={handleToggle} />
      )}
    </section>
  )
}

export default TasksPage
