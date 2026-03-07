<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createAddress,
  deleteAddress,
  getAddresses,
  getMe,
  login,
  register,
  setDefaultAddress,
  updateAddress,
  updateMe,
} from '@/services/user-center'
import type { AddressForm, AddressItem, UserProfile } from '@/types/user-center'

type AuthMode = 'login' | 'register'

const ACCESS_TOKEN_KEY = 'mall_access_token'
const REFRESH_TOKEN_KEY = 'mall_refresh_token'

const authMode = ref<AuthMode>('login')
const loading = ref(false)
const profileSaving = ref(false)
const addressSaving = ref(false)
const addressLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY) || '')
const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || '')

const user = ref<UserProfile | null>(null)
const addresses = ref<AddressItem[]>([])
const editingAddressId = ref<number | null>(null)

const loginForm = reactive({
  username: '',
  password: '',
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
})

const profileForm = reactive({
  username: '',
  email: '',
  avatar: '',
})

const emptyAddressForm = (): AddressForm => ({
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  is_default: false,
})

const addressForm = reactive<AddressForm>(emptyAddressForm())

const isLoggedIn = computed(() => Boolean(accessToken.value && user.value))

function setTokens(access: string, refresh: string) {
  accessToken.value = access
  refreshToken.value = refresh
  localStorage.setItem(ACCESS_TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

function clearTokens() {
  accessToken.value = ''
  refreshToken.value = ''
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

function setProfileForm(data: UserProfile) {
  profileForm.username = data.username || ''
  profileForm.email = data.email || ''
  profileForm.avatar = data.avatar || ''
}

function resetAddressForm() {
  Object.assign(addressForm, emptyAddressForm())
  editingAddressId.value = null
}

function clearStatus() {
  errorMessage.value = ''
  successMessage.value = ''
}

function handleError(error: unknown) {
  if (error instanceof Error) {
    errorMessage.value = error.message
    return
  }
  errorMessage.value = '发生未知错误，请稍后重试'
}

async function loadCurrentUser() {
  if (!accessToken.value) {
    return
  }
  const profile = await getMe(accessToken.value)
  user.value = profile
  setProfileForm(profile)
}

async function loadAddressList() {
  if (!accessToken.value) {
    return
  }
  addressLoading.value = true
  try {
    addresses.value = await getAddresses(accessToken.value)
  } finally {
    addressLoading.value = false
  }
}

async function initUserCenter() {
  if (!accessToken.value) {
    return
  }
  try {
    await loadCurrentUser()
    await loadAddressList()
  } catch (error) {
    clearTokens()
    user.value = null
    addresses.value = []
    handleError(error)
  }
}

async function submitAuth() {
  clearStatus()
  loading.value = true
  try {
    if (authMode.value === 'login') {
      const payload = await login(loginForm)
      setTokens(payload.access, payload.refresh)
      user.value = payload.user
      setProfileForm(payload.user)
      await loadAddressList()
      successMessage.value = '登录成功'
    } else {
      const payload = await register(registerForm)
      setTokens(payload.access, payload.refresh)
      user.value = payload.user
      setProfileForm(payload.user)
      await loadAddressList()
      successMessage.value = '注册成功，已自动登录'
    }
  } catch (error) {
    handleError(error)
  } finally {
    loading.value = false
  }
}

async function submitProfileUpdate() {
  if (!accessToken.value) {
    return
  }
  clearStatus()
  profileSaving.value = true
  try {
    const profile = await updateMe(
      {
        username: profileForm.username,
        email: profileForm.email,
        avatar: profileForm.avatar,
      },
      accessToken.value,
    )
    user.value = profile
    setProfileForm(profile)
    successMessage.value = '用户信息已更新'
  } catch (error) {
    handleError(error)
  } finally {
    profileSaving.value = false
  }
}

function editAddress(item: AddressItem) {
  editingAddressId.value = item.id
  addressForm.name = item.name
  addressForm.phone = item.phone
  addressForm.province = item.province
  addressForm.city = item.city
  addressForm.district = item.district
  addressForm.detail = item.detail
  addressForm.is_default = item.is_default
}

async function submitAddress() {
  if (!accessToken.value) {
    return
  }
  clearStatus()
  addressSaving.value = true
  try {
    if (editingAddressId.value !== null) {
      await updateAddress(editingAddressId.value, addressForm, accessToken.value)
      successMessage.value = '地址已更新'
    } else {
      await createAddress(addressForm, accessToken.value)
      successMessage.value = '地址已创建'
    }
    resetAddressForm()
    await loadAddressList()
  } catch (error) {
    handleError(error)
  } finally {
    addressSaving.value = false
  }
}

async function removeAddress(id: number) {
  if (!accessToken.value) {
    return
  }
  clearStatus()
  try {
    await deleteAddress(id, accessToken.value)
    successMessage.value = '地址已删除'
    await loadAddressList()
  } catch (error) {
    handleError(error)
  }
}

async function markDefaultAddress(id: number) {
  if (!accessToken.value) {
    return
  }
  clearStatus()
  try {
    await setDefaultAddress(id, accessToken.value)
    successMessage.value = '默认地址已更新'
    await loadAddressList()
  } catch (error) {
    handleError(error)
  }
}

function logout() {
  clearTokens()
  user.value = null
  addresses.value = []
  resetAddressForm()
  clearStatus()
  successMessage.value = '您已退出登录'
}

onMounted(() => {
  void initUserCenter()
})
</script>

<template>
  <main class="page">
    <section class="hero">
      <p class="hero-kicker">Mall User Center</p>
      <h1>用户中心</h1>
      <p class="hero-subtitle">完成注册登录、个人资料维护，以及完整收货地址管理流程。</p>
    </section>

    <p v-if="errorMessage" class="notice notice-error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="notice notice-success">{{ successMessage }}</p>

    <section v-if="!isLoggedIn" class="panel auth-panel">
      <div class="tab-row">
        <button
          class="tab-btn"
          :class="{ active: authMode === 'login' }"
          type="button"
          @click="authMode = 'login'"
        >
          登录
        </button>
        <button
          class="tab-btn"
          :class="{ active: authMode === 'register' }"
          type="button"
          @click="authMode = 'register'"
        >
          注册
        </button>
      </div>

      <form class="grid-form" @submit.prevent="submitAuth">
        <label>
          <span>用户名</span>
          <input v-if="authMode === 'login'" v-model.trim="loginForm.username" required />
          <input v-else v-model.trim="registerForm.username" required />
        </label>

        <label v-if="authMode === 'register'">
          <span>邮箱</span>
          <input v-model.trim="registerForm.email" type="email" required />
        </label>

        <label>
          <span>密码</span>
          <input v-if="authMode === 'login'" v-model.trim="loginForm.password" type="password" required />
          <input v-else v-model.trim="registerForm.password" type="password" required />
        </label>

        <button class="primary-btn" type="submit" :disabled="loading">
          {{ loading ? '提交中...' : authMode === 'login' ? '立即登录' : '注册并登录' }}
        </button>
      </form>
    </section>

    <template v-else>
      <section class="panel user-bar">
        <div>
          <p class="label">当前用户</p>
          <h2>{{ user?.username }}</h2>
          <p>{{ user?.email }}</p>
        </div>
        <button class="ghost-btn" type="button" @click="logout">退出登录</button>
      </section>

      <section class="panel">
        <h3>个人资料</h3>
        <form class="grid-form" @submit.prevent="submitProfileUpdate">
          <label>
            <span>用户名</span>
            <input v-model.trim="profileForm.username" required />
          </label>
          <label>
            <span>邮箱</span>
            <input v-model.trim="profileForm.email" type="email" required />
          </label>
          <label>
            <span>头像 URL</span>
            <input v-model.trim="profileForm.avatar" placeholder="https://example.com/avatar.png" />
          </label>
          <button class="primary-btn" type="submit" :disabled="profileSaving">
            {{ profileSaving ? '保存中...' : '更新资料' }}
          </button>
        </form>
      </section>

      <section class="panel">
        <div class="panel-head">
          <h3>收货地址管理</h3>
          <button class="ghost-btn" type="button" @click="resetAddressForm">新建地址</button>
        </div>

        <form class="grid-form address-form" @submit.prevent="submitAddress">
          <label>
            <span>收货人</span>
            <input v-model.trim="addressForm.name" required />
          </label>
          <label>
            <span>手机号</span>
            <input v-model.trim="addressForm.phone" required />
          </label>
          <label>
            <span>省份</span>
            <input v-model.trim="addressForm.province" required />
          </label>
          <label>
            <span>城市</span>
            <input v-model.trim="addressForm.city" required />
          </label>
          <label>
            <span>区/县</span>
            <input v-model.trim="addressForm.district" required />
          </label>
          <label class="full-row">
            <span>详细地址</span>
            <input v-model.trim="addressForm.detail" required />
          </label>
          <label class="checkbox-line full-row">
            <input v-model="addressForm.is_default" type="checkbox" />
            <span>设为默认地址</span>
          </label>
          <button class="primary-btn" type="submit" :disabled="addressSaving">
            {{ addressSaving ? '保存中...' : editingAddressId !== null ? '更新地址' : '新增地址' }}
          </button>
        </form>

        <div v-if="addressLoading" class="empty">地址加载中...</div>
        <ul v-else-if="addresses.length" class="address-list">
          <li v-for="item in addresses" :key="item.id" class="address-item">
            <div>
              <p class="address-line">
                <strong>{{ item.name }}</strong>
                <span>{{ item.phone }}</span>
                <span v-if="item.is_default" class="default-tag">默认</span>
              </p>
              <p>{{ item.province }} {{ item.city }} {{ item.district }} {{ item.detail }}</p>
            </div>
            <div class="action-row">
              <button class="inline-btn" type="button" @click="editAddress(item)">编辑</button>
              <button class="inline-btn" type="button" @click="markDefaultAddress(item.id)">设为默认</button>
              <button class="inline-btn danger" type="button" @click="removeAddress(item.id)">删除</button>
            </div>
          </li>
        </ul>
        <div v-else class="empty">还没有收货地址，先创建一个吧。</div>
      </section>
    </template>
  </main>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Chivo:wght@400;700;900&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
  font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif;
  color: #1f2328;
  background: #f6f0e8;
  line-height: 1.4;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at 90% 10%, rgba(255, 146, 84, 0.2), transparent 35%),
    radial-gradient(circle at 8% 92%, rgba(57, 125, 255, 0.2), transparent 35%),
    linear-gradient(130deg, #fef7ee, #f7efe7 45%, #f6f4ff);
}

#app {
  min-height: 100vh;
}

.page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 32px 16px 56px;
}

