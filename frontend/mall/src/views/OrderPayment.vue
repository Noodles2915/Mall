<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Order } from '@/types/product-center'
import { getOrderDetail, payOrder } from '@/services/order-center'

const router = useRouter()
const route = useRoute()
const accessToken = ref(localStorage.getItem('mall_access_token') || '')

const orderId = computed(() => Number(route.params.id))
const order = ref<Order | null>(null)
const loading = ref(false)
const error = ref('')
const paying = ref(false)

async function loadOrder() {
  loading.value = true
  error.value = ''
  try {
    order.value = await getOrderDetail(orderId.value, accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载订单失败'
  } finally {
    loading.value = false
  }
}

async function handlePayment() {
  if (order.value?.status !== 'pending_payment') {
    error.value = '订单状态已更新，无法支付'
    return
  }

  paying.value = true
  error.value = ''
  try {
    const updatedOrder = await payOrder(orderId.value, accessToken.value)
    order.value = updatedOrder

    // 显示成功提示
    setTimeout(() => {
      router.push(`/orders/${orderId.value}`)
    }, 1500)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '支付失败'
  } finally {
    paying.value = false
  }
}

onMounted(() => {
  void loadOrder()
})
</script>

<template>
  <div class="order-payment">
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="loading" class="spinner">加载中...</div>

    <template v-else-if="order">
      <div class="payment-card">
        <h1>订单支付</h1>

        <div class="order-info">
          <div class="info-row">
            <span class="label">订单号:</span>
            <span class="value">{{ order.order_number }}</span>
          </div>
          <div class="info-row">
            <span class="label">订单状态:</span>
            <span class="value status" :class="order.status">{{ order.status_display }}</span>
          </div>
          <div class="info-row">
            <span class="label">创建时间:</span>
            <span class="value">{{ new Date(order.created_at).toLocaleString('zh-CN') }}</span>
          </div>
        </div>

        <div class="items-section">
          <h2>订单商品</h2>
          <div class="items-list">
            <div v-for="item in order.items" :key="item.id" class="item">
              <span class="item-name">{{ item.product_name }}</span>
              <span class="item-qty">x{{ item.quantity }}</span>
              <span class="item-price">¥{{ item.subtotal }}</span>
            </div>
          </div>
        </div>

        <div class="address-section">
          <h2>收货地址</h2>
          <p>
            {{ order.address_name }} {{ order.address_phone }}
            {{ order.address_province }} {{ order.address_city }} {{ order.address_district }}
            {{ order.address_detail }}
          </p>
          <p v-if="order.remarks" class="remarks">备注: {{ order.remarks }}</p>
        </div>

        <div class="total-section">
          <div class="total-item">
            <span>商品总额:</span>
            <span>¥{{ order.total_price }}</span>
          </div>
          <div class="total-item">
            <span>运费:</span>
            <span>¥0.00</span>
          </div>
          <div class="total-item total">
            <span>应付金额:</span>
            <span class="total-price">¥{{ order.total_price }}</span>
          </div>
        </div>

        <div v-if="order.status === 'pending_payment'" class="payment-methods">
          <h2>选择支付方式</h2>
          <p class="method-info">支付方式: {{ order.payment_method === 'online' ? '在线支付' : '线下支付' }}</p>

          <div class="payment-simulation">
            <div class="simulation-info">
              <p><strong>模拟支付说明:</strong></p>
              <p>这是一个演示系统，点击下方"模拟支付"按钮会立即完成支付。</p>
              <p>实际项目中这里应该集成真实的支付网关（如支付宝、微信支付等）。</p>
            </div>
          </div>

          <button class="btn-pay" @click="handlePayment" :disabled="paying">
            {{ paying ? '支付处理中...' : '模拟支付' }}
          </button>
        </div>

        <div v-else class="payment-success">
          <div class="success-icon">✓</div>
          <h2>支付成功</h2>
          <p>您的订单已成功支付，请等待商家发货。</p>
          <RouterLink :to="`/orders/${order.id}`" class="btn-primary">查看订单详情</RouterLink>
        </div>

        <RouterLink to="/orders" class="link-back">返回我的订单</RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.order-payment {
  max-width: 600px;
  margin: 0 auto;
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
  padding: 2rem;
  color: #999;
}

.payment-card {
  background: white;
  border-radius: 0.8rem;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #103f50;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.5rem;
}

h2 {
  color: #1d5166;
  font-size: 1.05rem;
  margin: 1.5rem 0 1rem;
  border-bottom: 2px solid #d4e6f0;
  padding-bottom: 0.5rem;
}

.order-info {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 0.6rem;
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.label {
  color: #666;
  font-weight: 600;
}

.value {
  color: #1d5166;
}

.status {
  padding: 0.2rem 0.6rem;
  border-radius: 0.3rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.status.pending_payment {
  background: #fff3cd;
  color: #856404;
}

.status.pending_delivery {
  background: #d1ecf1;
  color: #0c5460;
}

.status.pending_receipt {
  background: #d4edda;
  color: #155724;
}

.status.completed {
  background: #d4edda;
  color: #155724;
}

.status.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.items-section,
.address-section {
  margin-bottom: 1.5rem;
}

.items-list {
  border: 1px solid #e0e0e0;
  border-radius: 0.4rem;
  overflow: hidden;
}

.item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.9rem;
}

.item:last-child {
  border-bottom: none;
}

.item-name {
  flex: 1;
  color: #1d5166;
}

.item-qty {
  color: #666;
  margin: 0 0.5rem;
}

.item-price {
  color: #1f9f78;
  font-weight: 600;
}

.address-section p {
  color: #555;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0.5rem 0;
}

.remarks {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f9f9f9;
  border-left: 3px solid #fd7e14;
  font-style: italic;
}

.total-section {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 0.6rem;
  margin-bottom: 1.5rem;
}

.total-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.total-item.total {
  font-size: 1.1rem;
  font-weight: 700;
  border-top: 1px solid #d4e6f0;
  padding-top: 0.75rem;
  margin-bottom: 0;
}

.total-price {
  color: #d32f2f;
  font-weight: 700;
}

.payment-methods {
  margin-bottom: 1.5rem;
}

.method-info {
  color: #666;
  font-size: 0.95rem;
  margin: 0.5rem 0 1rem;
}

.payment-simulation {
  background: #e3f2fd;
  border-left: 4px solid #1976d2;
  padding: 1rem;
  border-radius: 0.4rem;
  margin-bottom: 1.5rem;
}

.simulation-info {
  font-size: 0.9rem;
  color: #0d47a1;
}

.simulation-info p {
  margin: 0.5rem 0;
}

.btn-pay {
  width: 100%;
  padding: 0.9rem;
  background: #1f9f78;
  color: white;
  border: none;
  border-radius: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-pay:hover:not(:disabled) {
  background: #0c6f57;
}

.btn-pay:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.payment-success {
  text-align: center;
  padding: 2rem 0;
}

.success-icon {
  font-size: 3rem;
  color: #1f9f78;
  margin-bottom: 1rem;
}

.payment-success h2 {
  border: none;
  margin: 0 0 0.5rem;
  color: #1f9f78;
}

.payment-success p {
  color: #666;
  margin-bottom: 1.5rem;
}

.btn-primary {
  display: inline-block;
  padding: 0.6rem 1.5rem;
  background: #1f9f78;
  color: white;
  text-decoration: none;
  border-radius: 0.6rem;
  font-weight: 600;
}

.btn-primary:hover {
  background: #0c6f57;
}

.link-back {
  display: block;
  text-align: center;
  margin-top: 1.5rem;
  color: #1f9f78;
  text-decoration: none;
  font-weight: 600;
}

.link-back:hover {
  text-decoration: underline;
}
</style>
