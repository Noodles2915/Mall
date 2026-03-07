import type { ApiResponse } from '@/types/user-center'

type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

const API_BASE_URL =
  (globalThis as { __MALL_API_BASE_URL__?: string }).__MALL_API_BASE_URL__?.trim() || ''

function buildUrl(path: string): string {
  if (/^https?:\/\//.test(path)) {
    return path
  }
  return `${API_BASE_URL}${path}`
}

export async function request<T>(
  path: string,
  method: Method,
  body?: unknown,
  accessToken?: string,
) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`
  }

  const response = await fetch(buildUrl(path), {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  let payload: ApiResponse<T> | null = null
  try {
    payload = (await response.json()) as ApiResponse<T>
  } catch {
    // Keep null payload and provide an explicit error below.
  }

  if (!response.ok || payload === null || payload.code !== 0) {
    const message = payload?.message || `请求失败(${response.status})`
    throw new Error(message)
  }

  return payload.data
}
