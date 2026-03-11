<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { login } from '@/services/user-center'
import { getAuthState, setAuthSession } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

const isLoggedIn = computed(() => Boolean(getAuthState().accessToken))

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const payload = await login(form)
    setAuthSession(payload.access, payload.refresh, payload.user.username)
    form.password = ''
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/home'
    await router.push(redirect)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1>账号登录</h1>

      <p v-if="isLoggedIn" class="already-login">
        当前已登录，可直接前往 <RouterLink to="/user-center">用户中心</RouterLink>
      </p>

      <p v-if="error" class="alert alert-error">{{ error }}</p>

      <form class="login-form" @submit.prevent="handleLogin">
        <label>
          用户名
          <input v-model="form.username" type="text" placeholder="请输入用户名" required />
        </label>
        <label>
          密码
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </label>
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="register-tip">
        还没有账号？<RouterLink to="/register">立即注册</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 70vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.login-card {
  width: min(440px, 100%);
  border-radius: 1rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid #d4e6f0;
  box-shadow: 0 16px 36px rgba(16, 63, 80, 0.12);
}

h1 {
  margin: 0 0 1rem;
  color: #103f50;
}

.already-login {
  margin: 0 0 1rem;
  color: #1d5166;
}

.already-login a,
.register-tip a {
  color: #0c6f57;
  font-weight: 700;
  text-decoration: none;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  color: #1d5166;
  font-weight: 600;
}

.login-form input {
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  padding: 0.7rem 0.75rem;
}

.btn-login {
  margin-top: 0.4rem;
  border: none;
  border-radius: 0.7rem;
  padding: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  color: #fff;
  background: linear-gradient(120deg, #1f9f78, #1179a1);
}

.btn-login:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.alert {
  margin: 0 0 1rem;
  padding: 0.75rem;
  border-radius: 0.6rem;
}

.alert-error {
  background: #ffe8e3;
  color: #8e3026;
}

.register-tip {
  margin: 1rem 0 0;
  color: #1d5166;
}
</style>