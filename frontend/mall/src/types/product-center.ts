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

export interface ServiceMessageInput {
  content: string
}
