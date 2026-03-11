<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { ShoppingCart } from '@/types/product-center'
import type { AddressItem } from '@/types/user-center'
import { getCart, clearCart, createOrder } from '@/services/order-center'
import { getAddresses } from '@/services/user-center'

const router = useRouter()
const accessToken = ref(localStorage.getItem('mall_access_token') || '')

const cart = ref<ShoppingCart | null>(null)
const addresses = ref<AddressItem[]>([])
const selectedAddressId = ref<number | null>(null)
const remarks = ref('')
const paymentMethod = ref('online')

const loading = ref(false)
const addressing = ref(false)
const error = ref('')
const creating = ref(false)

const selectedAddress = computed(() => {
  return addresses.value.find((a) => a.id === selectedAddressId.value)
})

const totalPrice = computed(() => {
  if (!cart.value) return '0.00'
  return (
    cart.value.items.reduce((sum, item) => {
      return sum + parseFloat(item.subtotal)
    }, 0)
  ).toFixed(2)
})

async function loadData() {
  loading.value = true
  addressing.value = true
  error.value = ''
  try {
    cart.value = await getCart(accessToken.value)
    addresses.value = await getAddresses(accessToken.value)

    // 自动选择默认地址
    const defaultAddress = addresses.value.find((a) => a.is_default)
    if (defaultAddress) {
      selectedAddressId.value = defaultAddress.id
    } else if (addresses.value.length > 0) {
      const firstAddress = addresses.value[0]
      if (firstAddress) {
        selectedAddressId.value = firstAddress.id
      }
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载数据失败'
  } finally {
    loading.value = false
    addressing.value = false
  }
}

async function handleConfirm() {
  error.value = ''

  if (!selectedAddressId.value) {
    error.value = '请选择收货地址'
    return
  }

  if (!cart.value || cart.value.items.length === 0) {
    error.value = '购物车为空'
    return
  }

  creating.value = true
  try {
    const order = await createOrder(
      {
        address_id: selectedAddressId.value,
        remarks: remarks.value,
        payment_method: paymentMethod.value,
      },
      accessToken.value,
    )

    // 清空购物车
    await clearCart(accessToken.value)

    // 跳转到支付页面
    router.push(`/order/payment/${order.id}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建订单失败'
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  void loadData()
})
</script>

<template>
  <div class="order-confirm">
    <h1>确认订单</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="loading" class="spinner">加载中...</div>

    <template v-else>
      <!-- Order Items -->
      <section class="section">
        <h2>订单商品</h2>
        <div v-if="cart && cart.items.length > 0" class="items-list">
          <div v-for="item in cart.items" :key="item.id" class="item">
            <div class="item-image">
              <img :src="item.product_cover_url" :alt="item.product_name" />
            </div>
            <div class="item-info">
              <div class="item-name">{{ item.product_name }}</div>
              <div class="item-specs">数量: {{ item.quantity }}</div>
            </div>
            <div class="item-price">
              <div class="unit-price">¥{{ item.product_price }}</div>
              <div class="sub-price">小计: ¥{{ item.subtotal }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Address Selection -->
      <section class="section">
        <h2>选择收货地址</h2>
        <div v-if="addressing" class="spinner">加载地址中...</div>
        <div v-else-if="addresses.length > 0" class="address-list">
          <label v-for="address in addresses" :key="address.id" class="address-option">
            <input
              type="radio"
              :value="address.id"
              v-model="selectedAddressId"
              :disabled="creating"
            />
            <span class="address-content">
              <span class="address-name">{{ address.name }} {{ address.phone }}</span>
              <span v-if="address.is_default" class="default-badge">默认</span>
              <div class="address-text">
                {{ address.province }} {{ address.city }} {{ address.district }} {{ address.detail }}
              </div>
            </span>
          </label>

          <div v-if="selectedAddress" class="selected-address-display">
            <strong>已选地址:</strong>
            <p>
              {{ selectedAddress.name }} {{ selectedAddress.phone }}
              {{ selectedAddress.province }} {{ selectedAddress.city }} {{ selectedAddress.district }}
              {{ selectedAddress.detail }}
            </p>
          </div>
        </div>
        <div v-else class="no-data">
          没有地址，请<RouterLink to="/addresses">创建地址</RouterLink>
        </div>
      </section>

      <!-- Remarks -->
      <section class="section">
        <h2>订单备注</h2>
        <textarea
          v-model="remarks"
          placeholder="请输入订单备注（可选）"
          rows="3"
          :disabled="creating"
        />
      </section>

      <!-- Payment Method -->
      <section class="section">
        <h2>支付方式</h2>
        <div class="payment-options">
          <label>
            <input
              type="radio"
              value="online"
              v-model="paymentMethod"
              :disabled="creating"
            />
            <span>在线支付</span>
          </label>
          <label>
            <input type="radio" value="offline" v-model="paymentMethod" :disabled="creating" />
            <span>线下支付</span>
          </label>
        </div>
      </section>

      <!-- Order Summary -->
      <section class="section order-summary">
        <div class="summary-item">
          <span>商品总额:</span>
          <span>¥{{ totalPrice }}</span>
        </div>
        <div class="summary-item">
          <span>运费:</span>
          <span>¥0.00</span>
        </div>
        <div class="summary-item total">
          <span>合计:</span>
          <span class="total-price">¥{{ totalPrice }}</span>
        </div>
      </section>

      <!-- Actions -->
      <div class="actions">
        <RouterLink to="/cart" class="btn-secondary">返回购物车</RouterLink>
        <button class="btn-primary" @click="handleConfirm" :disabled="creating || !selectedAddressId">
          {{ creating ? '创建订单中...' : '创建订单' }}
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.order-confirm {
  max-width: 800px;
}

h1 {
  color: #103f50;
  margin-bottom: 1.5rem;
}

h2 {
  color: #1d5166;
  font-size: 1.1rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #d4e6f0;
  padding-bottom: 0.5rem;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.8rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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

.spinner {
  text-align: center;
  padding: 1rem;
  color: #999;
}

.items-list {
  display: grid;
  gap: 1rem;
}

.item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 0.6rem;
  border: 1px solid #e0e0e0;
}

.item-image {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 0.4rem;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
}

.item-name {
  font-weight: 600;
  color: #1d5166;
  margin-bottom: 0.25rem;
}

.item-specs {
  font-size: 0.9rem;
  color: #666;
}

.item-price {
  text-align: right;
}

.unit-price {
  color: #1f9f78;
  font-weight: 600;
}

.sub-price {
  font-size: 0.9rem;
  color: #666;
}

.address-list {
  display: grid;
  gap: 0.75rem;
}

.address-option {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 0.6rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.address-option input {
  margin-top: 0.25rem;
  cursor: pointer;
}

.address-option:has(input:checked) {
  border-color: #1f9f78;
  background: #f0fef8;
}

.address-content {
  flex: 1;
}

.address-name {
  font-weight: 600;
  color: #1d5166;
  display: inline-block;
  margin-right: 0.5rem;
}

.default-badge {
  background: #1f9f78;
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 0.2rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.address-text {
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.3rem;
}

.selected-address-display {
  margin-top: 1rem;
  padding: 1rem;
  background: #e8f5e9;
  border-radius: 0.4rem;
  border-left: 4px solid #1f9f78;
}

.selected-address-display p {
  margin: 0.5rem 0 0;
  color: #2e7d32;
  font-size: 0.9rem;
}

.no-data {
  text-align: center;
  padding: 1rem;
  color: #999;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.4rem;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
}

textarea:focus {
  outline: none;
  border-color: #1f9f78;
}

textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.payment-options {
  display: flex;
  gap: 2rem;
}

.payment-options label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.payment-options input {
  cursor: pointer;
}

.order-summary {
  background: #f9f9f9;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.summary-item.total {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1d5166;
  border-top: 1px solid #d4e6f0;
  padding-top: 0.75rem;
  margin-top: 0.75rem;
  margin-bottom: 0;
}

.total-price {
  color: #d32f2f;
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  text-decoration: none;
}

.btn-primary {
  background: #1f9f78;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0c6f57;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #bbb;
  color: white;
}

.btn-secondary:hover {
  background: #999;
}

@media (max-width: 600px) {
  .actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
