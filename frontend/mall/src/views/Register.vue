<script setup lang="ts">
import { onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { register, sendRegisterEmailCode } from '@/services/user-center'

const router = useRouter()

const form = reactive({
  username: '',
  email: '',
  emailCode: '',
  password: '',
  passwordConfirm: '',
})

const loading = ref(false)
const sendingCode = ref(false)
const codeCountdown = ref(0)
const error = ref('')
const success = ref('')
let codeTimer: ReturnType<typeof setInterval> | null = null

function clearCodeTimer() {
  if (codeTimer) {
    clearInterval(codeTimer)
    codeTimer = null
  }
}

function startCodeCountdown() {
  clearCodeTimer()
  codeCountdown.value = 60
  codeTimer = setInterval(() => {
    if (codeCountdown.value <= 1) {
      codeCountdown.value = 0
      clearCodeTimer()
      return
    }
    codeCountdown.value -= 1
  }, 1000)
}

async function handleSendEmailCode() {
  error.value = ''
  success.value = ''

  if (!form.email.trim()) {
    error.value = '请先输入邮箱'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    error.value = '邮箱格式不正确'
    return
  }
  if (codeCountdown.value > 0 || sendingCode.value) {
    return
  }

  sendingCode.value = true
  try {
    await sendRegisterEmailCode({ email: form.email })
    success.value = '验证码已发送，请查收邮箱'
    startCodeCountdown()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '验证码发送失败'
  } finally {
    sendingCode.value = false
  }
}

async function handleSubmit() {
  error.value = ''
  success.value = ''

  // 验证
  if (!form.username.trim()) {
    error.value = '用户名不能为空'
    return
  }
  if (!form.email.trim()) {
    error.value = '邮箱不能为空'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    error.value = '邮箱格式不正确'
    return
  }
  if (!form.password) {
    error.value = '密码不能为空'
    return
  }
  if (!form.emailCode.trim()) {
    error.value = '验证码不能为空'
    return
  }
  if (!/^\d{6}$/.test(form.emailCode.trim())) {
    error.value = '验证码应为6位数字'
    return
  }
  if (form.password.length < 6) {
    error.value = '密码长度至少为6个字符'
    return
  }
  if (form.password !== form.passwordConfirm) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    await register({
      username: form.username,
      email: form.email,
      password: form.password,
      email_code: form.emailCode.trim(),
    })
    success.value = '注册成功，正在跳转...'
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '注册失败'
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  clearCodeTimer()
})
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <h1>注册新账户</h1>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱地址"
            required
          />
        </div>

        <div class="form-group">
          <label for="emailCode">邮箱验证码</label>
          <div class="verification-row">
            <input
              id="emailCode"
              v-model="form.emailCode"
              type="text"
              maxlength="6"
              placeholder="请输入6位验证码"
              required
            />
            <button
              type="button"
              class="btn-secondary"
              :disabled="sendingCode || codeCountdown > 0"
              @click="handleSendEmailCode"
            >
              {{ codeCountdown > 0 ? `${codeCountdown}s后重发` : sendingCode ? '发送中...' : '发送验证码' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="请输入密码（至少6个字符）"
            required
          />
        </div>

        <div class="form-group">
          <label for="passwordConfirm">确认密码</label>
          <input
            id="passwordConfirm"
            v-model="form.passwordConfirm"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="login-link">
        已有账户？<RouterLink to="/login">前往登录</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.register-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 0.8rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #103f50;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #1d5166;
  font-weight: 600;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.6rem;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.verification-row {
  display: flex;
  gap: 0.75rem;
}

.verification-row input {
  flex: 1;
}

.btn-secondary {
  flex: 0 0 120px;
  border: 1px solid #1f9f78;
  background: #eefaf5;
  color: #0c6f57;
  border-radius: 0.6rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-group input:focus {
  outline: none;
  border-color: #1f9f78;
  box-shadow: 0 0 0 2px rgba(31, 159, 120, 0.1);
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 0.6rem;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.alert-error {
  background: #ffe8e3;
  color: #8e3026;
  border: 1px solid #ffb8a3;
}

.alert-success {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background: #1f9f78;
  color: white;
  border: none;
  border-radius: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #0c6f57;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #1d5166;
  font-size: 0.9rem;
}

.login-link a {
  color: #1f9f78;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
