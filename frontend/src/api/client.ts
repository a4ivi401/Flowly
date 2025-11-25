const envApiBase = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '');
const API_BASE_URL = envApiBase || '/api';
const buildUrl = (path: string) => `${API_BASE_URL}${path}`;

export interface Task {
  id?: number;
  title: string;
  description?: string | null;
  priority: 1 | 2 | 3 | 4 | 5;
  duration_minutes?: number | null;
  deadline?: string | null;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  created_at?: string;
  updated_at?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority: 1 | 2 | 3 | 4 | 5;
  duration_minutes?: number;
  deadline?: string;
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: 1 | 2 | 3 | 4 | 5;
  duration_minutes?: number;
  deadline?: string;
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
}

interface GetTasksParams {
  skip?: number;
  limit?: number;
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority?: 1 | 2 | 3 | 4 | 5;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    console.error(`API Error [${response.status}]:`, error);
    throw new ApiError(response.status, error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const apiClient = {
  /**
   * Отримати список задач з фільтрами та пагінацією
   */
  async getTasks(params: GetTasksParams = {}): Promise<Task[]> {
    const queryParams = new URLSearchParams();
    
    if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params.status) queryParams.append('status', params.status);
    if (params.priority) queryParams.append('priority', params.priority.toString());
    
    const url = buildUrl(`/tasks/?${queryParams.toString()}`);
    
    try {
      const response = await fetch(url);
      return handleResponse<Task[]>(response);
    } catch (error) {
      console.error('getTasks error:', error);
      throw error;
    }
  },

  /**
   * Створити нову задачу
   */
  async createTask(task: TaskCreate): Promise<Task> {
    try {
      const response = await fetch(buildUrl('/tasks/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(task),
      });
      return handleResponse<Task>(response);
    } catch (error) {
      console.error('createTask error:', error);
      throw error;
    }
  },

  /**
   * Оновити задачу (часткове оновлення)
   */
  async updateTask(id: number, task: TaskUpdate): Promise<Task> {
    try {
      const response = await fetch(buildUrl(`/tasks/${id}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(task),
      });
      return handleResponse<Task>(response);
    } catch (error) {
      console.error('updateTask error:', error);
      throw error;
    }
  },

  /**
   * Видалити задачу
   */
  async deleteTask(id: number): Promise<{ ok: boolean }> {
    try {
      const response = await fetch(buildUrl(`/tasks/${id}`), {
        method: 'DELETE',
      });
      return handleResponse<{ ok: boolean }>(response);
    } catch (error) {
      console.error('deleteTask error:', error);
      throw error;
    }
  },

  /**
   * Отримати задачі на сьогодні (статус pending або in_progress)
   */
  async getTodayTasks(): Promise<Task[]> {
    try {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      // Отримуємо задачі зі статусом pending та in_progress
      const pendingTasks = await this.getTasks({ status: 'pending' });
      const inProgressTasks = await this.getTasks({ status: 'in_progress' });
      
      // Обʼєднуємо та фільтруємо задачі з дедлайном на сьогодні
      const allTasks = [...pendingTasks, ...inProgressTasks];
      
      return allTasks.filter(task => {
        if (!task.deadline) return true; // Задачі без дедлайну теж включаємо
        const deadline = new Date(task.deadline);
        return deadline >= today && deadline < tomorrow;
      });
    } catch (error) {
      console.error('getTodayTasks error:', error);
      throw error;
    }
  },

  /**
   * Запланувати задачі на сьогодні через Planning Engine (Gemini AI)
   */
  async planToday(params?: {
    timezone?: string;
    workday_hours?: number;
    long_break_minutes?: number;
    short_break_minutes?: number;
  }): Promise<{
    generated_at: string;
    timezone: string;
    tasks: Array<{
      task_id: number;
      priority_rank: number;
      planned_start: string;
      planned_end: string;
      duration_minutes: number;
      note: string | null;
      task: Task;
    }>;
  }> {
    try {
      const response = await fetch(buildUrl('/plan/today'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params || {}),
      });
      return handleResponse(response);
    } catch (error) {
      console.error('planToday error:', error);
      throw error;
    }
  },

  /**
   * Отримати поточний план на сьогодні
   */
  async getTodayPlan(): Promise<{
    generated_at: string;
    timezone: string;
    tasks: Array<{
      task_id: number;
      priority_rank: number;
      planned_start: string;
      planned_end: string;
      duration_minutes: number;
      note: string | null;
      task: Task;
    }>;
  } | null> {
    try {
      const response = await fetch(buildUrl('/plan/today/optimized'));
      if (response.status === 404) {
        return null;
      }
      return handleResponse(response);
    } catch (error) {
      console.error('getTodayPlan error:', error);
      throw error;
    }
  },

  /**
   * Отримати задачу за ID
   */
  async getTask(id: number): Promise<Task> {
    try {
      const response = await fetch(buildUrl(`/tasks/${id}`));
      return handleResponse<Task>(response);
    } catch (error) {
      console.error('getTask error:', error);
      throw error;
    }
  },

  /**
   * Отримати прострочені задачі
   */
  async getOverdueTasks(skip = 0, limit = 100): Promise<Task[]> {
    try {
      const response = await fetch(
        buildUrl(`/tasks/status/overdue?skip=${skip}&limit=${limit}`)
      );
      return handleResponse<Task[]>(response);
    } catch (error) {
      console.error('getOverdueTasks error:', error);
      throw error;
    }
  },

  /**
   * Отримати задачі за пріоритетом
   */
  async getTasksByPriority(
    priority: 1 | 2 | 3 | 4 | 5,
    skip = 0,
    limit = 100
  ): Promise<Task[]> {
    try {
      const response = await fetch(
        buildUrl(`/tasks/priority/${priority}?skip=${skip}&limit=${limit}`)
      );
      return handleResponse<Task[]>(response);
    } catch (error) {
      console.error('getTasksByPriority error:', error);
      throw error;
    }
  },

  /**
   * Перевірити здоровʼя API
   */
  async healthCheck(): Promise<{
    status: string;
    database: string;
    mysql_version?: string;
    message: string;
  }> {
    try {
      const response = await fetch(buildUrl('/health'));
      return handleResponse(response);
    } catch (error) {
      console.error('healthCheck error:', error);
      throw error;
    }
  },
};
