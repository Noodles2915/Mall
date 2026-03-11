<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  getAdminServiceMessages,
  getMerchantProducts,
  replyServiceMessage,
} from '@/services/product-center'
import { getMe } from '@/services/user-center'
import type { AdminServiceMessage, MerchantProductItem } from '@/types/product-center'
import { getAuthState } from '@/utils/auth'

const accessToken = ref(getAuthState().accessToken)
const role = ref('')
const loading = ref(false)
const replyingId = ref<number | null>(null)
const error = ref('')
const success = ref('')

const messages = ref<AdminServiceMessage[]>([])
const merchantProducts = ref<MerchantProductItem[]>([])

const filters = reactive({
  productId: 0,
  hasReply: '',
})

const replyDrafts = reactive<Record<number, string>>({})

const isLoggedIn = computed(() => Boolean(accessToken.value))
const hasPermission = computed(() => role.value === 'admin' || role.value === 'merchant')

function hasReplyToBool(value: string): boolean | undefined {
  if (value === '1') {
    return true
  }
  if (value === '0') {
    return false
  }
  return undefined
}

async function loadBaseData() {
  if (!accessToken.value) {
    return
  }

  loading.value = true
  error.value = ''
  try {
    const [profile, products] = await Promise.all([
      getMe(accessToken.value),
      getMerchantProducts(accessToken.value),
    ])
    role.value = profile.role || ''
    merchantProducts.value = products

    if (profile.role === 'admin' || profile.role === 'merchant') {
      await loadMessages()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载客服管理数据失败'
  } finally {
    loading.value = false
  }
}

async function loadMessages() {
  if (!accessToken.value) {
    return
  }

  const params = {
    product_id: filters.productId || undefined,
    has_reply: hasReplyToBool(filters.hasReply),
  }

  const list = await getAdminServiceMessages(accessToken.value, params)
  messages.value = list
  for (const item of list) {
    replyDrafts[item.id] = item.reply || ''
  }
}

async function submitReply(item: AdminServiceMessage) {
  if (!accessToken.value) {
    return
  }

  const content = (replyDrafts[item.id] || '').trim()
  if (!content) {
    error.value = '回复内容不能为空'
    return
  }

  replyingId.value = item.id
  error.value = ''
  success.value = ''
  try {
    const updated = await replyServiceMessage(item.id, { reply: content }, accessToken.value)
    messages.value = messages.value.map((message) =>
      message.id === item.id ? updated : message,
    )
    replyDrafts[item.id] = updated.reply
    success.value = '回复已保存'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '回复失败'
  } finally {
    replyingId.value = null
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  void loadBaseData()
})
</script>

<template>
  <div class="service-page">
    <h1>商家客服留言管理</h1>

    <div v-if="!isLoggedIn" class="panel">
      <p>请先登录后管理客服留言。</p>
      <RouterLink class="btn-primary" to="/login">前往登录</RouterLink>
    </div>

    <template v-else>
      <p v-if="error" class="alert alert-error">{{ error }}</p>
      <p v-if="success" class="alert alert-success">{{ success }}</p>

      <div v-if="loading" class="panel">加载中...</div>

      <template v-else-if="!hasPermission">
        <div class="panel">
          <p>当前账号没有客服管理权限。</p>
          <RouterLink class="btn-primary" to="/user-center">返回用户中心</RouterLink>
        </div>
      </template>

      <template v-else>
        <section class="panel toolbar">
          <label>
            商品筛选
            <select v-model.number="filters.productId">
              <option :value="0">全部商品</option>
              <option v-for="item in merchantProducts" :key="item.id" :value="item.id">{{ item.name }}</option>
            </select>
          </label>
          <label>
            回复状态
            <select v-model="filters.hasReply">
              <option value="">全部</option>
              <option value="1">已回复</option>
              <option value="0">未回复</option>
            </select>
          </label>
          <button class="btn-secondary" type="button" @click="loadMessages">筛选</button>
          <RouterLink class="btn-secondary" to="/merchant/products">商品管理</RouterLink>
          <RouterLink class="btn-primary" to="/merchant/shipping">订单发货</RouterLink>
        </section>

        <section class="panel">
          <p v-if="messages.length === 0" class="empty-text">当前条件下暂无客服留言。</p>
          <div v-else class="message-list">
            <article v-for="item in messages" :key="item.id" class="message-card">
              <div class="message-meta">
                <h3>{{ item.product_name }}</h3>
                <p>用户：{{ item.username }} (ID: {{ item.user_id }})</p>
                <p>留言时间：{{ formatDate(item.created_at) }}</p>
                <p class="content">留言内容：{{ item.content }}</p>
              </div>

              <div class="reply-box">
                <textarea
                  v-model="replyDrafts[item.id]"
                  rows="3"
                  placeholder="输入回复内容"
                />
                <button
                  class="btn-primary"
                  type="button"
                  :disabled="replyingId === item.id"
                  @click="submitReply(item)"
                >
                  {{ replyingId === item.id ? '提交中...' : item.reply ? '更新回复' : '提交回复' }}
                </button>
              </div>
            </article>
          </div>
        </section>
      </template>
    </template>
  </div>
</template>

<style scoped>
.service-page {
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
  gap: 0.7rem;
  align-items: end;
}

label {
  display: grid;
  gap: 0.3rem;
  color: #1d5166;
  font-weight: 600;
}

select,
textarea {
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  padding: 0.55rem 0.65rem;
  font: inherit;
}

.message-list {
  display: grid;
  gap: 0.8rem;
}

.message-card {
  border: 1px solid #deebf2;
  border-radius: 0.8rem;
  padding: 0.9rem;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 0.9rem;
}

.message-meta h3,
.message-meta p {
  margin: 0.18rem 0;
}

.message-meta h3 {
  color: #103f50;
}

.message-meta p {
  color: #275063;
}

.content {
  margin-top: 0.5rem;
}

.reply-box {
  display: grid;
  gap: 0.5rem;
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

.alert-success {
  background: #e8f5e9;
  color: #2e7d32;
}

.empty-text {
  margin: 0;
  color: #4f6e7c;
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

@media (max-width: 960px) {
  .message-card {
    grid-template-columns: 1fr;
  }
}
</style>
