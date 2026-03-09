<script setup lang="ts">
import { computed, onMounted, ref, reactive } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { getMe, login } from '@/services/user-center'

const ACCESS_TOKEN_KEY = 'mall_access_token'
const REFRESH_TOKEN_KEY = 'mall_refresh_token'
const USERNAME_KEY = 'mall_username'

const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY) || '')
const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
const username = ref(localStorage.getItem(USERNAME_KEY) || '')
const authError = ref('')
const authLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const isLoggedIn = computed(() => Boolean(accessToken.value))

function setTokens(access: string, refresh: string, user: string) {
  accessToken.value = access
  refreshToken.value = refresh
  username.value = user
  localStorage.setItem(ACCESS_TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  localStorage.setItem(USERNAME_KEY, user)
}

function clearTokens() {
  accessToken.value = ''
  refreshToken.value = ''
  username.value = ''
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
}

async function hydrateUser() {
  if (!accessToken.value) {
    return
  }
  try {
    const user = await getMe(accessToken.value)
    username.value = user.username
    localStorage.setItem(USERNAME_KEY, user.username)
  } catch {
    clearTokens()
  }
}

async function submitLogin() {
  authError.value = ''
  authLoading.value = true
  try {
    const payload = await login(loginForm)
    setTokens(payload.access, payload.refresh, payload.user.username)
    loginForm.password = ''
  } catch (error) {
    authError.value = error instanceof Error ? error.message : '登录失败'
  } finally {
    authLoading.value = false
  }
}

function logout() {
  clearTokens()
  loginForm.username = ''
  loginForm.password = ''
}

onMounted(() => {
  void hydrateUser()
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
      </nav>
      <div class="auth-block">
        <p v-if="isLoggedIn" class="welcome">欢迎，{{ username || '已登录用户' }}</p>
        <form v-else class="mini-login" @submit.prevent="submitLogin">
          <input v-model="loginForm.username" placeholder="用户名" required />
          <input v-model="loginForm.password" type="password" placeholder="密码" required />
          <button type="submit" :disabled="authLoading">{{ authLoading ? '登录中' : '登录' }}</button>
        </form>
        <RouterLink v-if="!isLoggedIn" class="register-link" to="/register">注册</RouterLink>
        <button v-if="isLoggedIn" class="ghost-btn" type="button" @click="logout">退出</button>
      </div>
    </header>

    <p v-if="authError" class="auth-error">{{ authError }}</p>

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

.mini-login {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.mini-login input {
  width: 7rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  padding: 0.45rem 0.55rem;
}

.mini-login button,
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

.auth-error {
  margin: 0;
  padding: 0.45rem 1.5rem;
  color: #8e3026;
  background: #ffe8e3;
}

.content-wrap {
  width: min(1120px, 94vw);
  margin: 1.5rem auto 2rem;
}

@media (max-width: 860px) {
  .topbar {
    align-items: flex-start;
  }

  .auth-block,
  .mini-login {
    width: 100%;
    flex-wrap: wrap;
  }

  .mini-login input {
    flex: 1;
    min-width: 8.5rem;
  }
}
</style>
