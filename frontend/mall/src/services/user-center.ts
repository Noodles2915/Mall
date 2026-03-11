import type {
  AddressForm,
  AddressItem,
  AuthPayload,
  QualificationApplicationItem,
  QualificationApplicationType,
  UserProfile,
} from '@/types/user-center'
import { request } from '@/utils/http'

export function login(payload: { username: string; password: string }) {
  return request<AuthPayload>('/api/auth/login/', 'POST', payload)
}

export function register(payload: { username: string; email: string; password: string }) {
  return request<AuthPayload>('/api/auth/register/', 'POST', payload)
}

export function getMe(accessToken: string) {
  return request<UserProfile>('/api/auth/me/', 'GET', undefined, accessToken)
}

export function updateMe(
  payload: { username: string; email: string; avatar: string },
  accessToken: string,
) {
  return request<UserProfile>('/api/auth/me/', 'PUT', payload, accessToken)
}

export function getAddresses(accessToken: string) {
  return request<AddressItem[]>('/api/auth/addresses/', 'GET', undefined, accessToken)
}

export function createAddress(payload: AddressForm, accessToken: string) {
  return request<AddressItem>('/api/auth/addresses/', 'POST', payload, accessToken)
}

export function updateAddress(id: number, payload: AddressForm, accessToken: string) {
  return request<AddressItem>(`/api/auth/addresses/${id}/`, 'PUT', payload, accessToken)
}

export function deleteAddress(id: number, accessToken: string) {
  return request<null>(`/api/auth/addresses/${id}/`, 'DELETE', undefined, accessToken)
}

export function setDefaultAddress(id: number, accessToken: string) {
  return request<AddressItem>(`/api/auth/addresses/${id}/default/`, 'POST', {}, accessToken)
}

export function getQualificationApplications(accessToken: string) {
  return request<QualificationApplicationItem[]>(
    '/api/auth/qualification-applications/',
    'GET',
    undefined,
    accessToken,
  )
}

export function submitQualificationApplication(
  payload: { application_type: QualificationApplicationType; reason: string },
  accessToken: string,
) {
  return request<QualificationApplicationItem>(
    '/api/auth/qualification-applications/',
    'POST',
    payload,
    accessToken,
  )
}
