import type {
  Category,
  HomeData,
  ProductBase,
  ProductDetail,
  ServiceMessage,
  ServiceMessageInput,
} from '@/types/product-center'
import { request } from '@/utils/http'

export function getHomeData() {
  return request<HomeData>('/api/products/home/', 'GET')
}

export function getCategories() {
  return request<Category[]>('/api/products/categories/', 'GET')
}

export interface ProductListParams {
  keyword?: string
  category?: number
  is_hot?: boolean
}

export function getProducts(params?: ProductListParams) {
  const searchParams = new URLSearchParams()
  if (params?.keyword) {
    searchParams.set('keyword', params.keyword)
  }
  if (params?.category) {
    searchParams.set('category', String(params.category))
  }
  if (params?.is_hot) {
    searchParams.set('is_hot', 'true')
  }
  const query = searchParams.toString()
  const path = query ? `/api/products/?${query}` : '/api/products/'
  return request<ProductBase[]>(path, 'GET')
}

export function getProductDetail(id: number) {
  return request<ProductDetail>(`/api/products/${id}/`, 'GET')
}

export function getServiceMessages(productId: number, accessToken: string) {
  return request<ServiceMessage[]>(
    `/api/products/${productId}/service-messages/`,
    'GET',
    undefined,
    accessToken,
  )
}

export function createServiceMessage(
  productId: number,
  payload: ServiceMessageInput,
  accessToken: string,
) {
  return request<ServiceMessage>(
    `/api/products/${productId}/service-messages/`,
    'POST',
    payload,
    accessToken,
  )
}
