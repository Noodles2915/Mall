<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { OrderListItem } from '@/types/product-center'
import { getOrders } from '@/services/order-center'

const accessToken = ref(localStorage.getItem('mall_access_token') || '')
const orders = ref<OrderListItem[]>([])
const loading = ref(false)
const error = ref('')
const filterStatus = ref<string | null>(null)

const isLoggedIn = computed(() => Boolean(accessToken.value))

const filteredOrders = computed(() => {
  if (!filterStatus.value) {
    return orders.value
  }
  return orders.value.filter((order) => order.status === filterStatus.value)
})

const statusOptions = [
  { value: null, label: '全部订单' },
  { value: 'pending_payment', label: '待支付' },
  { value: 'pending_delivery', label: '待发货' },
  { value: 'pending_receipt', label: '待收货' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
]

async function loadOrders() {
  if (!isLoggedIn.value) {
    error.value = '请先登录'
    return
  }

  loading.value = true
  error.value = ''
  try {
    orders.value = await getOrders(accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载订单失败'
  } finally {
    loading.value = false
  }
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending_payment: 'warning',
    pending_delivery: 'info',
    pending_receipt: 'success',
    completed: 'success',
    cancelled: 'danger',
  }
  return colors[status] || 'default'
}

onMounted(() => {
  void loadOrders()
})
</script>

<template>
  <div class="order-list">
    <h1>我的订单</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="!isLoggedIn" class="not-logged-in">
      <p>请登录后查看订单</p>
      <RouterLink to="/login" class="btn-primary">前往登录</RouterLink>
    </div>

    <template v-else>
      <!-- Status Filter -->
      <div class="filter-bar">
        <button
          v-for="option in statusOptions"
          :key="option.value || 'all'"
          class="filter-btn"
          :class="{ active: filterStatus === option.value }"
          @click="filterStatus = option.value"
        >
          {{ option.label }}
        </button>
      </div>

      <!-- Orders List -->
      <div v-if="loading" class="spinner">加载中...</div>
      <div v-else-if="filteredOrders.length === 0" class="no-data">
        <p>没有订单</p>
        <RouterLink to="/products" class="btn-primary">去购物</RouterLink>
      </div>

      <div v-else class="orders-container">
        <div v-for="order in filteredOrders" :key="order.id" class="order-card">
          <div class="order-header">
            <div class="order-info-left">
              <div class="order-number">订单号: {{ order.order_number }}</div>
              <div class="order-date">{{ new Date(order.created_at).toLocaleString('zh-CN') }}</div>
            </div>
            <div class="order-status" :class="getStatusColor(order.status)">
              {{ order.status_display }}
            </div>
          </div>

          <div class="order-body">
            <div class="order-items">
              <div class="item-preview">已购买 {{ order.items_count }} 件商品</div>
            </div>
          </div>

          <div class="order-footer">
            <div class="order-total">
              <span>合计:</span>
              <span class="total-price">¥{{ order.total_price }}</span>
            </div>
            <div class="order-actions">
              <RouterLink :to="`/orders/${order.id}`" class="btn-link">查看详情</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.order-list {
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

.filter-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d4e6f0;
  background: white;
  border-radius: 0.6rem;
  cursor: pointer;
  color: #1d5166;
  font-weight: 600;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #1f9f78;
  color: #1f9f78;
}

.filter-btn.active {
  background: #1f9f78;
  color: white;
  border-color: #1f9f78;
}

.spinner {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.no-data {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 0.8rem;
}

.no-data p {
  color: #666;
  margin-bottom: 1rem;
}

.orders-container {
  display: grid;
  gap: 1rem;
}

.order-card {
  background: white;
  border: 1px solid #d4e6f0;
  border-radius: 0.8rem;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.order-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
}

.order-info-left {
  flex: 1;
}

.order-number {
  font-weight: 600;
  color: #1d5166;
  margin-bottom: 0.25rem;
}

.order-date {
  font-size: 0.85rem;
  color: #999;
}

.order-status {
  padding: 0.4rem 0.8rem;
  border-radius: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
  min-width: 80px;
}

.order-status.warning {
  background: #fff3cd;
  color: #856404;
}

.order-status.info {
  background: #d1ecf1;
  color: #0c5460;
}

.order-status.success {
  background: #d4edda;
  color: #155724;
}

.order-status.danger {
  background: #f8d7da;
  color: #721c24;
}

.order-status.default {
  background: #e2e3e5;
  color: #383d41;
}

.order-body {
  padding: 1rem;
}

.order-items {
  margin-bottom: 1rem;
}

.item-preview {
  color: #666;
  font-size: 0.9rem;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
}

.order-total {
  font-size: 0.95rem;
  color: #1d5166;
}

.total-price {
  color: #d32f2f;
  font-weight: 700;
  margin-left: 0.5rem;
}

.order-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-link {
  padding: 0.4rem 0.8rem;
  background: #1f9f78;
  color: white;
  text-decoration: none;
  border-radius: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background 0.2s;
}

.btn-link:hover {
  background: #0c6f57;
}

.btn-primary {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background: #1f9f78;
  color: white;
  text-decoration: none;
  border-radius: 0.6rem;
  font-weight: 600;
}

.btn-primary:hover {
  background: #0c6f57;
}

@media (max-width: 600px) {
  .order-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .order-status {
    align-self: flex-end;
    margin-top: 0.5rem;
  }

  .order-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
