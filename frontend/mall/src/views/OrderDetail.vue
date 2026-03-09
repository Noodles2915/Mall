<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Order } from '@/types/product-center'
import { getOrderDetail, cancelOrder, receiveOrder } from '@/services/order-center'

const router = useRouter()
const route = useRoute()
const accessToken = ref(localStorage.getItem('mall_access_token') || '')

const orderId = computed(() => Number(route.params.id))
const order = ref<Order | null>(null)
const loading = ref(false)
const error = ref('')
const operating = ref(false)

async function loadOrder() {
  loading.value = true
  error.value = ''
  try {
    order.value = await getOrderDetail(orderId.value, accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载订单详情失败'
  } finally {
    loading.value = false
  }
}

async function handleCancel() {
  if (!order.value) return
  if (!confirm('确定要取消订单吗？')) return

  operating.value = true
  error.value = ''
  try {
    order.value = await cancelOrder(orderId.value, accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '取消订单失败'
  } finally {
    operating.value = false
  }
}

async function handleReceive() {
  if (!order.value) return
  if (!confirm('确认已收货吗？')) return

  operating.value = true
  error.value = ''
  try {
    order.value = await receiveOrder(orderId.value, accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '确认收货失败'
  } finally {
    operating.value = false
  }
}

function getStatusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    pending_payment: 'warning',
    pending_delivery: 'info',
    pending_receipt: 'success',
    completed: 'success',
    cancelled: 'danger',
  }
  return classes[status] || 'default'
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  void loadOrder()
})
</script>

