<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ProductDetail, ServiceMessage } from '@/types/product-center'
import {
  getProductDetail,
  getServiceMessages,
  createServiceMessage,
} from '@/services/product-center'
import { addCartItem } from '@/services/order-center'

const route = useRoute()
const router = useRouter()

const productId = computed(() => Number(route.params.id))

const loading = ref(false)
const error = ref('')
const product = ref<ProductDetail | null>(null)
const selectedImageIndex = ref(0)
const quantity = ref(1)

// Service Messages
const messagesLoading = ref(false)
const messagesError = ref('')
const serviceMessages = ref<ServiceMessage[]>([])
const newMessageContent = ref('')
const submittingMessage = ref(false)
const messageSubmitError = ref('')
const messageSubmitSuccess = ref('')

// Shopping cart
const addingToCart = ref(false)
const cartMessage = ref('')

// Receive accessToken and username from parent component context
const accessToken = ref(localStorage.getItem('mall_access_token') || '')
const username = ref(localStorage.getItem('mall_username') || '')

const isLoggedIn = computed(() => Boolean(accessToken.value))

const selectedImage = computed(
  () =>
    product.value?.images[selectedImageIndex.value] || {
      id: 0,
      image_url: '',
      sort: 0,
    },
)

async function loadProductDetail() {
  error.value = ''
  loading.value = true
  try {
    product.value = await getProductDetail(productId.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载商品详情失败'
  } finally {
    loading.value = false
  }
}

async function loadServiceMessages() {
  if (!isLoggedIn.value) {
    return
  }
  messagesError.value = ''
  messagesLoading.value = true
  try {
    serviceMessages.value = await getServiceMessages(productId.value, accessToken.value)
  } catch (err) {
    messagesError.value = err instanceof Error ? err.message : '加载客服留言失败'
  } finally {
    messagesLoading.value = false
  }
}

async function submitServiceMessage() {
  if (!newMessageContent.value.trim()) {
    messageSubmitError.value = '请输入留言内容'
    return
  }

  messageSubmitError.value = ''
  messageSubmitSuccess.value = ''
  submittingMessage.value = true

  try {
    const result = await createServiceMessage(
      productId.value,
      { content: newMessageContent.value },
      accessToken.value,
    )
    serviceMessages.value.push(result)
    newMessageContent.value = ''
    messageSubmitSuccess.value = '留言已发送，等待客服回复'
    setTimeout(() => {
      messageSubmitSuccess.value = ''
    }, 3000)
  } catch (err) {
    messageSubmitError.value = err instanceof Error ? err.message : '发送留言失败'
  } finally {
    submittingMessage.value = false
  }
}

async function handleAddToCart() {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }

  if (!product.value) return
  if (quantity.value < 1) return

  addingToCart.value = true
  cartMessage.value = ''
  try {
    await addCartItem(
      {
        product_id: product.value.id,
        quantity: quantity.value,
      },
      accessToken.value,
    )
    cartMessage.value = '已添加到购物车'
    setTimeout(() => {
      cartMessage.value = ''
    }, 2000)
    quantity.value = 1
  } catch (err) {
    cartMessage.value = err instanceof Error ? err.message : '添加购物车失败'
  } finally {
    addingToCart.value = false
  }
}

onMounted(() => {
  void loadProductDetail()
  void loadServiceMessages()
})
</script>

