<template>
  <div class="login-page">
    <div class="login-card">
      <h1>学生登录</h1>
      <p class="tip">请输入您的姓名和学号进行验证</p>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @keyup.enter="handleLogin">
        <el-form-item prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="studentId">
          <el-input v-model="form.studentId" placeholder="请输入学号" size="large" prefix-icon="Edit" />
        </el-form-item>

        <!-- Class selection (only shown during registration) -->
        <el-form-item v-if="showRegister" prop="className">
          <el-select v-model="form.className" placeholder="选择班级" size="large" style="width:100%" filterable :loading="loadingClasses">
            <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
            <template #empty>
              <span v-if="loadingClasses">加载中...</span>
              <span v-else>暂无可用班级，请联系老师创建</span>
            </template>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button v-if="!showRegister" type="success" @click="handleLogin" :loading="logging" size="large" style="width:100%">
            验证身份
          </el-button>
          <el-button v-else type="primary" @click="handleRegister" :loading="registering" size="large" style="width:100%">
            注册并登录
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="errorMsg" style="margin-top:12px">
        <el-alert :title="errorMsg" type="error" :closable="false" show-icon />
      </div>
      <div style="margin-top:16px;text-align:center">
        <span style="color:#909399;font-size:13px">
          {{ showRegister ? '已有账号？' : '首次使用？' }}
        </span>
        <el-button text type="primary" @click="toggleRegister">
          {{ showRegister ? '返回登录' : '注册新账号' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { studentLogin, studentRegister, getPublicClasses } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const logging = ref(false)
const registering = ref(false)
const errorMsg = ref('')
const showRegister = ref(false)
const classes = ref([])
const loadingClasses = ref(true)

const form = reactive({ name: '', studentId: '', className: '' })
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  studentId: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  className: [{ required: true, message: '请选择班级', trigger: 'change' }]
}

function toggleRegister() {
  showRegister.value = !showRegister.value
  errorMsg.value = ''
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  logging.value = true; errorMsg.value = ''
  try {
    const res = await studentLogin(form.name, form.studentId)
    const student = res.data.student
    sessionStorage.setItem('student_info', JSON.stringify(student))
    ElMessage.success('登录成功')
    router.push('/student/dashboard')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '验证失败'
  } finally { logging.value = false }
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!form.className) {
    errorMsg.value = '请选择班级'
    return
  }
  registering.value = true; errorMsg.value = ''
  try {
    const res = await studentRegister(form.name, form.studentId, form.className)
    sessionStorage.setItem('student_info', JSON.stringify(res.data.student))
    ElMessage.success('注册成功')
    router.push('/student/dashboard')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '注册失败'
  } finally { registering.value = false }
}

onMounted(async () => {
  loadingClasses.value = true
  try {
    const res = await getPublicClasses()
    classes.value = res.data.classes || []
  } catch { /* ignore */ }
  finally { loadingClasses.value = false }
})
</script>

<style scoped>
.login-page {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
}
.login-card {
  background: white; padding: 40px 32px; border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.12); width: 100%; max-width: 400px;
}
.login-card h1 { margin: 0 0 8px; text-align: center; font-size: 22px; }
.tip { text-align: center; color: #909399; margin: 0 0 24px; font-size: 14px; }
</style>