<template>
  <div class="order-detail">
    <div class="header">
      <h1>订单详情</h1>
      <RouterLink to="/orders" class="link-back">← 返回订单列表</RouterLink>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="loading" class="spinner">加载中...</div>

    <template v-else-if="order">
      <!-- Order Status Timeline -->
      <div class="status-timeline">
        <div class="timeline-item" :class="{ completed: order.status !== 'pending_payment' }">
          <div class="timeline-label">已创建</div>
          <div class="timeline-time">{{ formatDate(order.created_at) }}</div>
        </div>
        <div
          class="timeline-item"
          :class="{ completed: ['pending_delivery', 'pending_receipt', 'completed'].includes(order.status) }"
        >
          <div class="timeline-label">已支付</div>
          <div class="timeline-time">{{ formatDate(order.paid_at) }}</div>
        </div>
        <div
          class="timeline-item"
          :class="{ completed: ['pending_receipt', 'completed'].includes(order.status) }"
        >
          <div class="timeline-label">已发货</div>
          <div class="timeline-time">{{ formatDate(order.shipped_at) }}</div>
        </div>
        <div class="timeline-item" :class="{ completed: order.status === 'completed' }">
          <div class="timeline-label">已收货</div>
          <div class="timeline-time">{{ formatDate(order.received_at) }}</div>
        </div>
      </div>

      <!-- Order Info Card -->
      <div class="card order-info-card">
        <div class="card-header">
          <div>
            <h2>订单信息</h2>
            <p class="order-number">{{ order.order_number }}</p>
          </div>
          <div class="status-badge" :class="getStatusBadgeClass(order.status)">
            {{ order.status_display }}
          </div>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="label">创建时间:</span>
            <span class="value">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">支付方式:</span>
            <span class="value">{{ order.payment_method === 'online' ? '在线支付' : '线下支付' }}</span>
          </div>
        </div>
      </div>

      <!-- Items Card -->
      <div class="card items-card">
        <h3>订单商品</h3>
        <div class="items-table">
          <div class="table-header">
            <div class="col-name">商品名称</div>
            <div class="col-price">单价</div>
            <div class="col-qty">数量</div>
            <div class="col-total">小计</div>
          </div>
          <div v-for="item in order.items" :key="item.id" class="table-row">
            <div class="col-name">{{ item.product_name }}</div>
            <div class="col-price">¥{{ item.product_price }}</div>
            <div class="col-qty">{{ item.quantity }}</div>
            <div class="col-total">¥{{ item.subtotal }}</div>
          </div>
        </div>
      </div>

      <!-- Address Card -->
      <div class="card address-card">
        <h3>收货地址</h3>
        <div class="address-info">
          <p class="name">{{ order.address_name }} {{ order.address_phone }}</p>
          <p class="detail">
            {{ order.address_province }} {{ order.address_city }} {{ order.address_district }}
          </p>
          <p class="detail">{{ order.address_detail }}</p>
        </div>
      </div>

      <!-- Summary Card -->
      <div class="card summary-card">
        <div class="summary-item">
          <span>商品总额:</span>
          <span>¥{{ order.total_price }}</span>
        </div>
        <div class="summary-item">
          <span>运费:</span>
          <span>¥0.00</span>
        </div>
        <div class="summary-item total">
          <span>应付金额:</span>
          <span class="total-price">¥{{ order.total_price }}</span>
        </div>
      </div>

      <!-- Remarks -->
      <div v-if="order.remarks" class="card remarks-card">
        <h3>订单备注</h3>
        <p>{{ order.remarks }}</p>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button
          v-if="order.status === 'pending_payment'"
          class="btn-primary"
          @click="() => router.push(`/order/payment/${order.id}`)"
        >
          继续支付
        </button>
        <button
          v-if="['pending_payment', 'pending_delivery'].includes(order.status)"
          class="btn-danger"
          @click="handleCancel"
          :disabled="operating"
        >
          {{ operating ? '取消中...' : '取消订单' }}
        </button>
        <button
          v-if="order.status === 'pending_receipt'"
          class="btn-primary"
          @click="handleReceive"
          :disabled="operating"
        >
          {{ operating ? '处理中...' : '确认收货' }}
        </button>
        <RouterLink to="/orders" class="btn-secondary">返回订单列表</RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.order-detail {
  max-width: 900px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h1 {
  color: #103f50;
  margin: 0;
}

.link-back {
  color: #1f9f78;
  text-decoration: none;
  font-weight: 600;
}

.link-back:hover {
  text-decoration: underline;
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

.status-timeline {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 0.8rem;
}

.timeline-item {
  text-align: center;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 0.6rem;
  background: #f9f9f9;
  position: relative;
}

.timeline-item.completed {
  background: #d4edda;
  border-color: #1f9f78;
}

.timeline-label {
  font-weight: 600;
  color: #1d5166;
  margin-bottom: 0.5rem;
}

.timeline-time {
  font-size: 0.85rem;
  color: #666;
}

.card {
  background: white;
  border-radius: 0.8rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.card h2,
.card h3 {
  color: #1d5166;
  margin: 0 0 0.5rem;
}

.order-number {
  font-size: 0.9rem;
  color: #999;
  margin: 0;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 0.4rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge.info {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.danger {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.default {
  background: #e2e3e5;
  color: #383d41;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.info-item .label {
  color: #666;
  font-weight: 600;
}

.info-item .value {
  color: #1d5166;
}

.items-table {
  border: 1px solid #e0e0e0;
  border-radius: 0.4rem;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  background: #f5f5f5;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.table-row:last-child {
  border-bottom: none;
}

.col-name {
  color: #1d5166;
  font-weight: 600;
}

.col-price,
.col-total {
  text-align: right;
  color: #1f9f78;
  font-weight: 600;
}

.address-info p {
  margin: 0 0 0.5rem;
  color: #555;
}

.address-info .name {
  font-weight: 600;
  color: #1d5166;
}

.address-info .detail {
  font-size: 0.95rem;
  line-height: 1.5;
}

.summary-card {
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
  border-top: 1px solid #d4e6f0;
  padding-top: 0.75rem;
  margin-bottom: 0;
}

.total-price {
  color: #d32f2f;
  font-weight: 700;
}

.remarks-card {
  background: #fff9e6;
  border-left: 4px solid #fd7e14;
}

.remarks-card p {
  margin: 0;
  color: #555;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-primary {
  background: #1f9f78;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0c6f57;
}

.btn-secondary {
  background: #bbb;
  color: white;
}

.btn-secondary:hover {
  background: #999;
}

.btn-danger {
  background: #d32f2f;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #b71c1c;
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .status-timeline {
    grid-template-columns: repeat(2, 1fr);
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr 1fr;
  }

  .col-price,
  .col-qty {
    text-align: left;
  }
}
</style>
