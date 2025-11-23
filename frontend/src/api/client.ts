const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

type RequestOptions = RequestInit & {
  path: string
}

export async function apiRequest<T>({ path, ...init }: RequestOptions): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
    ...init,
  })

  if (!response.ok) {
    const message = await safeParseError(response)
    throw new Error(message)
  }

  return response.json() as Promise<T>
}

async function safeParseError(response: Response) {
  try {
    const data = await response.json()
    return data.message || response.statusText
  } catch {
    return response.statusText
  }
}

export { API_BASE_URL }