<template>
  <div class="product-detail">
    <!-- Error Banner -->
    <p v-if="error" class="error-banner">{{ error }}</p>

    <!-- Product Detail Content -->
    <div v-if="loading" class="spinner">加载商品详情中...</div>
    <template v-else-if="product">
      <section class="product-main">
        <!-- Image Gallery -->
        <div class="image-gallery">
          <div class="image-main" :style="{ backgroundImage: `url(${selectedImage.image_url})` }" />
          <div v-if="product.images.length > 1" class="image-thumbnails">
            <button
              v-for="(img, index) in product.images"
              :key="img.id"
              class="thumbnail"
              :class="{ active: index === selectedImageIndex }"
              :style="{ backgroundImage: `url(${img.image_url})` }"
              type="button"
              @click="selectedImageIndex = index"
            />
          </div>
        </div>

        <!-- Product Info -->
        <div class="product-info-section">
          <div class="header-section">
            <h1 class="product-name">{{ product.name }}</h1>
            <p class="product-subtitle">{{ product.subtitle }}</p>
            <div class="category-badge">分类: {{ product.category.name }}</div>
          </div>

          <div class="price-section">
            <div class="price-main">¥{{ product.price }}</div>
            <div class="price-meta">
              <span class="sales">已售 {{ product.sales }} 件</span>
              <span class="stock" :class="{ unavailable: product.stock === 0 }">
                {{ product.stock > 0 ? `库存 ${product.stock} 件` : '缺货' }}
              </span>
            </div>
          </div>

          <div class="description-section">
            <h3>商品描述</h3>
            <p class="description">{{ product.description }}</p>
          </div>

          <div v-if="Object.keys(product.specs).length > 0" class="specs-section">
            <h3>规格信息</h3>
            <div v-for="(values, key) in product.specs" :key="key" class="spec-item">
              <span class="spec-label">{{ key }}:</span>
              <span class="spec-values">{{ values.join(', ') }}</span>
            </div>
          </div>

          <div class="customer-hint">
            <p>{{ product.customer_service_hint }}</p>
          </div>

          <!-- Add to Cart Section -->
          <div class="add-to-cart-section">
            <div v-if="cartMessage" class="cart-message" :class="{ success: cartMessage.includes('已添加') }">
              {{ cartMessage }}
            </div>
            <div class="quantity-selector">
              <label>数量:</label>
              <button
                type="button"
                class="qty-btn"
                @click="quantity = Math.max(1, quantity - 1)"
                :disabled="addingToCart"
              >
                -
              </button>
              <input v-model.number="quantity" type="number" min="1" :disabled="addingToCart" />
              <button
                type="button"
                class="qty-btn"
                @click="quantity = Math.min(product.stock, quantity + 1)"
                :disabled="addingToCart || product.stock === 0"
              >
                +
              </button>
            </div>
            <button
              class="add-btn"
              type="button"
              :disabled="addingToCart || product.stock === 0"
              @click="handleAddToCart"
            >
              {{ addingToCart ? '添加中...' : product.stock === 0 ? '缺货' : '加入购物车' }}
            </button>
          </div>
        </div>
      </section>

      <!-- Service Messages Section -->
      <section class="service-section">
        <h2>在线客服</h2>

        <div v-if="!isLoggedIn" class="login-prompt">
          <p>请先登录以联系客服</p>
          <button
            class="login-btn"
            type="button"
            @click="() => router.push({ path: '/login', query: { redirect: $route.fullPath } })"
          >
            返回登录
          </button>
        </div>

        <template v-else>
          <!-- Message Form -->
          <div class="message-form">
            <h3>发送留言</h3>
            <p v-if="messageSubmitError" class="form-error">{{ messageSubmitError }}</p>
            <p v-if="messageSubmitSuccess" class="form-success">{{ messageSubmitSuccess }}</p>
            <textarea
              v-model="newMessageContent"
              placeholder="请输入您的疑问或建议..."
              class="message-input"
              rows="4"
            />
            <button
              class="submit-btn"
              type="button"
              :disabled="submittingMessage"
              @click="submitServiceMessage"
            >
              {{ submittingMessage ? '发送中...' : '发送留言' }}
            </button>
          </div>

          <!-- Messages Display -->
          <div class="messages-list">
            <h3>留言列表</h3>
            <p v-if="messagesError" class="messages-error">{{ messagesError }}</p>
            <div v-if="messagesLoading" class="spinner">加载留言中...</div>
            <div v-else-if="serviceMessages.length > 0" class="messages">
              <div v-for="msg in serviceMessages" :key="msg.id" class="message-item">
                <div class="message-header">
                  <span class="message-user">{{ msg.username }}</span>
                  <span class="message-time">{{ new Date(msg.created_at).toLocaleDateString('zh-CN') }}</span>
                </div>
                <div class="message-content">{{ msg.content }}</div>
                <div v-if="msg.reply" class="message-reply">
                  <div class="reply-label">客服回复:</div>
                  <div class="reply-content">{{ msg.reply }}</div>
                </div>
              </div>
            </div>
            <div v-else class="no-messages">暂无留言</div>
          </div>
        </template>
      </section>
    </template>
    <div v-else class="no-data">商品不存在</div>
  </div>
</template>

<style scoped>
.product-detail {
  padding: 1rem 0;
}

.error-banner {
  margin: 0 auto;
  max-width: 100%;
  padding: 0.75rem 1.5rem;
  background: #ffe8e3;
  color: #8e3026;
  text-align: center;
}

/* Product Main Section */
.product-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 0.8rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* Image Gallery */
.image-gallery {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.image-main {
  width: 100%;
  aspect-ratio: 1;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #f5f5f5;
  border-radius: 0.8rem;
}

.image-thumbnails {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.thumbnail {
  aspect-ratio: 1;
  background-size: cover;
  background-position: center;
  background-color: #f5f5f5;
  border: 2px solid #d4e6f0;
  border-radius: 0.6rem;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.thumbnail:hover {
  border-color: #1f9f78;
}

.thumbnail.active {
  border-color: #1f9f78;
}

/* Product Info Section */
.product-info-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.product-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1b2a2f;
}

.product-subtitle {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #666;
}

.category-badge {
  display: inline-block;
  background: #f0f0f0;
  padding: 0.4rem 0.8rem;
  border-radius: 0.4rem;
  font-size: 0.85rem;
  color: #666;
}

/* Price Section */
.price-section {
  padding: 1rem;
  background: #fffef8;
  border-radius: 0.6rem;
}

.price-main {
  font-size: 1.8rem;
  font-weight: 700;
  color: #ff5550;
  margin-bottom: 0.5rem;
}

.price-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #999;
}

.stock.unavailable {
  color: #ff5550;
  font-weight: 600;
}

/* Description Section */
.description-section h3,
.specs-section h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b2a2f;
}

