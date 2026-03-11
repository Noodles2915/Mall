<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import type { ProductBanner, ProductBase } from '@/types/product-center'
import { getHomeData } from '@/services/product-center'

interface HomeLoadingStates {
  banners: boolean
  hotProducts: boolean
}

const loading = ref<HomeLoadingStates>({ banners: false, hotProducts: false })
const error = ref('')
const banners = ref<ProductBanner[]>([])
const hotProducts = ref<ProductBase[]>([])
const currentBannerIndex = ref(0)

const totalBanners = computed(() => banners.value.length)
const currentBanner = computed(() => banners.value[currentBannerIndex.value] || null)

async function loadHomeData() {
  error.value = ''
  loading.value.banners = true
  loading.value.hotProducts = true
  try {
    const data = await getHomeData()
    banners.value = data.banners.sort((a, b) => a.sort - b.sort)
    hotProducts.value = data.hot_products
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载首页数据失败'
  } finally {
    loading.value.banners = false
    loading.value.hotProducts = false
  }
}

function goToNextBanner() {
  currentBannerIndex.value = (currentBannerIndex.value + 1) % totalBanners.value
}

function goToPrevBanner() {
  currentBannerIndex.value = (currentBannerIndex.value - 1 + totalBanners.value) % totalBanners.value
}

function selectBanner(index: number) {
  currentBannerIndex.value = index
}

onMounted(() => {
  void loadHomeData()
})
</script>

<template>
  <div class="home">
    <p v-if="error" class="error-banner">{{ error }}</p>

    <!-- Carousel / Banners Section -->
    <section class="carousel-section">
      <div v-if="loading.banners" class="spinner">加载轮播图中...</div>
      <div v-else-if="currentBanner" class="carousel">
        <RouterLink
          :to="currentBanner.link"
          class="carousel-main"
          :style="{ backgroundImage: `url(${currentBanner.image_url})` }"
        >
          <div class="carousel-label">{{ currentBanner.title }}</div>
        </RouterLink>

        <div class="carousel-controls">
          <button class="nav-btn prev-btn" type="button" @click="goToPrevBanner">❮</button>
          <button class="nav-btn next-btn" type="button" @click="goToNextBanner">❯</button>
        </div>

        <div class="carousel-indicators">
          <button
            v-for="(_, index) in banners"
            :key="index"
            class="indicator"
            :class="{ active: index === currentBannerIndex }"
            type="button"
            @click="selectBanner(index)"
          />
        </div>
      </div>
      <div v-else class="no-data">暂无轮播图</div>
    </section>

    <!-- Hot Products Section -->
    <section class="hot-products-section">
      <h2>热门推荐</h2>
      <div v-if="loading.hotProducts" class="spinner">加载商品中...</div>
      <div v-else-if="hotProducts.length > 0" class="products-grid">
        <RouterLink
          v-for="product in hotProducts"
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
      <div v-else class="no-data">暂无商品</div>
    </section>
  </div>
</template>

<style scoped>
.home {
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

/* Carousel Section */
.carousel-section {
  margin-bottom: 3rem;
}

.carousel {
  position: relative;
  width: 100%;
  height: 350px;
  border-radius: 0.8rem;
  overflow: hidden;
  background: #f0f0f0;
}

.carousel-main {
  display: block;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease;
}

.carousel-main:hover {
  transform: scale(1.02);
}

.carousel-label {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.4rem;
  font-size: 0.95rem;
  font-weight: 600;
}

.carousel-controls {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  padding: 0 1rem;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.7);
  border: none;
  border-radius: 50%;
  width: 2.5rem;
  height: 2.5rem;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 1);
}

.carousel-indicators {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.5rem;
}

.indicator {
  width: 0.6rem;
  height: 0.6rem;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: background 0.3s ease;
}

.indicator.active {
  background: rgba(255, 255, 255, 1);
}

/* Hot Products Section */
.hot-products-section {
  margin: 3rem 0;
}

.hot-products-section h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  color: #103f50;
  font-weight: 700;
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

/* Spinner & No Data */
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
  .carousel {
    height: 250px;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
