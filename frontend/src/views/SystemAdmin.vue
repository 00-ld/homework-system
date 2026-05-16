<template>
  <div class="system-page" v-loading="loading">
    <header class="sys-header">
      <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:12px;padding:0">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h1>系统管理</h1>
    </header>

    <el-tabs v-model="activeTab" class="sys-tabs">
      <!-- ========== 概览标签页 ========== -->
      <el-tab-pane label="概览" name="overview">
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

        <!-- 最近活动 -->
        <div class="section-card">
          <div class="section-header">
            <h2>最近活动</h2>
            <el-tag type="info" size="small" v-if="activities.length">
              共 {{ activities.length }} 条
            </el-tag>
          </div>
          <div v-if="activities.length" class="activity-list">
            <div
              v-for="(act, i) in activities"
              :key="act.time + act.type + (act.title || '') + i"
              class="activity-item"
            >
              <div class="activity-icon" :class="act.type">
                <el-icon :size="18">
                  <Notebook v-if="act.type === 'homework_created'" />
                  <Upload v-else />
                </el-icon>
              </div>
              <div class="activity-body">
                <div class="activity-text">
                  <template v-if="act.type === 'homework_created'">
                    创建了作业
                    <strong>{{ act.title }}</strong>
                    <el-tag size="small" class="activity-tag">{{ act.class_name }}</el-tag>
                  </template>
                  <template v-else>
                    学生
                    <strong>{{ act.student_name }}</strong>
                    提交了作业
                    <strong>{{ act.homework_title }}</strong>
                  </template>
                </div>
                <div class="activity-time">{{ formatTime(act.time) }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无最近活动" />
        </div>
      </el-tab-pane>

      <!-- ========== 管理员管理标签页 ========== -->
      <el-tab-pane label="管理员管理" name="admins">
        <div class="section-card">
          <div class="section-header">
            <h2>所有管理员</h2>
            <el-tag type="info" size="small">{{ admins.length }} 人</el-tag>
          </div>
          <el-table
            :data="admins"
            stripe
            v-loading="loadingAdmins"
            empty-text="暂无管理员"
            style="width:100%"
          >
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="class_name" label="班级" min-width="200" />
            <el-table-column prop="created_at" label="注册时间" min-width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="130" fixed="right">
              <template #default="{ row }">
                <el-popconfirm
                  v-if="row.username !== 'admin'"
                  :title="`确定踢出管理员 ${row.username}？此操作不可撤销！`"
                  @confirm="handleKickAdmin(row.username)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">踢出</el-button>
                  </template>
                </el-popconfirm>
                <el-tag v-else type="warning">超级管理员</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- ========== 反馈管理标签页 ========== -->
      <el-tab-pane label="反馈管理" name="feedbacks">
        <div class="section-card">
          <div class="section-header">
            <h2>意见与反馈</h2>
          </div>
          <div class="filter-bar">
            <el-select
              v-model="typeFilter"
              placeholder="筛选类型"
              clearable
              style="width:160px"
              @change="fetchFeedbacks"
            >
              <el-option label="全部" value="" />
              <el-option label="Bug" value="bug" />
              <el-option label="建议" value="suggestion" />
            </el-select>
            <span class="filter-count" v-if="feedbacks.length">
              共 {{ feedbacks.length }} 条反馈
            </span>
          </div>
          <el-table
            :data="feedbacks"
            stripe
            v-loading="loadingFeedbacks"
            empty-text="暂无反馈"
            style="width:100%"
          >
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'bug' ? 'danger' : 'warning'" size="small">
                  {{ row.type === 'bug' ? 'Bug' : '建议' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="contact" label="联系方式" width="180" />
            <el-table-column prop="content" label="反馈内容" min-width="280" show-overflow-tooltip />
            <el-table-column prop="created_at" label="提交时间" width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-popconfirm
                  title="确定删除此反馈？"
                  @confirm="handleDeleteFeedback(row.id)"
                >
                  <template #reference>
                    <el-button size="small" type="danger" circle>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getAllAdmins,
  deleteAdmin,
  getSystemOverview,
  getRecentActivities,
  getFeedbacks,
  deleteFeedback
} from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UserFilled,
  Collection,
  Reading,
  Notebook,
  Upload,
  Delete
} from '@element-plus/icons-vue'

const router = useRouter()

// --- 通用状态 ---
const loading = ref(true)
const activeTab = ref('overview')

// --- 概览 ---
const stats = reactive([
  { label: '管理员', value: 0, icon: 'UserFilled', bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { label: '班级', value: 0, icon: 'Collection', bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { label: '学生', value: 0, icon: 'Reading', bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { label: '作业', value: 0, icon: 'Notebook', bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
  { label: '提交', value: 0, icon: 'Upload', bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
])
const activities = ref([])

// --- 管理员 ---
const loadingAdmins = ref(false)
const admins = ref([])

// --- 反馈 ---
const loadingFeedbacks = ref(false)
const feedbacks = ref([])
const typeFilter = ref('')

// --- 通用函数 ---
function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

// --- 概览 API ---
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

async function fetchActivities() {
  try {
    const res = await getRecentActivities(10)
    activities.value = res.data.activities || []
  } catch {
    activities.value = []
  }
}

// --- 管理员 API ---
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

// --- 反馈 API ---
async function fetchFeedbacks() {
  loadingFeedbacks.value = true
  try {
    const params = typeFilter.value ? { type: typeFilter.value } : {}
    const res = await getFeedbacks(params)
    feedbacks.value = res.data.feedbacks || []
  } catch {
    feedbacks.value = []
  } finally {
    loadingFeedbacks.value = false
  }
}

async function handleDeleteFeedback(id) {
  try {
    await ElMessageBox.confirm('确定要删除这条反馈吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteFeedback(id)
    ElMessage.success('反馈已删除')
    fetchFeedbacks()
  } catch {
    // cancelled or handled
  }
}

onMounted(async () => {
  await Promise.all([fetchStats(), fetchAdmins(), fetchActivities(), fetchFeedbacks()])
  loading.value = false
})
</script>

<style scoped>
.system-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.sys-header {
  margin-bottom: 24px;
}
.sys-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

/* ─── Tabs ─── */
.sys-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
  transition: color 0.3s;
}
.sys-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
}
.sys-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}
.sys-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #667eea, #764ba2);
  height: 3px;
}
.sys-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

/* ─── 统计卡片 ─── */
.stats-row {
  margin-bottom: 24px;
}
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
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  flex-shrink: 0;
}
.stat-info {
  flex: 1;
  min-width: 0;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-label {
  font-size: 13px;
  opacity: 0.9;
  margin-top: 2px;
}

/* ─── 通用区块卡片 ─── */
.section-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: box-shadow 0.3s ease;
}
.section-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

/* ─── 最近活动列表 ─── */
.activity-list {
  display: flex;
  flex-direction: column;
}
.activity-item {
  display: flex;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}
.activity-item:last-child {
  border-bottom: none;
}
.activity-item:hover {
  background: #fafafa;
  margin: 0 -12px;
  padding-left: 12px;
  padding-right: 12px;
  border-radius: 8px;
}
.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.activity-icon.homework_created {
  background: #e8f5e9;
  color: #43a047;
}
.activity-icon.submission {
  background: #e3f2fd;
  color: #1e88e5;
}
.activity-body {
  flex: 1;
  min-width: 0;
}
.activity-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}
.activity-text strong {
  font-weight: 600;
}
.activity-tag {
  margin-left: 6px;
  vertical-align: middle;
}
.activity-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* ─── 反馈筛选栏 ─── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}
.filter-count {
  color: #909399;
  font-size: 13px;
}

/* ─── 手机自适应 ─── */
@media (max-width: 768px) {
  .system-page {
    padding: 16px;
  }
  .stat-value {
    font-size: 22px;
  }
  .stat-card {
    padding: 16px;
  }
  .section-card {
    padding: 16px;
  }
  .activity-item {
    padding: 12px 0;
  }
  .sys-tabs :deep(.el-tabs__item) {
    font-size: 13px;
    padding: 0 12px;
  }
}
</style>
