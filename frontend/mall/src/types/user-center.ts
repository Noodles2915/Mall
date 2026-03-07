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
