<template>
  <div class="stu-page">
    <header class="stu-header">
      <div>
        <h1>作业提交系统</h1>
        <span class="user-badge">{{ student?.student_name }} ({{ student?.student_id }})</span>
        <span v-if="student?.email" class="phone-badge">
          <el-icon><Message /></el-icon> {{ student.email }}
        </span>
      </div>
      <div style="display:flex;gap:8px;align-items:center">
        <el-popover trigger="click" :width="300">
          <template #reference>
            <el-button size="small">
              <el-icon><Message /></el-icon> 邮箱
            </el-button>
          </template>
          <div style="padding:8px">
            <h4 style="margin:0 0 8px">邮箱设置</h4>
            <p style="font-size:12px;color:#909399;margin:0 0 12px">
              填写邮箱后，可接收作业截止邮件提醒（免费）。
            </p>
            <el-input v-model="emailInput" placeholder="请输入邮箱地址" style="margin-bottom:8px" />
            <el-button type="primary" size="small" @click="saveEmail" :loading="savingEmail" style="width:100%">
              保存
            </el-button>
          </div>
        </el-popover>
        <el-button size="small" @click="subscribeNotification">
          <el-icon><Bell /></el-icon> 桌面提醒
        </el-button>
        <el-button @click="logout" type="info" plain>退出登录</el-button>
      </div>
    </header>

    <el-tabs v-model="activeTab" class="stu-tabs">
      <el-tab-pane label="公告" name="notice">
        <div v-if="!homeworks.length" style="text-align:center;padding:60px;color:#909399">
          暂无公告
        </div>
        <div v-for="hw in homeworks" :key="hw.link_id" class="notice-card">
          <div class="notice-header">
            <h3>{{ hw.title }}</h3>
            <el-tag size="small">截止：{{ hw.due_date }}</el-tag>
          </div>
          <p class="notice-desc">{{ hw.description || '无详细说明' }}</p>
          <div class="notice-footer">
            <span class="notice-date">发布：{{ formatTime(hw.created_at) }}</span>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="提交作业" name="submit">
        <div v-if="!homeworks.length" style="text-align:center;padding:60px;color:#909399">
          暂无作业
        </div>
        <div v-for="hw in homeworks" :key="hw.link_id" class="hw-card">
          <div class="hw-card-body">
            <h3>{{ hw.title }}</h3>
            <p>{{ hw.description || '无详细说明' }}</p>
            <el-tag size="small">截止：{{ hw.due_date }}</el-tag>
          </div>
          <div class="hw-card-action">
            <el-button type="primary" @click="goSubmit(hw.link_id)">
              提交作业
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, Bell } from '@element-plus/icons-vue'

const router = useRouter()
const activeTab = ref('notice')
const homeworks = ref([])
const student = ref(null)
const emailInput = ref('')
const savingEmail = ref(false)

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

function goSubmit(linkId) {
  router.push(`/student/submit/${linkId}`)
}

function logout() {
  sessionStorage.removeItem('student_info')
  router.push('/')
}

async function saveEmail() {
  const email = emailInput.value.trim()
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }
  savingEmail.value = true
  try {
    const res = await fetch('/api/student/update-phone', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: student.value.student_id, phone: email })
    })
    const data = await res.json()
    if (res.ok) {
      student.value.email = email
      student.value.phone = email
      sessionStorage.setItem('student_info', JSON.stringify(student.value))
      ElMessage.success('邮箱已保存')
    } else {
      ElMessage.error(data.detail || '保存失败')
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingEmail.value = false
  }
}

function subscribeNotification() {
  if (!('Notification' in window)) {
    ElMessage.warning('当前浏览器不支持桌面通知')
    return
  }
  if (Notification.permission === 'granted') {
    new Notification('作业提交系统', { body: '桌面提醒已开启，作业截止时会通知你' })
    ElMessage.success('桌面提醒已开启')
  } else if (Notification.permission === 'denied') {
    ElMessage.warning('通知已被拒绝，请在浏览器设置中允许')
  } else {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        new Notification('作业提交系统', { body: '桌面提醒已开启' })
        ElMessage.success('桌面提醒已开启')
      }
    })
  }
}

async function fetchHomeworks() {
  try {
    const cn = student.value?.class_name || ''
    const res = await fetch(`/api/student/homeworks?class_name=${encodeURIComponent(cn)}`)
    const data = await res.json()
    homeworks.value = data.homeworks || []
  } catch {
    ElMessage.error('获取作业列表失败')
  }
}

onMounted(() => {
  const saved = sessionStorage.getItem('student_info')
  if (!saved) {
    router.push('/student/login')
    return
  }
  student.value = JSON.parse(saved)
  emailInput.value = student.value.email || student.value.phone || ''
  fetchHomeworks()
})
</script>

<style scoped>
.stu-page { max-width: 900px; margin: 0 auto; padding: 24px; }
.stu-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px; background: white; padding: 20px 24px;
  border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.stu-header h1 { margin: 0; font-size: 20px; }
.user-badge { color: #67c23a; font-size: 13px; margin-top: 4px; display: inline-block; }
.phone-badge { color: #409eff; font-size: 12px; margin-left: 8px; }
.stu-tabs { background: white; border-radius: 12px; padding: 20px 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.notice-card {
  padding: 20px; border: 1px solid #ebeef5; border-radius: 8px; margin-bottom: 12px;
}
.notice-card:last-child { margin-bottom: 0; }
.notice-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.notice-header h3 { margin: 0; font-size: 16px; }
.notice-desc { color: #606266; margin: 0 0 8px; white-space: pre-wrap; font-size: 14px; }
.notice-footer { display: flex; justify-content: space-between; align-items: center; }
.notice-date { color: #c0c4cc; font-size: 12px; }
.hw-card {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px; border: 1px solid #ebeef5; border-radius: 8px; margin-bottom: 12px;
}
.hw-card:last-child { margin-bottom: 0; }
.hw-card-body h3 { margin: 0 0 6px; font-size: 16px; }
.hw-card-body p { color: #606266; margin: 0 0 8px; font-size: 14px; white-space: pre-wrap; }
.hw-card-action { margin-left: 16px; }
</style>