.hero {
  margin-bottom: 16px;
}

.hero-kicker {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: #cb5f2f;
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
}

.hero h1 {
  font-family: 'Chivo', 'IBM Plex Sans', sans-serif;
  margin: 0;
  font-size: clamp(32px, 5vw, 48px);
  line-height: 1.05;
}

.hero-subtitle {
  margin: 8px 0 0;
  color: #485164;
  max-width: 640px;
}

.notice {
  border-radius: 12px;
  padding: 10px 14px;
  margin: 12px 0;
  font-size: 14px;
}

.notice-error {
  background: #ffe4e3;
  color: #8d1f1f;
}

.notice-success {
  background: #def6e5;
  color: #155b37;
}

.panel {
  border: 1px solid #d8d7d3;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(4px);
  border-radius: 18px;
  padding: 18px;
  margin-top: 16px;
  box-shadow: 0 12px 28px rgba(45, 52, 71, 0.08);
}

.auth-panel {
  max-width: 520px;
}

.tab-row {
  display: inline-grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4px;
  background: #ece8e2;
  border-radius: 999px;
  padding: 4px;
}

.tab-btn {
  border: 0;
  border-radius: 999px;
  padding: 8px 18px;
  font-weight: 600;
  background: transparent;
  cursor: pointer;
}

