<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  getMe,
  getQualificationApplications,
  submitQualificationApplication,
} from '@/services/user-center'
import type {
  QualificationApplicationItem,
  QualificationApplicationStatus,
} from '@/types/user-center'
import { getAuthState } from '@/utils/auth'

const accessToken = ref(getAuthState().accessToken)
const username = ref(getAuthState().username)
const profileEmail = ref('')
const profileError = ref('')
const applications = ref<QualificationApplicationItem[]>([])
const recordsLoading = ref(false)
const recordsError = ref('')

const loadingMerchant = ref(false)
const loadingStaff = ref(false)
const submitError = ref('')
const submitSuccess = ref('')

const form = reactive({
  merchantReason: '',
  staffReason: '',
})

const isLoggedIn = computed(() => Boolean(accessToken.value))

async function loadProfile() {
  if (!accessToken.value) {
    return
  }

  profileError.value = ''
  try {
    const profile = await getMe(accessToken.value)
    username.value = profile.username
    profileEmail.value = profile.email
  } catch (err) {
    profileError.value = err instanceof Error ? err.message : '加载用户信息失败'
  }
}

async function loadApplications() {
  if (!accessToken.value) {
    return
  }

  recordsLoading.value = true
  recordsError.value = ''
  try {
    applications.value = await getQualificationApplications(accessToken.value)
  } catch (err) {
    recordsError.value = err instanceof Error ? err.message : '加载资质申请列表失败'
  } finally {
    recordsLoading.value = false
  }
}

async function submitMerchant() {
  submitError.value = ''
  submitSuccess.value = ''

  if (!form.merchantReason.trim()) {
    submitError.value = '请填写商家资质申请说明'
    return
  }

  loadingMerchant.value = true
  try {
    await submitQualificationApplication({
      application_type: 'merchant',
      reason: form.merchantReason,
    }, accessToken.value)
    submitSuccess.value = '商家资质申请已提交，等待管理员审核'
    form.merchantReason = ''
    await loadApplications()
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : '提交商家资质申请失败'
  } finally {
    loadingMerchant.value = false
  }
}

async function submitStaff() {
  submitError.value = ''
  submitSuccess.value = ''

  if (!form.staffReason.trim()) {
    submitError.value = '请填写工作人员资质申请说明'
    return
  }

  loadingStaff.value = true
  try {
    await submitQualificationApplication({
      application_type: 'staff',
      reason: form.staffReason,
    }, accessToken.value)
    submitSuccess.value = '工作人员资质申请已提交，等待管理员审核'
    form.staffReason = ''
    await loadApplications()
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : '提交工作人员资质申请失败'
  } finally {
    loadingStaff.value = false
  }
}

function statusClass(status: QualificationApplicationStatus) {
  const map: Record<QualificationApplicationStatus, string> = {
    pending: 'status-pending',
    approved: 'status-approved',
    rejected: 'status-rejected',
  }
  return map[status]
}

function formatDate(value: string | null) {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  void loadProfile()
  void loadApplications()
})
</script>

