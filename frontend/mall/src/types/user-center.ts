export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface UserProfile {
  id: number
  username: string
  email: string
  avatar: string
  role?: 'normal' | 'admin' | 'merchant' | 'staff'
  role_display?: string
}

export interface AuthPayload {
  access: string
  refresh: string
  user: UserProfile
}

export interface AddressItem {
  id: number
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  is_default: boolean
}

export interface AddressForm {
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  is_default: boolean
}

export type QualificationApplicationType = 'merchant' | 'staff'
export type QualificationApplicationStatus = 'pending' | 'approved' | 'rejected'

export interface QualificationApplicationItem {
  id: number
  application_type: QualificationApplicationType
  application_type_display: string
  reason: string
  status: QualificationApplicationStatus
  status_display: string
  review_note: string
  created_at: string
  reviewed_at: string | null
}
