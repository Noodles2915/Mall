<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  createMerchantProduct,
  deleteMerchantProduct,
  getCategories,
  getMerchantProducts,
  publishMerchantProduct,
  updateMerchantProduct,
  unpublishMerchantProduct,
} from '@/services/product-center'
import { getMe } from '@/services/user-center'
import type {
  Category,
  MerchantProductItem,
  MerchantProductPayload,
} from '@/types/product-center'
import { getAuthState } from '@/utils/auth'

const accessToken = ref(getAuthState().accessToken)
const role = ref('')
const loading = ref(false)
const submitting = ref(false)
const actionLoadingId = ref<number | null>(null)

const listError = ref('')
const submitError = ref('')
const submitSuccess = ref('')
const editingId = ref<number | null>(null)

const categories = ref<Category[]>([])
const products = ref<MerchantProductItem[]>([])

const form = reactive({
  category: 0,
  name: '',
  subtitle: '',
  cover_url: '',
  price: '0.00',
  stock: 1,
  is_hot: false,
  description: '',
  customer_service_hint: '',
  specsText: '颜色: 黑, 白',
})

const isLoggedIn = computed(() => Boolean(accessToken.value))
const hasPermission = computed(() => role.value === 'admin' || role.value === 'merchant')

function normalizeCoverUrl(raw: string): string {
  const normalized = raw
    .trim()
    .replace(/：/g, ':')
    .replace(/／/g, '/')
    .replace(/。/g, '.')

  if (!normalized) {
    return ''
  }

  const withScheme = /^https?:\/\//i.test(normalized)
    ? normalized
    : normalized.startsWith('//')
      ? `https:${normalized}`
      : `https://${normalized}`

  const parsed = new URL(withScheme)
  if (!['http:', 'https:'].includes(parsed.protocol) || !parsed.hostname) {
    throw new Error('封面图 URL 格式不正确，请输入完整可访问地址')
  }

  return parsed.toString()
}

function parseSpecs(raw: string): Record<string, string[]> {
  const result: Record<string, string[]> = {}
  const lines = raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  lines.forEach((line) => {
    const separator = line.includes(':') ? ':' : line.includes('：') ? '：' : ''
    if (!separator) {
      return
    }
    const [keyPart = '', valuePart = ''] = line.split(separator)
    const key = keyPart.trim()
    const values = valuePart
      .split(/[，,]/)
      .map((item) => item.trim())
      .filter(Boolean)
    if (key && values.length > 0) {
      result[key] = values
    }
  })

  return result
}

async function loadBaseData() {
  if (!accessToken.value) {
    return
  }

  loading.value = true
  listError.value = ''
  try {
    const [profile, categoryList, merchantProducts] = await Promise.all([
      getMe(accessToken.value),
      getCategories(),
      getMerchantProducts(accessToken.value),
    ])
    role.value = profile.role || ''
    categories.value = categoryList
    products.value = merchantProducts
    const firstCategory = categoryList[0]
    if (!form.category && firstCategory) {
      form.category = firstCategory.id
    }
  } catch (err) {
    listError.value = err instanceof Error ? err.message : '加载商家商品数据失败'
  } finally {
    loading.value = false
  }
}

