<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getAdminOrders, shipAdminOrder } from '@/services/order-center'
import { getMe } from '@/services/user-center'
import type { OrderListItem } from '@/types/product-center'
import { getAuthState } from '@/utils/auth'

const accessToken = ref(getAuthState().accessToken)
const role = ref('')
const loading = ref(false)
const error = ref('')
const shippingId = ref<number | null>(null)
const filterStatus = ref('pending_delivery')
const orders = ref<OrderListItem[]>([])

const isLoggedIn = computed(() => Boolean(accessToken.value))
const hasPermission = computed(() => role.value === 'admin' || role.value === 'merchant')

const statusOptions = [
  { value: 'pending_delivery', label: '待发货' },
  { value: 'pending_receipt', label: '待收货' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
]

async function loadOrders() {
  if (!accessToken.value) {
    return
  }

  loading.value = true
  error.value = ''
  try {
    const [profile, list] = await Promise.all([
      getMe(accessToken.value),
      getAdminOrders(accessToken.value, filterStatus.value),
    ])
    role.value = profile.role || ''
    orders.value = list
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载可发货订单失败'
  } finally {
    loading.value = false
  }
}

async function ship(orderId: number) {
  if (!accessToken.value) {
    return
  }
  shippingId.value = orderId
  error.value = ''
  try {
    await shipAdminOrder(orderId, accessToken.value)
    await loadOrders()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发货失败'
  } finally {
    shippingId.value = null
  }
}

onMounted(() => {
  void loadOrders()
})
</script>

<template>
  <div class="shipping-page">
    <h1>商家发货管理</h1>

    <div v-if="!isLoggedIn" class="panel">
      <p>请先登录后查看可发货订单。</p>
      <RouterLink class="btn-primary" to="/login">前往登录</RouterLink>
    </div>

    <template v-else>
      <p v-if="error" class="alert alert-error">{{ error }}</p>

      <div v-if="loading" class="panel">加载中...</div>

      <template v-else-if="!hasPermission">
        <div class="panel">
          <p>当前账号没有发货管理权限。</p>
          <RouterLink class="btn-primary" to="/user-center">返回用户中心</RouterLink>
        </div>
      </template>

      <template v-else>
        <section class="panel toolbar">
          <label>
            订单状态
            <select v-model="filterStatus" @change="loadOrders">
              <option v-for="item in statusOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
            </select>
          </label>
          <button class="btn-secondary" type="button" @click="loadOrders">刷新</button>
          <RouterLink class="btn-primary" to="/merchant/products">返回商品管理</RouterLink>
        </section>

        <section class="panel">
          <p v-if="orders.length === 0" class="empty-text">当前筛选下没有订单。</p>
          <div v-else class="order-list">
            <article v-for="item in orders" :key="item.id" class="order-card">
              <div>
                <h3>{{ item.order_number }}</h3>
                <p>状态：{{ item.status_display }}</p>
                <p>下单时间：{{ new Date(item.created_at).toLocaleString('zh-CN') }}</p>
                <p>商品项数量：{{ item.items_count }} | 金额：¥{{ item.total_price }}</p>
              </div>
              <div class="actions">
                <button
                  v-if="item.status === 'pending_delivery'"
                  class="btn-primary"
                  :disabled="shippingId === item.id"
                  @click="ship(item.id)"
                >
                  {{ shippingId === item.id ? '发货中...' : '立即发货' }}
                </button>
                <span v-else class="tag">无需发货操作</span>
              </div>
            </article>
          </div>
        </section>
      </template>
    </template>
  </div>
</template>

<style scoped>
.shipping-page {
  display: grid;
  gap: 1rem;
}

h1 {
  margin: 0;
  color: #103f50;
}

.panel {
  background: #fff;
  border: 1px solid #d4e6f0;
  border-radius: 0.9rem;
  padding: 1rem;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.8rem;
}

label {
  display: grid;
  gap: 0.3rem;
  color: #1d5166;
  font-weight: 600;
}

select {
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  padding: 0.5rem 0.6rem;
  font: inherit;
}

.order-list {
  display: grid;
  gap: 0.8rem;
}

.order-card {
  border: 1px solid #deebf2;
  border-radius: 0.8rem;
  padding: 0.9rem;
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  align-items: center;
}

.order-card h3,
.order-card p {
  margin: 0.2rem 0;
}

.order-card h3 {
  color: #103f50;
}

.order-card p {
  color: #275063;
}

.actions {
  display: grid;
  justify-items: end;
}

.tag {
  color: #557789;
  font-weight: 600;
}

.empty-text {
  margin: 0;
  color: #4f6e7c;
}

.alert {
  margin: 0;
  padding: 0.7rem;
  border-radius: 0.6rem;
}

.alert-error {
  background: #ffe8e3;
  color: #8e3026;
}

.btn-primary,
.btn-secondary {
  border: none;
  border-radius: 0.7rem;
  padding: 0.62rem 0.9rem;
  color: #fff;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}

.btn-primary {
  background: #1f9f78;
}

.btn-secondary {
  background: #697884;
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 860px) {
  .order-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    justify-items: start;
  }
}
</style>
