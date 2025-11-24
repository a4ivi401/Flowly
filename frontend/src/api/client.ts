const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const API_BASE_URL = rawBaseUrl.replace(/\/$/, '')

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'

export type Task = {
  id: number
  title: string
  description: string | null
  priority: number | null
  duration_minutes: number | null
  deadline: string | null
  status: TaskStatus
  created_at?: string
  updated_at?: string
}

type RequestOptions = RequestInit & { skipJson?: boolean }

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`API error ${response.status}: ${errorText}`)
      throw new Error(`API request failed with status ${response.status}`)
    }

    if (options.skipJson || response.status === 204) {
      return undefined as T
    }

    return (await response.json()) as T
  } catch (error) {
    console.error('API request failed', error)
    throw error
  }
}

export async function getTasks(params?: {
  skip?: number
  limit?: number
  status?: TaskStatus
  priority?: number
}): Promise<Task[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', String(params.skip))
  if (params?.limit) searchParams.set('limit', String(params.limit))
  if (params?.status) searchParams.set('status', params.status)
  if (params?.priority) searchParams.set('priority', String(params.priority))

  const query = searchParams.toString()
  const url = query ? `/tasks/?${query}` : '/tasks/'

  return request<Task[]>(url)
}

export async function createTask(task: Partial<Task> & { title: string }): Promise<Task> {
  return request<Task>('/tasks/', {
    method: 'POST',
    body: JSON.stringify(task),
  })
}

export async function updateTask(
  id: number,
  task: Partial<Omit<Task, 'id'>>,
): Promise<Task> {
  return request<Task>(`/tasks/${id}`, {
    method: 'PUT',
    body: JSON.stringify(task),
  })
}

export async function deleteTask(id: number): Promise<void> {
  await request(`/tasks/${id}`, { method: 'DELETE', skipJson: true })
}

export async function getTasksByPriority(priority: number, params?: { skip?: number; limit?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', String(params.skip))
  if (params?.limit) searchParams.set('limit', String(params.limit))
  const query = searchParams.toString()
  const url = query
    ? `/tasks/priority/${priority}?${query}`
    : `/tasks/priority/${priority}`
  return request<Task[]>(url)
}

export async function getOverdueTasks(params?: { skip?: number; limit?: number }): Promise<Task[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', String(params.skip))
  if (params?.limit) searchParams.set('limit', String(params.limit))
  const query = searchParams.toString()
  const url = query ? `/tasks/status/overdue?${query}` : '/tasks/status/overdue'
  return request<Task[]>(url)
}

// Convenience aliases for legacy calls
export async function getTodayTasks(): Promise<Task[]> {
  return getTasks({ status: 'in_progress' })
}

export async function planToday(): Promise<{ message: string } | undefined> {
  console.warn('planToday endpoint is not provided by the backend; implement when available.')
  return undefined
}
