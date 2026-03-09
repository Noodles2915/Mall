<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { ShoppingCart } from '@/types/product-center'
import { getCart, updateCartItem, removeCartItem, clearCart } from '@/services/order-center'

const router = useRouter()
const accessToken = ref(localStorage.getItem('mall_access_token') || '')

const cart = ref<ShoppingCart | null>(null)
const loading = ref(false)
const error = ref('')
const operatingItemId = ref<number | null>(null)

const isLoggedIn = computed(() => Boolean(accessToken.value))

const totalPrice = computed(() => {
  if (!cart.value) return '0.00'
  return (
    cart.value.items.reduce((sum, item) => {
      return sum + parseFloat(item.subtotal)
    }, 0)
  ).toFixed(2)
})

async function loadCart() {
  if (!isLoggedIn.value) {
    error.value = '请先登录'
    return
  }

  loading.value = true
  error.value = ''
  try {
    cart.value = await getCart(accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载购物车失败'
  } finally {
    loading.value = false
  }
}

async function updateQuantity(itemId: number, newQuantity: number) {
  if (newQuantity < 1) return

  operatingItemId.value = itemId
  try {
    cart.value = await updateCartItem(itemId, { quantity: newQuantity }, accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新数量失败'
  } finally {
    operatingItemId.value = null
  }
}

async function removeItem(itemId: number) {
  if (!confirm('确定要删除这个商品吗？')) return

  operatingItemId.value = itemId
  try {
    cart.value = await removeCartItem(itemId, accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
  } finally {
    operatingItemId.value = null
  }
}

async function handleClearCart() {
  if (!confirm('确定要清空购物车吗？')) return

  loading.value = true
  try {
    cart.value = await clearCart(accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '清空失败'
  } finally {
    loading.value = false
  }
}

function goToCheckout() {
  if (!cart.value || cart.value.items.length === 0) {
    error.value = '购物车为空，无法结算'
    return
  }
  router.push('/order/confirm')
}

onMounted(() => {
  void loadCart()
})
</script>

<template>
  <div class="shopping-cart">
    <h1>购物车</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="!isLoggedIn" class="not-logged-in">
      <p>请登录后查看购物车</p>
      <RouterLink to="/home" class="btn-primary">返回登录</RouterLink>
    </div>

    <div v-else>
      <div v-if="loading" class="spinner">加载购物车中...</div>

      <template v-else-if="cart && cart.items.length > 0">
        <div class="cart-header">
          <div>共 {{ cart.items.length }} 件商品</div>
          <button class="btn-link" @click="handleClearCart">清空购物车</button>
        </div>

        <div class="cart-table">
          <div class="table-header">
            <div class="col-product">商品</div>
            <div class="col-price">单价</div>
            <div class="col-quantity">数量</div>
            <div class="col-subtotal">小计</div>
            <div class="col-action">操作</div>
          </div>

          <div v-for="item in cart.items" :key="item.id" class="table-row">
            <div class="col-product">
              <div class="product-image">
                <img :src="item.product_cover_url" :alt="item.product_name" />
              </div>
              <div class="product-info">
                <div class="product-name">{{ item.product_name }}</div>
                <div class="product-id">商品ID: {{ item.product }}</div>
              </div>
            </div>
            <div class="col-price">¥{{ item.product_price }}</div>
            <div class="col-quantity">
              <input
                type="number"
                :value="item.quantity"
                min="1"
                @change="(e) => updateQuantity(item.id, parseInt((e.target as HTMLInputElement).value))"
                :disabled="operatingItemId === item.id"
              />
            </div>
            <div class="col-subtotal">¥{{ item.subtotal }}</div>
            <div class="col-action">
              <button
                class="btn-link btn-danger"
                @click="removeItem(item.id)"
                :disabled="operatingItemId === item.id"
              >
                删除
              </button>
            </div>
          </div>
        </div>

        <div class="cart-summary">
          <div class="summary-item">
            <span>商品总计:</span>
            <span class="total-price">¥{{ totalPrice }}</span>
          </div>
          <div class="summary-item">
            <span>运费:</span>
            <span>¥0.00</span>
          </div>
          <div class="summary-item total">
            <span>合计:</span>
            <span class="total-price">¥{{ totalPrice }}</span>
          </div>
        </div>

        <div class="cart-actions">
          <RouterLink to="/products" class="btn-secondary">继续购物</RouterLink>
          <button class="btn-primary" @click="goToCheckout">去结算</button>
        </div>
      </template>

      <div v-else class="empty-cart">
        <div class="empty-icon">🛒</div>
        <p>购物车是空的</p>
        <RouterLink to="/products" class="btn-primary">去购物</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shopping-cart {
  max-width: 1000px;
}

h1 {
  color: #103f50;
  margin-bottom: 1.5rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 0.6rem;
  margin-bottom: 1rem;
}

.alert-error {
  background: #ffe8e3;
  color: #8e3026;
}

.not-logged-in {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 0.8rem;
}

.not-logged-in p {
  margin-bottom: 1rem;
  color: #666;
}

.spinner {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.empty-cart {
  text-align: center;
  padding: 3rem 2rem;
  background: white;
  border-radius: 0.8rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-cart p {
  color: #666;
  margin-bottom: 1.5rem;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 2px solid #d4e6f0;
  margin-bottom: 1rem;
}

.cart-table {
  background: white;
  border-radius: 0.8rem;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 0.8fr;
  gap: 1rem;
  padding: 1rem;
  background: #f5f5f5;
  font-weight: 600;
  color: #1d5166;
  border-bottom: 1px solid #d4e6f0;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 0.8fr;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  align-items: center;
}

.col-product {
  display: flex;
  gap: 1rem;
}

.product-image {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  background: #f5f5f5;
  border-radius: 0.4rem;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.product-name {
  font-weight: 600;
  color: #1d5166;
  margin-bottom: 0.25rem;
}

.product-id {
  font-size: 0.85rem;
  color: #999;
}

.col-quantity input {
  width: 60px;
  padding: 0.4rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.4rem;
  text-align: center;
}

.col-price,
.col-subtotal {
  text-align: right;
  font-weight: 600;
  color: #1f9f78;
}

.col-action {
  text-align: center;
}

.cart-summary {
  background: white;
  padding: 1.5rem;
  border-radius: 0.8rem;
  text-align: right;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-item {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.summary-item.total {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1d5166;
  border-top: 1px solid #e0e0e0;
  padding-top: 0.75rem;
}

.total-price {
  color: #d32f2f;
  font-weight: 700;
  font-size: 1.1rem;
}

.cart-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary,
.btn-link,
.btn-danger {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #1f9f78;
  color: white;
}

.btn-primary:hover {
  background: #0c6f57;
}

.btn-secondary {
  background: #bbb;
  color: white;
}

.btn-secondary:hover {
  background: #999;
}

.btn-link {
  background: none;
  color: #1f9f78;
  padding: 0;
  font-size: 0.9rem;
}

.btn-link:hover:not(:disabled) {
  text-decoration: underline;
}

.btn-link:disabled,
.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-link.btn-danger {
  color: #d32f2f;
}

@media (max-width: 768px) {
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .col-product {
    grid-column: 1;
  }

  .table-header > div:not(.col-product),
  .table-row > div:not(.col-product) {
    display: none;
  }

  .cart-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
