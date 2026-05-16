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
        <!-- 改进8: 记住账号 -->
        <el-form-item>
          <el-checkbox v-model="rememberAccount">记住账号</el-checkbox>
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
// 改进8: 记住账号
const rememberAccount = ref(false)

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
    // 改进8: 记住账号
    if (rememberAccount.value) {
      localStorage.setItem('remembered_admin_user', username.value)
    } else {
      localStorage.removeItem('remembered_admin_user')
    }
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (e) {
    // error handled by axios interceptor
  } finally {
    loading.value = false
  }
}

// 改进8: 自动填充记住的账号
const savedUser = localStorage.getItem('remembered_admin_user')
if (savedUser) {
  username.value = savedUser
  rememberAccount.value = true
}
</script>

<style scoped>
.login-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.login-card {
  background: white; padding: 40px; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15); width: 400px; max-width: 100%;
  animation: cardIn 0.4s ease;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.login-title { text-align: center; font-size: 24px; color: #303133; margin: 0 0 24px; }

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .login-container { padding: 16px; }
  .login-card { padding: 28px 20px; }
  .login-title { font-size: 20px; }
}
</style>
