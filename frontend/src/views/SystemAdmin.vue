<template>
  <!-- 改进7: 超管面板 -->
  <div class="system-page" v-loading="loading">
    <header class="sys-header">
      <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:12px;padding:0">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h1>系统管理</h1>
    </header>

    <!-- 系统概览卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="8" :md="4" v-for="stat in stats" :key="stat.label">
        <div class="stat-card" :style="{ background: stat.bg }">
          <div class="stat-icon">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 管理员列表 -->
    <div class="section-card">
      <div class="section-header">
        <h2>所有管理员</h2>
      </div>
      <el-table :data="admins" stripe v-loading="loadingAdmins" empty-text="暂无管理员" style="width:100%">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="class_name" label="班级" width="200" />
        <el-table-column prop="created_at" label="注册时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              v-if="row.username !== 'admin'"
              :title="`确定踢出管理员 ${row.username}？此操作不可撤销！`"
              @confirm="handleKickAdmin(row.username)">
              <template #reference>
                <el-button size="small" type="danger">踢出</el-button>
              </template>
            </el-popconfirm>
            <el-tag v-else type="warning">超级管理员</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAllAdmins, deleteAdmin, getSystemOverview } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Collection, Reading, Notebook, Upload } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(true)
const loadingAdmins = ref(false)
const admins = ref([])

const stats = reactive([
  { label: '管理员', value: 0, icon: 'UserFilled', bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { label: '班级', value: 0, icon: 'Collection', bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { label: '学生', value: 0, icon: 'Reading', bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { label: '作业', value: 0, icon: 'Notebook', bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
  { label: '提交', value: 0, icon: 'Upload', bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
])

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function fetchStats() {
  try {
    const res = await getSystemOverview()
    const data = res.data
    stats[0].value = data.total_admins ?? '-'
    stats[1].value = data.total_classes ?? '-'
    stats[2].value = data.total_students ?? '-'
    stats[3].value = data.total_homeworks ?? '-'
    stats[4].value = data.total_submissions ?? '-'
  } catch {
    // API may not be available yet
  }
}

async function fetchAdmins() {
  loadingAdmins.value = true
  try {
    const res = await getAllAdmins()
    admins.value = res.data.admins || []
  } catch { /* ignored */ }
  finally { loadingAdmins.value = false }
}

async function handleKickAdmin(username) {
  try {
    await ElMessageBox.confirm(
      `确定要踢出管理员「${username}」吗？此操作不可撤销！`,
      '警告',
      { confirmButtonText: '确定踢出', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteAdmin(username)
    ElMessage.success(`已踢出 ${username}`)
    fetchAdmins()
  } catch {
    // user cancelled or error handled by interceptor
  }
}

onMounted(async () => {
  await Promise.all([fetchStats(), fetchAdmins()])
  loading.value = false
})
</script>

<style scoped>
.system-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.sys-header { margin-bottom: 24px; }
.sys-header h1 { margin: 0; font-size: 24px; color: #303133; }

.stats-row { margin-bottom: 24px; }
.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-radius: 16px;
  color: white;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  margin-bottom: 16px;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.stat-icon {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
}
.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; line-height: 1.2; }
.stat-label { font-size: 13px; opacity: 0.9; margin-top: 2px; }

.section-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.section-header h2 { margin: 0; font-size: 18px; color: #303133; }

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .system-page { padding: 16px; }
  .stat-value { font-size: 22px; }
  .stat-card { padding: 16px; }
  .section-card { padding: 16px; }
}
</style>
