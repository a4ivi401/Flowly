import { useMemo, useState } from 'react'
import TaskForm from '../components/TaskForm'
import TaskList, { type Task } from '../components/TaskList'

const initialTasks: Task[] = [
  { id: 1, title: 'Draft MVP scope for AI Time Manager', status: 'in-progress' },
  { id: 2, title: "Outline today's schedule", status: 'todo' },
  { id: 3, title: 'Sync with backend on API contract', status: 'todo' },
]

const TasksPage = () => {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)

  const stats = useMemo(() => {
    const completed = tasks.filter((task) => task.status === 'done').length
    return { total: tasks.length, completed }
  }, [tasks])

  const handleAdd = (title: string) => {
    const newTask: Task = {
      id: Date.now(),
      title,
      status: 'todo',
    }
    setTasks((current) => [newTask, ...current])
  }

  const handleToggle = (id: number) => {
    setTasks((current) =>
      current.map((task) =>
        task.id === id
          ? { ...task, status: task.status === 'done' ? 'todo' : 'done' }
          : task,
      ),
    )
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
      <TaskList tasks={tasks} onToggle={handleToggle} />
    </section>
  )
}

export default TasksPage