.description {
  margin: 0;
  line-height: 1.6;
  color: #666;
}

/* Specs Section */
.specs-section {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 0.6rem;
}

.spec-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.spec-item:last-child {
  margin-bottom: 0;
}

.spec-label {
  font-weight: 600;
  color: #1b2a2f;
  min-width: 100px;
}

.spec-values {
  color: #666;
}

/* Customer Hint */
.customer-hint {
  padding: 0.75rem 1rem;
  background: #f0f8ff;
  border-left: 3px solid #1f9f78;
  border-radius: 0.4rem;
}

.customer-hint p {
  margin: 0;
  font-size: 0.9rem;
  color: #1d5166;
}

/* Service Section */
.service-section {
  background: white;
  padding: 2rem;
  border-radius: 0.8rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.service-section h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #103f50;
}

.login-prompt {
  padding: 2rem;
  text-align: center;
  background: #f0f8ff;
  border-radius: 0.6rem;
}

.login-prompt p {
  margin: 0 0 1rem 0;
  color: #1d5166;
}

.login-btn {
  padding: 0.6rem 1.5rem;
  background: #1f9f78;
  color: white;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.login-btn:hover {
  background: #16825f;
}

/* Message Form */
.message-form {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 0.6rem;
}

.message-form h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b2a2f;
}

.form-error {
  margin: 0 0 1rem 0;
  padding: 0.75rem 1rem;
  background: #ffe8e3;
  color: #8e3026;
  border-radius: 0.4rem;
  font-size: 0.9rem;
}

.form-success {
  margin: 0 0 1rem 0;
  padding: 0.75rem 1rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 0.4rem;
  font-size: 0.9rem;
}

.message-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  margin-bottom: 1rem;
}

.submit-btn {
  padding: 0.6rem 1.5rem;
  background: #1f9f78;
  color: white;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: #16825f;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Messages List */
.messages-list h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b2a2f;
}

.messages-error {
  padding: 0.75rem 1rem;
  background: #ffe8e3;
  color: #8e3026;
  border-radius: 0.4rem;
  font-size: 0.9rem;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 0.6rem;
  border-left: 3px solid #d4e6f0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.message-user {
  font-weight: 600;
  color: #1b2a2f;
}

.message-time {
  color: #999;
}

.message-content {
  margin-bottom: 0.5rem;
  color: #666;
  line-height: 1.5;
}

.message-reply {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #e8f5e9;
  border-radius: 0.4rem;
}

.reply-label {
  font-weight: 600;
  color: #2e7d32;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.reply-content {
  color: #2e7d32;
  line-height: 1.5;
}

.no-messages {
  padding: 1rem;
  text-align: center;
  color: #999;
}

.spinner,
.no-data {
  padding: 2rem 1rem;
  text-align: center;
  color: #999;
}

.spinner {
  font-weight: 600;
}

/* Add to Cart Section */
.add-to-cart-section {
  padding: 1rem;
  background: #f0fef8;
  border-radius: 0.6rem;
  border: 2px solid #d4e6f0;
}

.cart-message {
  padding: 0.6rem;
  margin-bottom: 0.75rem;
  text-align: center;
  border-radius: 0.4rem;
  font-size: 0.9rem;
  background: #ffe8e3;
  color: #8e3026;
}

.cart-message.success {
  background: #d4edda;
  color: #155724;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.quantity-selector label {
  font-weight: 600;
  color: #1d5166;
  min-width: 40px;
}

.qty-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #b6cfdc;
  background: white;
  border-radius: 0.4rem;
  cursor: pointer;
  font-weight: 600;
  color: #1d5166;
  transition: all 0.2s;
}

.qty-btn:hover:not(:disabled) {
  background: #1f9f78;
  color: white;
  border-color: #1f9f78;
}

.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-selector input {
  width: 60px;
  height: 32px;
  padding: 0.4rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.4rem;
  text-align: center;
  font-weight: 600;
}

.quantity-selector input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.add-btn {
  width: 100%;
  padding: 0.75rem;
  background: #1f9f78;
  color: white;
  border: none;
  border-radius: 0.6rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn:hover:not(:disabled) {
  background: #0c6f57;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(31, 159, 120, 0.3);
}

.add-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 1024px) {
  .product-main {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .product-main {
    padding: 1.5rem;
  }

  .image-thumbnails {
    grid-template-columns: repeat(3, 1fr);
  }

  .service-section {
    padding: 1.5rem;
  }
}
</style>
