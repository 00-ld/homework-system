<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>作业提交系统</h1>
        <span class="admin-badge" v-if="isSuperAdmin">超级管理员</span>
        <span class="class-badge">{{ adminInfo?.class_name }}</span>
      </div>
      <div>
        <el-button type="primary" @click="$router.push('/admin/homework/create')" size="large">
          <el-icon><Plus /></el-icon> 创建新作业
        </el-button>
        <el-button @click="$router.push('/admin/sms-config')">
          <el-icon><Message /></el-icon> 邮件设置
        </el-button>
        <el-button @click="logout" type="info" plain>退出登录</el-button>
      </div>
    </header>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="作业管理" name="homeworks">
        <el-table :data="homeworks" stripe style="width:100%" v-loading="loading" empty-text="暂无作业">
          <el-table-column prop="title" label="作业名称" min-width="180" />
          <el-table-column prop="due_date" label="截止时间" width="160" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="提交人数" width="100">
            <template #default="{ row }">
              <el-tag type="success">{{ row.submissions?.length || 0 }} 人</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="$router.push(`/admin/homework/${row.id}`)">查看</el-button>
              <el-button size="small" @click="copyLink(row)"><el-icon><Link /></el-icon> 复制链接</el-button>
              <el-popconfirm title="确定删除此作业？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="学生管理" name="students">
        <el-table :data="students" stripe v-loading="loadingStudents" empty-text="本班暂无注册学生">
          <el-table-column prop="student_name" label="姓名" width="120" />
          <el-table-column prop="student_id" label="学号" width="140" />
          <el-table-column prop="email" label="邮箱" min-width="200">
            <template #default="{ row }">{{ row.email || row.phone || '-' }}</template>
          </el-table-column>
          <el-table-column prop="registered_at" label="注册时间" width="180">
            <template #default="{ row }">{{ formatTime(row.registered_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="isSuperAdmin" label="系统管理" name="system">
        <h3 style="margin:0 0 16px">管理员账号管理</h3>
        <el-table :data="admins" stripe v-loading="loadingAdmins">
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="class_name" label="班级" width="200" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-popconfirm
                v-if="row.username !== 'admin'"
                :title="`确定踢出 ${row.username}？`"
                @confirm="handleKickAdmin(row.username)">
                <template #reference>
                  <el-button size="small" type="danger">踢出</el-button>
                </template>
              </el-popconfirm>
              <el-tag v-else type="info">不可操作</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listHomeworks, deleteHomework, getStudents, getAllAdmins, deleteAdmin } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('homeworks')
const homeworks = ref([])
const loading = ref(true)
const students = ref([])
const loadingStudents = ref(false)
const admins = ref([])
const loadingAdmins = ref(false)
const adminInfo = ref(null)
const isSuperAdmin = computed(() => adminInfo.value?.username === 'admin')

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function fetchHomeworks() {
  loading.value = true
  try {
    const res = await listHomeworks()
    homeworks.value = res.data.homeworks
  } finally { loading.value = false }
}

async function fetchStudents() {
  loadingStudents.value = true
  try {
    const res = await getStudents()
    students.value = res.data.students || []
  } finally { loadingStudents.value = false }
}

async function fetchAdmins() {
  if (!isSuperAdmin.value) return
  loadingAdmins.value = true
  try {
    const res = await getAllAdmins()
    admins.value = res.data.admins || []
  } finally { loadingAdmins.value = false }
}

function copyLink(row) {
  const link = `${window.location.origin}/#/submit/${row.link_id}`
  navigator.clipboard.writeText(link).then(() => ElMessage.success('链接已复制'))
    .catch(() => ElMessage.info(`提交链接: ${link}`))
}

async function handleDelete(id) {
  await deleteHomework(id)
  ElMessage.success('已删除')
  fetchHomeworks()
}

async function handleKickAdmin(username) {
  try {
    await deleteAdmin(username)
    ElMessage.success(`已踢出 ${username}`)
    fetchAdmins()
  } catch { /* handled */ }
}

function logout() {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_info')
  router.push('/')
}

onMounted(async () => {
  const saved = localStorage.getItem('admin_info')
  if (saved) {
    adminInfo.value = JSON.parse(saved)
  }
  fetchHomeworks()
  fetchStudents()
  fetchAdmins()
})
</script>

<style scoped>
.dashboard { max-width: 1200px; margin: 0 auto; padding: 24px; }
.dashboard-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px; background: white; padding: 20px 24px;
  border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.dashboard-header h1 { margin: 0; font-size: 20px; }
.admin-badge { color: #e6a23c; font-size: 12px; margin-left: 8px; }
.class-badge { color: #909399; font-size: 12px; margin-left: 8px; }
</style>
