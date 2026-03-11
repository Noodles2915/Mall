import type {
  ShoppingCart,
  CartItem,
  Order,
  OrderListItem,
  OrderCreatePayload,
} from '@/types/product-center'
import { request } from '@/utils/http'

// 购物车相关接口
export function getCart(accessToken: string) {
  return request<ShoppingCart>('/api/orders/cart/', 'GET', undefined, accessToken)
}

export function addCartItem(payload: { product_id: number; quantity: number }, accessToken: string) {
  return request<ShoppingCart>('/api/orders/cart/add/', 'POST', payload, accessToken)
}

export function updateCartItem(itemId: number, payload: { quantity: number }, accessToken: string) {
  return request<ShoppingCart>(
    `/api/orders/cart/items/${itemId}/`,
    'PUT',
    payload,
    accessToken,
  )
}

export function removeCartItem(itemId: number, accessToken: string) {
  return request<ShoppingCart>(
    `/api/orders/cart/items/${itemId}/`,
    'DELETE',
    undefined,
    accessToken,
  )
}

export function clearCart(accessToken: string) {
  return request<ShoppingCart>('/api/orders/cart/clear/', 'DELETE', undefined, accessToken)
}

// 订单相关接口
export function getOrders(accessToken: string) {
  return request<OrderListItem[]>('/api/orders/orders/', 'GET', undefined, accessToken)
}

export function getOrderDetail(orderId: number, accessToken: string) {
  return request<Order>(`/api/orders/orders/${orderId}/`, 'GET', undefined, accessToken)
}

export function createOrder(payload: OrderCreatePayload, accessToken: string) {
  return request<Order>('/api/orders/orders/create/', 'POST', payload, accessToken)
}

export function payOrder(orderId: number, accessToken: string) {
  return request<Order>(`/api/orders/orders/${orderId}/pay/`, 'POST', {}, accessToken)
}

export function cancelOrder(orderId: number, accessToken: string) {
  return request<Order>(`/api/orders/orders/${orderId}/cancel/`, 'POST', {}, accessToken)
}

export function receiveOrder(orderId: number, accessToken: string) {
  return request<Order>(`/api/orders/orders/${orderId}/receive/`, 'POST', {}, accessToken)
}

export function getAdminOrders(accessToken: string, status?: string) {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return request<OrderListItem[]>(`/api/orders/admin/orders/${query}`, 'GET', undefined, accessToken)
}

export function shipAdminOrder(orderId: number, accessToken: string) {
  return request<Order>(`/api/orders/admin/orders/${orderId}/ship/`, 'POST', {}, accessToken)
}