async function createProduct() {
  submitError.value = ''
  submitSuccess.value = ''

  if (!accessToken.value) {
    submitError.value = '请先登录'
    return
  }

  if (!form.category) {
    submitError.value = '请选择商品分类'
    return
  }

  if (!form.name.trim()) {
    submitError.value = '请填写商品名称'
    return
  }

  let normalizedCoverUrl = ''
  try {
    normalizedCoverUrl = normalizeCoverUrl(form.cover_url)
  } catch {
    submitError.value = '封面图 URL 格式不正确，请检查后重试'
    return
  }

  if (!normalizedCoverUrl) {
    submitError.value = '请填写封面图 URL'
    return
  }

  const payload: MerchantProductPayload = {
    category: form.category,
    name: form.name.trim(),
    subtitle: form.subtitle.trim(),
    cover_url: normalizedCoverUrl,
    price: form.price,
    stock: Number(form.stock),
    is_hot: form.is_hot,
    is_active: false,
    description: form.description.trim(),
    specs: parseSpecs(form.specsText),
    customer_service_hint: form.customer_service_hint.trim(),
  }

  submitting.value = true
  try {
    if (editingId.value) {
      await updateMerchantProduct(editingId.value, payload, accessToken.value)
      submitSuccess.value = '商品信息已更新'
    } else {
      await createMerchantProduct(payload, accessToken.value)
      submitSuccess.value = '商品已创建，可在下方点击“上架”后对外展示'
    }
    resetForm()
    products.value = await getMerchantProducts(accessToken.value)
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : '商品保存失败'
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  editingId.value = null
  form.name = ''
  form.subtitle = ''
  form.cover_url = ''
  form.price = '0.00'
  form.stock = 1
  form.is_hot = false
  form.description = ''
  form.customer_service_hint = ''
  form.specsText = '颜色: 黑, 白'
}

function startEdit(item: MerchantProductItem) {
  editingId.value = item.id
  form.category = item.category
  form.name = item.name
  form.subtitle = item.subtitle
  form.cover_url = item.cover_url
  form.price = item.price
  form.stock = item.stock
  form.is_hot = item.is_hot
  form.description = item.description
  form.customer_service_hint = item.customer_service_hint
  const specRows = Object.entries(item.specs || {}).map(([key, values]) => `${key}: ${values.join(', ')}`)
  form.specsText = specRows.join('\n') || '颜色: 黑, 白'
}

async function deleteItem(item: MerchantProductItem) {
  if (!accessToken.value) {
    return
  }
  const confirmed = window.confirm(`确定删除商品【${item.name}】吗？该操作不可恢复。`)
  if (!confirmed) {
    return
  }
  actionLoadingId.value = item.id
  listError.value = ''
  try {
    await deleteMerchantProduct(item.id, accessToken.value)
    products.value = products.value.filter((product) => product.id !== item.id)
    if (editingId.value === item.id) {
      resetForm()
    }
  } catch (err) {
    listError.value = err instanceof Error ? err.message : '删除商品失败'
  } finally {
    actionLoadingId.value = null
  }
}

async function publishItem(item: MerchantProductItem) {
  if (!accessToken.value) {
    return
  }
  actionLoadingId.value = item.id
  try {
    const updated = await publishMerchantProduct(item.id, accessToken.value)
    products.value = products.value.map((product) => (product.id === item.id ? updated : product))
  } catch (err) {
    listError.value = err instanceof Error ? err.message : '商品上架失败'
  } finally {
    actionLoadingId.value = null
  }
}

async function unpublishItem(item: MerchantProductItem) {
  if (!accessToken.value) {
    return
  }
  actionLoadingId.value = item.id
  try {
    const updated = await unpublishMerchantProduct(item.id, accessToken.value)
    products.value = products.value.map((product) => (product.id === item.id ? updated : product))
  } catch (err) {
    listError.value = err instanceof Error ? err.message : '商品下架失败'
  } finally {
    actionLoadingId.value = null
  }
}

onMounted(() => {
  void loadBaseData()
})
</script>

<template>
  <div class="merchant-page">
    <h1>商家商品上架</h1>

    <div v-if="!isLoggedIn" class="login-required">
      <p>请先登录后再管理商家商品。</p>
      <RouterLink class="btn-primary" to="/login">前往登录</RouterLink>
    </div>

    <template v-else>
      <p v-if="listError" class="alert alert-error">{{ listError }}</p>
      <p v-if="submitError" class="alert alert-error">{{ submitError }}</p>
      <p v-if="submitSuccess" class="alert alert-success">{{ submitSuccess }}</p>

      <div v-if="loading" class="panel">加载中...</div>

      <template v-else-if="!hasPermission">
        <div class="panel">
          <p>当前账号不是商家或管理员，无法访问商家上架功能。</p>
          <RouterLink class="btn-primary" to="/user-center">去用户中心申请商家资质</RouterLink>
        </div>
      </template>

      <template v-else>
        <section class="panel quick-entry-panel">
          <h2>经营快捷入口</h2>
          <div class="quick-entry-grid">
            <RouterLink class="quick-entry" to="/merchant/shipping">发货管理</RouterLink>
            <RouterLink class="quick-entry" to="/merchant/service-messages">客服留言管理</RouterLink>
          </div>
          <p class="entry-hint">使用前台客服管理页可按商品筛选留言并直接回复。</p>
        </section>

        <section class="panel form-panel">
          <h2>{{ editingId ? '编辑商品' : '创建待上架商品' }}</h2>
          <div class="form-grid">
            <label>
              商品分类
              <select v-model.number="form.category">
                <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
              </select>
            </label>
            <label>
              商品名称
              <input v-model="form.name" type="text" placeholder="如：Nova M5" />
            </label>
            <label>
              副标题
              <input v-model="form.subtitle" type="text" placeholder="如：轻薄长续航" />
            </label>
            <label>
              封面图 URL
              <input v-model="form.cover_url" type="url" placeholder="https://..." />
            </label>
            <label>
              价格
              <input v-model="form.price" type="text" placeholder="1999.00" />
            </label>
            <label>
              库存
              <input v-model.number="form.stock" type="number" min="0" />
            </label>
            <label class="check-row">
              <input v-model="form.is_hot" type="checkbox" /> 热门商品
            </label>
            <label>
              客服提示
              <input v-model="form.customer_service_hint" type="text" placeholder="联系客服获取活动价" />
            </label>
          </div>

          <label class="block">
            商品描述
            <textarea v-model="form.description" rows="3" placeholder="请填写商品亮点与卖点" />
          </label>

          <label class="block">
            商品规格（每行一项，格式：键: 值1, 值2）
            <textarea v-model="form.specsText" rows="4" />
          </label>

          <div class="form-actions">
            <button class="btn-primary" type="button" :disabled="submitting" @click="createProduct">
              {{ submitting ? '提交中...' : editingId ? '保存修改' : '创建商品' }}
            </button>
            <button
              v-if="editingId"
              class="btn-secondary"
              type="button"
              :disabled="submitting"
              @click="resetForm"
            >
              取消编辑
            </button>
          </div>
        </section>

        <section class="panel list-panel">
          <h2>我的商品与上架操作</h2>
          <p v-if="products.length === 0" class="empty-text">暂无商品，请先创建商品。</p>
          <div v-else class="product-list">
            <article v-for="item in products" :key="item.id" class="product-card">
              <img :src="item.cover_url" :alt="item.name" />
              <div class="meta">
                <h3>{{ item.name }}</h3>
                <p class="subtitle">{{ item.subtitle || '暂无副标题' }}</p>
                <p>价格：¥{{ item.price }} | 库存：{{ item.stock }}</p>
                <p>
                  状态：
                  <span :class="item.is_active ? 'status-up' : 'status-down'">
                    {{ item.is_active ? '已上架' : '未上架' }}
                  </span>
                </p>
              </div>
              <div class="actions">
                <button
                  class="btn-secondary"
                  :disabled="actionLoadingId === item.id"
                  @click="startEdit(item)"
                >
                  编辑
                </button>
                <button
                  v-if="!item.is_active"
                  class="btn-primary"
                  :disabled="actionLoadingId === item.id"
                  @click="publishItem(item)"
                >
                  {{ actionLoadingId === item.id ? '处理中...' : '上架' }}
                </button>
                <button
                  v-else
                  class="btn-secondary"
                  :disabled="actionLoadingId === item.id"
                  @click="unpublishItem(item)"
                >
                  {{ actionLoadingId === item.id ? '处理中...' : '下架' }}
                </button>
                <button
                  class="btn-danger"
                  :disabled="actionLoadingId === item.id"
                  @click="deleteItem(item)"
                >
                  {{ actionLoadingId === item.id ? '处理中...' : '删除' }}
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
.merchant-page {
  display: grid;
  gap: 1rem;
}

h1,
h2 {
  margin: 0;
  color: #103f50;
}

.panel {
  background: #fff;
  border: 1px solid #d4e6f0;
  border-radius: 0.9rem;
  padding: 1rem;
}

.form-panel {
  display: grid;
  gap: 0.8rem;
}

.quick-entry-panel {
  display: grid;
  gap: 0.65rem;
}

.quick-entry-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 0.7rem;
}

