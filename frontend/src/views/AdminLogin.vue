<template>
  <div class="login-container">
    <div class="login-card">
      <el-button text @click="$router.push('/')" style="margin-bottom:12px;padding:0">
        <el-icon><ArrowLeft /></el-icon> 返回首页
      </el-button>
      <h1 class="login-title">管理员登录</h1>
      <el-form @submit.prevent="handleLogin" label-width="0">
        <el-form-item>
          <el-input v-model="username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="密码" show-password
            @keyup.enter="handleLogin" size="large" prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" size="large" style="width:100%">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div style="text-align:center;margin-top:16px">
        <span style="color:#909399;font-size:13px">没有账号？</span>
        <el-button text type="primary" @click="$router.push('/admin/register')">注册管理员</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(username.value, password.value)
    localStorage.setItem('admin_token', res.data.token)
    localStorage.setItem('admin_info', JSON.stringify(res.data.admin))
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (e) {
    // error handled by axios interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  background: white; padding: 40px; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15); width: 400px;
}
.login-title { text-align: center; font-size: 24px; color: #303133; margin: 0 0 24px; }
</style>