.tab-btn.active {
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(37, 38, 45, 0.16);
}

.grid-form {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

label {
  display: grid;
  gap: 6px;
}

label span {
  font-size: 13px;
  color: #5f6775;
}

input {
  border: 1px solid #c8ced8;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 15px;
  background: #fff;
}

input:focus {
  border-color: #2b67f6;
  outline: 2px solid rgba(43, 103, 246, 0.16);
}

.primary-btn,
.ghost-btn,
.inline-btn {
  border-radius: 10px;
  border: 0;
  padding: 9px 14px;
  font-size: 14px;
  cursor: pointer;
}

.primary-btn {
  background: #1b3f9b;
  color: #fff;
  font-weight: 600;
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ghost-btn {
  background: #eceff8;
  color: #1a2f67;
}

.user-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.label {
  margin: 0;
  color: #747b8a;
  font-size: 13px;
}

.user-bar h2 {
  margin: 4px 0;
}

.user-bar p {
  margin: 0;
}

.panel h3 {
  margin: 0;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.address-form {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.full-row {
  grid-column: 1 / -1;
}

.checkbox-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-line input {
  width: 16px;
  height: 16px;
  margin: 0;
}

.address-list {
  list-style: none;
  margin: 16px 0 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.address-item {
  border: 1px solid #d7dce6;
  border-radius: 12px;
  padding: 12px;
  background: #fdfdfd;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.address-line {
  margin: 0 0 6px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.address-item p {
  margin: 0;
}

.default-tag {
  background: #ffc861;
  color: #6e3b02;
  font-size: 12px;
  border-radius: 999px;
  padding: 2px 8px;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.inline-btn {
  background: #edf2ff;
  color: #1e3e87;
}

.inline-btn.danger {
  background: #ffe8e8;
  color: #8f2323;
}

.empty {
  margin-top: 14px;
  color: #6b7281;
}

@media (max-width: 768px) {
  .address-form {
    grid-template-columns: 1fr;
  }

  .address-item,
  .user-bar,
  .panel-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