.quick-entry {
  border-radius: 0.75rem;
  border: 1px solid #cde1ec;
  background: #f4fbff;
  padding: 0.8rem 1rem;
  font-weight: 700;
  color: #145068;
  text-decoration: none;
  text-align: center;
}

.entry-hint {
  margin: 0;
  color: #557789;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(240px, 1fr));
  gap: 0.8rem;
}

label {
  display: grid;
  gap: 0.35rem;
  color: #1d5166;
  font-weight: 600;
}

input,
select,
textarea {
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  padding: 0.55rem 0.65rem;
  font: inherit;
}

.block {
  display: grid;
}

.check-row {
  align-content: center;
}

.product-list {
  display: grid;
  gap: 0.8rem;
}

.product-card {
  border: 1px solid #deebf2;
  border-radius: 0.8rem;
  padding: 0.8rem;
  display: grid;
  grid-template-columns: 96px 1fr auto;
  gap: 0.8rem;
  align-items: center;
}

.product-card img {
  width: 96px;
  height: 96px;
  border-radius: 0.6rem;
  object-fit: cover;
  background: #eff7fb;
}

.meta h3 {
  margin: 0;
  color: #103f50;
}

.meta p {
  margin: 0.2rem 0;
  color: #275063;
}

.subtitle {
  color: #557789;
}

.actions {
  display: grid;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 0.6rem;
}

.status-up {
  color: #176130;
  font-weight: 700;
}

.status-down {
  color: #8e3026;
  font-weight: 700;
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

.btn-danger {
  border: none;
  border-radius: 0.7rem;
  padding: 0.62rem 0.9rem;
  background: #b44337;
  color: #fff;
  cursor: pointer;
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-danger:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.login-required {
  border-radius: 0.8rem;
  background: #fff;
  border: 1px solid #d4e6f0;
  padding: 1rem;
  display: grid;
  gap: 0.8rem;
  justify-items: start;
}

@media (max-width: 860px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .quick-entry-grid {
    grid-template-columns: 1fr;
  }

  .product-card {
    grid-template-columns: 1fr;
  }

  .product-card img {
    width: 100%;
    max-width: 280px;
    height: auto;
  }
}
</style>