<template>
  <div class="user-center">
    <h1>用户中心</h1>

    <div v-if="!isLoggedIn" class="login-required">
      <p>请先登录后使用用户中心功能。</p>
      <RouterLink class="btn-primary" to="/login">前往登录</RouterLink>
    </div>

    <template v-else>
      <section class="profile-panel">
        <h2>基本信息</h2>
        <p><strong>用户名：</strong>{{ username || '未获取' }}</p>
        <p><strong>邮箱：</strong>{{ profileEmail || '未设置' }}</p>
        <p v-if="profileError" class="error-text">{{ profileError }}</p>
      </section>

      <p v-if="submitError" class="alert alert-error">{{ submitError }}</p>
      <p v-if="submitSuccess" class="alert alert-success">{{ submitSuccess }}</p>

      <section class="qualification-grid">
        <article class="qualification-card">
          <h3>商家资质申请</h3>
          <p>用于开通商品发布、库存维护、订单发货等商家能力。</p>
          <textarea
            v-model="form.merchantReason"
            rows="4"
            placeholder="请说明你的经营范围、主营类目和联系方式"
          />
          <small class="hint">同一类型在待审核状态下只能提交一条申请。</small>
          <button class="btn-primary" type="button" :disabled="loadingMerchant" @click="submitMerchant">
            {{ loadingMerchant ? '提交中...' : '提交商家资质申请' }}
          </button>
        </article>

        <article class="qualification-card">
          <h3>工作人员资质申请</h3>
          <p>用于开通客服、运营、仓储等后台协作权限。</p>
          <textarea
            v-model="form.staffReason"
            rows="4"
            placeholder="请说明你的岗位职责、所属团队和联系方式"
          />
          <small class="hint">请填写真实岗位信息，便于管理员审核。</small>
          <button class="btn-primary" type="button" :disabled="loadingStaff" @click="submitStaff">
            {{ loadingStaff ? '提交中...' : '提交工作人员资质申请' }}
          </button>
        </article>
      </section>

      <section class="records-panel">
        <h2>我的资质申请</h2>
        <p v-if="recordsError" class="error-text">{{ recordsError }}</p>
        <p v-if="recordsLoading">加载申请记录中...</p>
        <p v-else-if="applications.length === 0" class="empty-text">暂无申请记录</p>
        <ul v-else class="records-list">
          <li v-for="item in applications" :key="item.id" class="record-item">
            <div class="record-head">
              <strong>{{ item.application_type_display }}</strong>
              <span class="status-tag" :class="statusClass(item.status)">{{ item.status_display }}</span>
            </div>
            <p class="record-reason">申请说明：{{ item.reason }}</p>
            <p class="record-meta">提交时间：{{ formatDate(item.created_at) }}</p>
            <p class="record-meta">审核时间：{{ formatDate(item.reviewed_at) }}</p>
            <p v-if="item.review_note" class="record-note">审核备注：{{ item.review_note }}</p>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<style scoped>
.user-center {
  display: grid;
  gap: 1rem;
}

h1 {
  margin: 0;
  color: #103f50;
}

.profile-panel {
  background: #fff;
  border: 1px solid #d4e6f0;
  border-radius: 0.9rem;
  padding: 1rem 1.2rem;
}

.profile-panel h2 {
  margin: 0 0 0.8rem;
  color: #1d5166;
}

.profile-panel p {
  margin: 0.4rem 0;
}

.qualification-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 1rem;
}

.qualification-card {
  border-radius: 0.9rem;
  border: 1px solid #d4e6f0;
  background: #fff;
  padding: 1rem;
  display: grid;
  gap: 0.8rem;
}

.qualification-card h3 {
  margin: 0;
  color: #103f50;
}

.qualification-card p {
  margin: 0;
  color: #1d5166;
}

.qualification-card textarea {
  border: 1px solid #b6cfdc;
  border-radius: 0.7rem;
  resize: vertical;
  padding: 0.7rem;
  font-family: inherit;
}

.hint {
  color: #4f6e7c;
}

.records-panel {
  background: #fff;
  border: 1px solid #d4e6f0;
  border-radius: 0.9rem;
  padding: 1rem 1.2rem;
}

.records-panel h2 {
  margin: 0 0 0.8rem;
  color: #1d5166;
}

.records-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.8rem;
}

.record-item {
  border: 1px solid #e0edf3;
  border-radius: 0.8rem;
  padding: 0.8rem;
  display: grid;
  gap: 0.35rem;
}

.record-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
}

.status-tag {
  border-radius: 999px;
  padding: 0.2rem 0.6rem;
  font-size: 0.82rem;
  font-weight: 700;
}

.status-pending {
  color: #8a5d00;
  background: #fff3cd;
}

.status-approved {
  color: #176130;
  background: #d8f3dc;
}

.status-rejected {
  color: #8e3026;
  background: #ffe8e3;
}

.record-reason,
.record-meta,
.record-note {
  margin: 0;
  color: #244f62;
}

.empty-text {
  margin: 0;
  color: #4f6e7c;
}

.btn-primary {
  border: none;
  border-radius: 0.7rem;
  padding: 0.68rem 0.9rem;
  background: #1f9f78;
  color: #fff;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}

.btn-primary:disabled {
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

.error-text {
  color: #8e3026;
}

@media (max-width: 860px) {
  .qualification-grid {
    grid-template-columns: 1fr;
  }
}
</style>