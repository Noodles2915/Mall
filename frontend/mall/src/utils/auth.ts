const ACCESS_TOKEN_KEY = 'mall_access_token'
const REFRESH_TOKEN_KEY = 'mall_refresh_token'
const USERNAME_KEY = 'mall_username'

export const AUTH_CHANGED_EVENT = 'mall-auth-changed'

export interface AuthState {
  accessToken: string
  refreshToken: string
  username: string
}

export function getAuthState(): AuthState {
  return {
    accessToken: localStorage.getItem(ACCESS_TOKEN_KEY) || '',
    refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY) || '',
    username: localStorage.getItem(USERNAME_KEY) || '',
  }
}

export function setAuthSession(accessToken: string, refreshToken: string, username: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  localStorage.setItem(USERNAME_KEY, username)
  window.dispatchEvent(new CustomEvent(AUTH_CHANGED_EVENT))
}

export function clearAuthSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
  window.dispatchEvent(new CustomEvent(AUTH_CHANGED_EVENT))
}

export function onAuthChanged(listener: () => void): () => void {
  const handleStorage = (event: StorageEvent) => {
    if (!event.key || event.key.startsWith('mall_')) {
      listener()
    }
  }

  window.addEventListener(AUTH_CHANGED_EVENT, listener)
  window.addEventListener('storage', handleStorage)

  return () => {
    window.removeEventListener(AUTH_CHANGED_EVENT, listener)
    window.removeEventListener('storage', handleStorage)
  }
}