<template>
  <div class="register-page">
    <div class="register-card">
      <el-button text @click="$router.push('/admin/login')" style="margin-bottom:12px;padding:0">
        <el-icon><ArrowLeft /></el-icon> 返回登录
      </el-button>
      <h1>注册管理员</h1>
      <p class="tip">创建管理员账号并选择管理的班级</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>

        <!-- 改进4: 授权码 -->
        <el-form-item prop="auth_code">
          <el-input v-model="form.auth_code" placeholder="授权码" size="large" prefix-icon="Key" show-password />
        </el-form-item>

        <el-form-item label="班级" prop="class_name">
          <div style="display:flex;gap:8px;width:100%">
            <el-select v-model="form.class_name" placeholder="选择已有班级" size="large" style="flex:1" filterable allow-create>
              <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
            </el-select>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="registering" size="large" style="width:100%">
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider />
      <div class="create-class-area">
        <p style="margin:0 0 8px;color:#909399;font-size:13px">如果没有合适的班级，可以新建：</p>
        <div style="display:flex;gap:8px">
          <el-input v-model="newClass" placeholder="输入新班级名称" size="default" @keyup.enter="handleCreateClass" />
          <el-button type="success" @click="handleCreateClass" :loading="creatingClass" :disabled="!newClass.trim()">
            创建班级
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getClasses, createClass } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const classes = ref([])
const newClass = ref('')
const creatingClass = ref(false)
const registering = ref(false)

const form = reactive({ username: '', password: '', auth_code: '', class_name: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  // 改进4: 授权码验证
  auth_code: [{ required: true, message: '请输入授权码', trigger: 'blur' }],
  class_name: [{ required: true, message: '请选择或创建班级', trigger: 'change' }]
}

async function handleRegister() {
  if (!form.class_name) {
    ElMessage.warning('请选择或创建一个班级')
    return
  }
  registering.value = true
  try {
    // 改进4: 传递授权码
    const res = await fetch('/api/admin/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.username,
        password: form.password,
        class_name: form.class_name,
        auth_code: form.auth_code
      })
    })
    const data = await res.json()
    if (res.ok) {
      ElMessage.success('注册成功，请登录')
      router.push('/admin/login')
    } else {
      ElMessage.error(data.detail || '注册失败')
    }
  } catch {
    ElMessage.error('注册失败')
  } finally {
    registering.value = false
  }
}

async function handleCreateClass() {
  if (!newClass.value.trim()) return
  creatingClass.value = true
  try {
    const res = await fetch('/api/admin/classes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newClass.value.trim() })
    })
    const data = await res.json()
    if (res.ok) {
      classes.value.push(newClass.value.trim())
      form.class_name = newClass.value.trim()
      newClass.value = ''
      ElMessage.success('班级创建成功')
    } else {
      ElMessage.error(data.detail || '创建失败')
    }
  } catch {
    ElMessage.error('创建失败')
  } finally {
    creatingClass.value = false
  }
}

onMounted(async () => {
  try {
    const res = await fetch('/api/admin/classes')
    const data = await res.json()
    classes.value = data.classes || []
  } catch { /* ignore */ }
})
</script>

<style scoped>
.register-page {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.register-card {
  background: white; padding: 40px; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15); width: 440px; max-width: 100%;
  animation: cardIn 0.4s ease;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.register-card h1 { margin: 0 0 4px; font-size: 22px; }
.tip { color: #909399; margin: 0 0 24px; font-size: 14px; }
.create-class-area {
  background: #f5f7fa; padding: 16px; border-radius: 8px;
}

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .register-page { padding: 16px; }
  .register-card { padding: 28px 20px; }
  .register-card h1 { font-size: 20px; }
  .create-class-area > div { flex-direction: column; }
}
</style>
