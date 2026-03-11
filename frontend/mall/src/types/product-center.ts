export interface Category {
  id: number
  name: string
  parent: number | null
  sort: number
}

export interface ProductBanner {
  id: number
  title: string
  image_url: string
  link: string
  sort: number
}

export interface ProductBase {
  id: number
  name: string
  subtitle: string
  cover_url: string
  price: string
  stock: number
  sales: number
  is_hot: boolean
  category: number
  category_name: string
  merchant_id?: number | null
}

export interface HomeData {
  banners: ProductBanner[]
  hot_products: ProductBase[]
}

export interface ProductSpec {
  [key: string]: string[]
}

export interface ProductImage {
  id: number
  image_url: string
  sort: number
}

export interface ProductDetail extends Omit<ProductBase, 'category'> {
  description: string
  specs: ProductSpec
  customer_service_hint: string
  category: Category
  images: ProductImage[]
  customer_service_entry: string
}

export interface ServiceMessage {
  id: number
  product: number
  username: string
  content: string
  reply: string
  created_at: string
}

export interface AdminServiceMessage extends ServiceMessage {
  product_name: string
  user_id: number
}

export interface AdminServiceMessageReplyPayload {
  reply: string
}

export interface ServiceMessageInput {
  content: string
}

export interface CartItem {
  id: number
  product: number
  product_name: string
  product_price: string
  product_cover_url: string
  quantity: number
  subtotal: string
}

export interface ShoppingCart {
  id: number
  items: CartItem[]
  total_price: string
  total_quantity: number
  updated_at: string
}

export interface OrderItem {
  id: number
  product_name: string
  product_price: string
  quantity: number
  subtotal: string
}

export interface Order {
  id: number
  order_number: string
  status: string
  status_display: string
  address_name: string
  address_phone: string
  address_province: string
  address_city: string
  address_district: string
  address_detail: string
  remarks: string
  total_price: string
  payment_method: string
  items: OrderItem[]
  created_at: string
  paid_at: string | null
  shipped_at: string | null
  received_at: string | null
  cancelled_at: string | null
}

export interface OrderListItem {
  id: number
  order_number: string
  status: string
  status_display: string
  total_price: string
  items_count: number
  created_at: string
}

export interface OrderCreatePayload {
  address_id: number
  remarks: string
  payment_method: string
}

export interface MerchantProductPayload {
  category: number
  name: string
  subtitle: string
  cover_url: string
  price: string
  stock: number
  is_hot: boolean
  is_active: boolean
  description: string
  specs: Record<string, string[]>
  customer_service_hint: string
}

export interface MerchantProductItem extends ProductBase {
  is_active: boolean
  description: string
  specs: Record<string, string[]>
  customer_service_hint: string
  created_at: string
  updated_at: string
}
