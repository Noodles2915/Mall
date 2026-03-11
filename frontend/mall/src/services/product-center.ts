import type {
  AdminServiceMessage,
  AdminServiceMessageReplyPayload,
  Category,
  HomeData,
  MerchantProductItem,
  MerchantProductPayload,
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

export function getMerchantProducts(accessToken: string) {
  return request<MerchantProductItem[]>(
    '/api/products/merchant/products/',
    'GET',
    undefined,
    accessToken,
  )
}

export function createMerchantProduct(payload: MerchantProductPayload, accessToken: string) {
  return request<MerchantProductItem>(
    '/api/products/merchant/products/',
    'POST',
    payload,
    accessToken,
  )
}

export function updateMerchantProduct(
  productId: number,
  payload: MerchantProductPayload,
  accessToken: string,
) {
  return request<MerchantProductItem>(
    `/api/products/merchant/products/${productId}/`,
    'PUT',
    payload,
    accessToken,
  )
}

export function deleteMerchantProduct(productId: number, accessToken: string) {
  return request<null>(`/api/products/merchant/products/${productId}/`, 'DELETE', undefined, accessToken)
}

export function publishMerchantProduct(productId: number, accessToken: string) {
  return request<MerchantProductItem>(
    `/api/products/merchant/products/${productId}/publish/`,
    'POST',
    {},
    accessToken,
  )
}

export function unpublishMerchantProduct(productId: number, accessToken: string) {
  return request<MerchantProductItem>(
    `/api/products/merchant/products/${productId}/unpublish/`,
    'POST',
    {},
    accessToken,
  )
}

export interface AdminServiceMessageParams {
  product_id?: number
  has_reply?: boolean
}

export function getAdminServiceMessages(
  accessToken: string,
  params?: AdminServiceMessageParams,
) {
  const searchParams = new URLSearchParams()
  if (params?.product_id) {
    searchParams.set('product_id', String(params.product_id))
  }
  if (params?.has_reply !== undefined) {
    searchParams.set('has_reply', params.has_reply ? '1' : '0')
  }
  const query = searchParams.toString()
  const path = query
    ? `/api/products/admin/service-messages/?${query}`
    : '/api/products/admin/service-messages/'
  return request<AdminServiceMessage[]>(path, 'GET', undefined, accessToken)
}

export function replyServiceMessage(
  messageId: number,
  payload: AdminServiceMessageReplyPayload,
  accessToken: string,
) {
  return request<AdminServiceMessage>(
    `/api/products/service-messages/${messageId}/reply/`,
    'POST',
    payload,
    accessToken,
  )
}
