import { useState, type FormEvent } from 'react'

type TaskFormProps = {
  onAdd?: (title: string) => void
}

const TaskForm = ({ onAdd }: TaskFormProps) => {
  const [title, setTitle] = useState('')

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) {
      return
    }

    onAdd?.(trimmed)
    setTitle('')
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <div className="input-group">
        <label htmlFor="task-title">Quick add</label>
        <input
          id="task-title"
          name="title"
          type="text"
          placeholder="Capture a task and keep momentum..."
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
      </div>
      <button type="submit" className="button primary">
        Add task
      </button>
    </form>
  )
}

export default TaskForm
