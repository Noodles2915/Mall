<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { getMe } from '@/services/user-center'
import { clearAuthSession, getAuthState, onAuthChanged } from '@/utils/auth'

const accessToken = ref('')
const refreshToken = ref('')
const username = ref('')
const userRole = ref('')
let stopAuthListener: (() => void) | null = null

const isLoggedIn = computed(() => Boolean(accessToken.value))
const canManageMerchantProducts = computed(
  () => userRole.value === 'admin' || userRole.value === 'merchant',
)

function syncAuthState() {
  const state = getAuthState()
  accessToken.value = state.accessToken
  refreshToken.value = state.refreshToken
  username.value = state.username
  if (!state.accessToken) {
    userRole.value = ''
  }
}

async function hydrateUser() {
  if (!accessToken.value) {
    return
  }
  try {
    const user = await getMe(accessToken.value)
    username.value = user.username
    userRole.value = user.role || ''
    localStorage.setItem('mall_username', user.username)
  } catch {
    clearAuthSession()
    syncAuthState()
  }
}

function logout() {
  clearAuthSession()
  syncAuthState()
}

onMounted(() => {
  syncAuthState()
  stopAuthListener = onAuthChanged(syncAuthState)
  void hydrateUser()
})

onBeforeUnmount(() => {
  stopAuthListener?.()
  stopAuthListener = null
})
</script>

<template>
  <div class="shell">
    <header class="topbar">
      <RouterLink class="brand" to="/home">Mall Showcase</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/home">首页</RouterLink>
        <RouterLink to="/products">商品列表</RouterLink>
        <RouterLink v-show="isLoggedIn" to="/cart">购物车</RouterLink>
        <RouterLink v-show="isLoggedIn" to="/orders">订单</RouterLink>
        <RouterLink v-show="isLoggedIn" to="/addresses">地址</RouterLink>
        <RouterLink v-show="canManageMerchantProducts" to="/merchant/products">商家上架</RouterLink>
        <RouterLink v-show="canManageMerchantProducts" to="/merchant/shipping">商家订单</RouterLink>
        <RouterLink v-show="canManageMerchantProducts" to="/merchant/service-messages">商家客服</RouterLink>
        <RouterLink v-show="isLoggedIn" to="/user-center">用户中心</RouterLink>
      </nav>
      <div class="auth-block">
        <p v-if="isLoggedIn" class="welcome">欢迎，{{ username || '已登录用户' }}</p>
        <RouterLink v-if="!isLoggedIn" class="auth-link" to="/login">登录</RouterLink>
        <RouterLink v-if="!isLoggedIn" class="register-link" to="/register">注册</RouterLink>
        <RouterLink v-if="isLoggedIn" class="auth-link" to="/user-center">个人中心</RouterLink>
        <button v-if="isLoggedIn" class="ghost-btn" type="button" @click="logout">退出</button>
      </div>
    </header>

    <main class="content-wrap">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  color: #1b2a2f;
  background:
    radial-gradient(circle at 10% 10%, #fff6d7 0%, transparent 45%),
    radial-gradient(circle at 90% 20%, #dbf7f0 0%, transparent 50%),
    linear-gradient(165deg, #fffef8 0%, #f4fbff 100%);
  font-family: 'Trebuchet MS', 'Segoe UI', Tahoma, sans-serif;
}

.topbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #d4e6f0;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(8px);
}

.brand {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: #103f50;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  text-decoration: none;
  color: #1d5166;
  font-weight: 600;
}

.nav-links a.router-link-active {
  color: #0c6f57;
}

.auth-block {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.auth-link,
.ghost-btn,
.register-link {
  border: none;
  border-radius: 0.6rem;
  padding: 0.45rem 0.7rem;
  background: #1f9f78;
  color: #fff;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.auth-link {
  background: #1f9f78;
}

.ghost-btn {
  background: #5f6f78;
}

.register-link {
  background: #0c6f57;
}

.welcome {
  margin: 0;
  font-size: 0.9rem;
  color: #1d5166;
}

.content-wrap {
  width: min(1120px, 94vw);
  margin: 1.5rem auto 2rem;
}

@media (max-width: 860px) {
  .topbar {
    align-items: flex-start;
  }

  .auth-block {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
