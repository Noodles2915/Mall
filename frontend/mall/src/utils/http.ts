import type { ApiResponse } from '@/types/user-center'

type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

const API_BASE_URL =
  'http://localhost:8000' /* 生产环境请替换为实际后端地址，开发环境可使用代理或本地地址 */

function buildUrl(path: string): string {
  if (/^https?:\/\//.test(path)) {
    return path
  }
  return `${API_BASE_URL}${path}`
}

function extractErrorMessage(payload: unknown, status: number): string {
  if (!payload || typeof payload !== 'object') {
    return `请求失败(${status})`
  }

  const maybeApiResponse = payload as { message?: unknown }
  if (typeof maybeApiResponse.message === 'string' && maybeApiResponse.message.trim()) {
    return maybeApiResponse.message
  }

  const entries = Object.entries(payload as Record<string, unknown>)
  for (const [field, detail] of entries) {
    if (typeof detail === 'string' && detail.trim()) {
      return field === 'non_field_errors' ? detail : `${field}: ${detail}`
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0]
      if (typeof first === 'string' && first.trim()) {
        return field === 'non_field_errors' ? first : `${field}: ${first}`
      }
    }
  }

  return `请求失败(${status})`
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

  let payload: unknown = null
  try {
    payload = await response.json()
  } catch {
    // Keep null payload and provide an explicit error below.
  }

  const typedPayload = payload as ApiResponse<T> | null

  if (!response.ok) {
    const message = extractErrorMessage(payload, response.status)
    throw new Error(message)
  }

  // 兼容两种后端响应格式：统一包装({ code, data })与直接返回业务数据。
  if (
    typedPayload !== null &&
    typeof typedPayload === 'object' &&
    Object.prototype.hasOwnProperty.call(typedPayload, 'code')
  ) {
    if (typedPayload.code !== 0) {
      const message = extractErrorMessage(payload, response.status)
      throw new Error(message)
    }
    return typedPayload.data
  }

  return payload as T
}
