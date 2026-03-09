<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import type { AddressItem, AddressForm } from '@/types/user-center'
import {
  getAddresses,
  createAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress,
} from '@/services/user-center'

const accessToken = ref(localStorage.getItem('mall_access_token') || '')

const addresses = ref<AddressItem[]>([])
const loading = ref(false)
const error = ref('')
const showForm = ref(false)
const editingId = ref<number | null>(null)

const form = reactive<AddressForm>({
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  is_default: false,
})

const formError = ref('')
const formLoading = ref(false)

async function loadAddresses() {
  loading.value = true
  error.value = ''
  try {
    addresses.value = await getAddresses(accessToken.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载地址失败'
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.phone = ''
  form.province = ''
  form.city = ''
  form.district = ''
  form.detail = ''
  form.is_default = false
  editingId.value = null
  formError.value = ''
}

function openCreateForm() {
  resetForm()
  showForm.value = true
}

function openEditForm(address: AddressItem) {
  form.name = address.name
  form.phone = address.phone
  form.province = address.province
  form.city = address.city
  form.district = address.district
  form.detail = address.detail
  form.is_default = address.is_default
  editingId.value = address.id
  showForm.value = true
}

async function handleSubmit() {
  formError.value = ''

  if (!form.name.trim()) {
    formError.value = '收货人名字不能为空'
    return
  }
  if (!form.phone.trim()) {
    formError.value = '电话号码不能为空'
    return
  }
  if (!form.province.trim() || !form.city.trim() || !form.district.trim()) {
    formError.value = '省市区不能为空'
    return
  }
  if (!form.detail.trim()) {
    formError.value = '详细地址不能为空'
    return
  }

  formLoading.value = true
  try {
    if (editingId.value === null) {
      // 创建新地址
      await createAddress(form, accessToken.value)
    } else {
      // 更新地址
      await updateAddress(editingId.value, form, accessToken.value)
    }
    showForm.value = false
    resetForm()
    await loadAddresses()
  } catch (err) {
    formError.value = err instanceof Error ? err.message : '操作失败'
  } finally {
    formLoading.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除这个地址吗？')) {
    return
  }
  try {
    await deleteAddress(id, accessToken.value)
    await loadAddresses()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
  }
}

async function handleSetDefault(id: number) {
  try {
    await setDefaultAddress(id, accessToken.value)
    await loadAddresses()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '设置默认地址失败'
  }
}

onMounted(() => {
  void loadAddresses()
})
</script>

<template>
  <div class="address-management">
    <h1>收货地址管理</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <button v-if="!showForm" class="btn-primary" @click="openCreateForm">新增地址</button>

    <!-- Add/Edit Form -->
    <div v-if="showForm" class="form-container">
      <h2>{{ editingId ? '编辑地址' : '新增地址' }}</h2>
      <div v-if="formError" class="alert alert-error">{{ formError }}</div>

      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <div class="form-group">
            <label>收货人</label>
            <input v-model="form.name" type="text" placeholder="收货人名字" />
          </div>
          <div class="form-group">
            <label>电话</label>
            <input v-model="form.phone" type="text" placeholder="电话号码" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>省份</label>
            <input v-model="form.province" type="text" placeholder="省份" />
          </div>
          <div class="form-group">
            <label>城市</label>
            <input v-model="form.city" type="text" placeholder="城市" />
          </div>
          <div class="form-group">
            <label>区县</label>
            <input v-model="form.district" type="text" placeholder="区县" />
          </div>
        </div>

        <div class="form-group full-width">
          <label>详细地址</label>
          <input v-model="form.detail" type="text" placeholder="详细地址" />
        </div>

        <div class="form-group checkbox">
          <input id="is_default" v-model="form.is_default" type="checkbox" />
          <label for="is_default">设为默认地址</label>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="formLoading">
            {{ formLoading ? '保存中...' : '保存' }}
          </button>
          <button
            type="button"
            class="btn-secondary"
            @click="() => (showForm = false)"
            :disabled="formLoading"
          >
            取消
          </button>
        </div>
      </form>
    </div>

    <!-- Address List -->
    <div v-if="!showForm" class="address-list">
      <div v-if="loading" class="spinner">加载中...</div>
      <div v-else-if="addresses.length === 0" class="no-data">暂无地址，请创建一个</div>
      <div v-else class="address-cards">
        <div v-for="address in addresses" :key="address.id" class="address-card">
          <div class="address-header">
            <div class="address-name">{{ address.name }} {{ address.phone }}</div>
            <div v-if="address.is_default" class="default-badge">默认地址</div>
          </div>
          <div class="address-content">
            <p>
              {{ address.province }} {{ address.city }} {{ address.district }}
            </p>
            <p>{{ address.detail }}</p>
          </div>
          <div class="address-actions">
            <button
              v-if="!address.is_default"
              class="btn-link"
              @click="handleSetDefault(address.id)"
            >
              设为默认
            </button>
            <button class="btn-link" @click="openEditForm(address)">编辑</button>
            <button class="btn-link btn-danger" @click="handleDelete(address.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.address-management {
  max-width: 900px;
}

h1 {
  color: #103f50;
  margin-bottom: 1.5rem;
}

h2 {
  color: #1d5166;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
}

.btn-primary {
  background: #1f9f78;
  color: white;
  margin-bottom: 2rem;
}

.btn-primary:hover:not(:disabled) {
  background: #0c6f57;
}

.btn-secondary {
  background: #bbb;
  color: white;
  margin-left: 0.5rem;
}

.btn-secondary:hover:not(:disabled) {
  background: #999;
}

.form-container {
  background: white;
  padding: 1.5rem;
  border-radius: 0.8rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 0.3rem;
  font-weight: 600;
  color: #1d5166;
  font-size: 0.9rem;
}

.form-group input[type='text'],
.form-group input[type='email'],
.form-group input[type='number'] {
  padding: 0.6rem;
  border: 1px solid #b6cfdc;
  border-radius: 0.4rem;
  font-size: 0.9rem;
}

.form-group input[type='text']:focus,
.form-group input[type='email']:focus,
.form-group input[type='number']:focus {
  outline: none;
  border-color: #1f9f78;
}

.form-group.checkbox {
  flex-direction: row;
  align-items: center;
}

.form-group.checkbox input {
  margin-right: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 0.6rem;
  margin-bottom: 1rem;
}

.alert-error {
  background: #ffe8e3;
  color: #8e3026;
}

.address-list {
  margin-top: 2rem;
}

.address-cards {
  display: grid;
  gap: 1rem;
}

.address-card {
  background: white;
  border: 1px solid #d4e6f0;
  border-radius: 0.8rem;
  padding: 1.2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.address-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.address-name {
  font-weight: 600;
  color: #1d5166;
  font-size: 1rem;
}

.default-badge {
  background: #1f9f78;
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 0.3rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.address-content p {
  margin: 0.3rem 0;
  color: #555;
  font-size: 0.9rem;
}

.address-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  border-top: 1px solid #e0e0e0;
  padding-top: 1rem;
}

.btn-link {
  background: none;
  border: none;
  color: #1f9f78;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 0;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-link.btn-danger {
  color: #d32f2f;
}

.no-data,
.spinner {
  text-align: center;
  padding: 2rem;
  color: #999;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
