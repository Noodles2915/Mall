<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import type { ProductBase, Category } from '@/types/product-center'
import { getProducts, getCategories } from '@/services/product-center'

interface QueryState {
  keyword: string
  category: number | null
  isHot: boolean
}

const route = useRoute()

const loading = ref(false)
const error = ref('')
const products = ref<ProductBase[]>([])
const categories = ref<Category[]>([])
const categoriesLoading = ref(false)

const query = ref<QueryState>({
  keyword: (route.query.keyword as string) || '',
  category: route.query.category ? Number(route.query.category) : null,
  isHot: route.query.is_hot === 'true',
})

// Organize categories into a flat list with hierarchy info
const categoryListWithPath = computed(() => {
  const getPath = (id: number, cats: Category[]): string => {
    const cat = cats.find((c) => c.id === id)
    if (!cat) return ''
    if (cat.parent === null) return cat.name
    return `${getPath(cat.parent, cats)} > ${cat.name}`
  }

  return categories.value.map((cat) => ({
    ...cat,
    path: getPath(cat.id, categories.value),
  }))
})

async function loadCategories() {
  categoriesLoading.value = true
  try {
    categories.value = await getCategories()
  } catch (err) {
    console.error('加载分类失败:', err)
  } finally {
    categoriesLoading.value = false
  }
}

async function loadProducts() {
  error.value = ''
  loading.value = true
  try {
    products.value = await getProducts({
      keyword: query.value.keyword || undefined,
      category: query.value.category || undefined,
      is_hot: query.value.isHot ? true : undefined,
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载商品失败'
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  query.value = {
    keyword: '',
    category: null,
    isHot: false,
  }
}

function toggleHot() {
  query.value.isHot = !query.value.isHot
}

function selectCategory(catId: number | null) {
  query.value.category = query.value.category === catId ? null : catId
}

watch(query, () => {
  void loadProducts()
}, { deep: true })

onMounted(async () => {
  await loadCategories()
  await loadProducts()
})
</script>

<template>
  <div class="product-list">
    <!-- Error Banner -->
    <p v-if="error" class="error-banner">{{ error }}</p>

    <!-- Filters Section -->
    <section class="filters-section">
      <div class="filter-group">
        <input
          v-model="query.keyword"
          type="text"
          placeholder="搜索商品名称、副标题..."
          class="search-input"
        />
        <button class="search-btn" type="button">搜索</button>
      </div>

      <div class="filter-group">
        <label class="checkbox-label">
          <input v-model="query.isHot" type="checkbox" />
          <span>仅展示热门商品</span>
        </label>
      </div>

      <div class="filter-group categories-filter">
        <div class="category-label">分类：</div>
        <div class="category-list">
          <button
            type="button"
            class="category-btn"
            :class="{ active: query.category === null && (query.keyword || query.isHot) }"
            @click="selectCategory(null)"
          >
            全部
          </button>
          <button
            v-for="cat in categoryListWithPath"
            :key="cat.id"
            type="button"
            class="category-btn"
            :class="{ active: query.category === cat.id }"
            :title="cat.path"
            @click="selectCategory(cat.id)"
          >
            {{ cat.name }}
          </button>
        </div>
      </div>

      <button v-if="query.keyword || query.category || query.isHot" class="clear-btn" type="button" @click="clearFilters">
        清除筛选
      </button>
    </section>

    <!-- Results Info -->
    <div class="results-info">
      <span>搜索结果: {{ products.length }} 件商品</span>
    </div>

    <!-- Products Grid -->
    <section class="products-section">
      <div v-if="loading" class="spinner">加载商品中...</div>
      <div v-else-if="products.length > 0" class="products-grid">
        <RouterLink
          v-for="product in products"
          :key="product.id"
          :to="`/products/${product.id}`"
          class="product-card"
        >
          <div class="product-image">
            <img :src="product.cover_url" :alt="product.name" />
            <div v-if="product.is_hot" class="hot-badge">热売</div>
          </div>
          <div class="product-info">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-subtitle">{{ product.subtitle }}</p>
            <div class="product-meta">
              <span class="category">{{ product.category_name }}</span>
              <span class="sales">已售 {{ product.sales }}</span>
            </div>
            <div class="product-footer">
              <span class="price">¥{{ product.price }}</span>
              <span class="stock" :class="{ low: product.stock < 10 }">
                {{
                  product.stock > 0
                    ? `库存 ${product.stock}`
                    : '缺货'
                }}
              </span>
            </div>
          </div>
        </RouterLink>
      </div>
      <div v-else class="no-data">暂无匹配的商品</div>
    </section>
  </div>
</template>

<style scoped>
.product-list {
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

/* Filters Section */
.filters-section {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 0.8rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.filter-group:last-of-type {
  margin-bottom: 0;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 0.6rem 0.9rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  font-size: 0.9rem;
}

.search-btn {
  padding: 0.6rem 1.2rem;
  background: #1f9f78;
  color: white;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
}

.search-btn:hover {
  background: #16825f;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.checkbox-label input {
  cursor: pointer;
}

.categories-filter {
  flex-wrap: wrap;
  align-items: flex-start;
}

.category-label {
  font-weight: 600;
  color: #1b2a2f;
}

.category-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.category-btn {
  padding: 0.4rem 0.8rem;
  background: #f0f0f0;
  border: 1px solid #d4e6f0;
  border-radius: 0.4rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.category-btn:hover {
  background: #e8f1f7;
}

.category-btn.active {
  background: #1f9f78;
  color: white;
  border-color: #1f9f78;
}

.clear-btn {
  padding: 0.5rem 1rem;
  background: #999;
  color: white;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s ease;
}

.clear-btn:hover {
  background: #777;
}

/* Results Info */
.results-info {
  margin-bottom: 1rem;
  padding: 0 0.5rem;
  color: #999;
  font-size: 0.9rem;
}

/* Products Section */
.products-section {
  margin: 2rem 0;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  border-radius: 0.8rem;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  color: inherit;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.product-image {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.product-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hot-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #ff5550;
  color: white;
  padding: 0.25rem 0.6rem;
  border-radius: 0.3rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.product-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 1rem;
}

.product-name {
  margin: 0 0 0.5rem 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1b2a2f;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-subtitle {
  margin: 0 0 0.5rem 0;
  font-size: 0.8rem;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0 auto 0;
  font-size: 0.75rem;
  color: #999;
}

.category {
  background: #f0f0f0;
  padding: 0.2rem 0.5rem;
  border-radius: 0.2rem;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f0f0f0;
}

.price {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ff5550;
}

.stock {
  font-size: 0.75rem;
  color: #999;
}

.stock.low {
  color: #ff5550;
  font-weight: 600;
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

@media (max-width: 768px) {
  .filter-group {
    flex-wrap: wrap;
  }

  .search-input {
    min-width: 150px;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
