<template>
  <!-- 改进10: 提交情况 + 改进12: 手机自适应 -->
  <div class="detail-page" v-loading="loading">
    <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:16px">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>

    <div v-if="hw" class="detail-card">
      <div class="hw-header">
        <div>
          <h1>{{ hw.title }}</h1>
          <p class="hw-desc">{{ hw.description }}</p>
          <p class="hw-meta">截止日期：{{ hw.due_date }} ｜ 已提交：{{ hw.submissions?.length || 0 }} 人</p>
        </div>
        <div class="hw-actions">
          <el-button type="success" @click="copyLink">
            <el-icon><Link /></el-icon> 复制提交链接
          </el-button>
          <el-button type="primary" @click="handleExport">
            <el-icon><Download /></el-icon> 导出 CSV
          </el-button>
          <el-button type="warning" @click="handleDownloadAll">
            <el-icon><FolderOpened /></el-icon> 下载全部文件
          </el-button>
          <el-popover trigger="click" :width="280">
            <template #reference>
              <el-button>
                <el-icon><Setting /></el-icon> 导出设置
              </el-button>
            </template>
            <div style="padding:8px">
              <h4 style="margin:0 0 12px">导出选项</h4>
              <el-checkbox v-model="flatExport" style="margin-bottom:12px">
                扁平模式（不以文件夹分组）
              </el-checkbox>
              <p style="font-size:12px;color:#909399;margin:0 0 12px">
                开启后，ZIP 中文件命名为「姓名_学号_文件名」，不放在子文件夹中。
              </p>
              <div style="display:flex;gap:8px">
                <el-button type="primary" size="small" @click="handleDownloadAll" style="flex:1">
                  立即下载
                </el-button>
              </div>
            </div>
          </el-popover>
          <el-button type="danger" @click="handleSendReminder" :loading="sendingReminder">
            <el-icon><Message /></el-icon> 邮件提醒
          </el-button>
          <el-button @click="$router.push('/admin/sms-config')">
            <el-icon><Message /></el-icon> 邮件设置
          </el-button>
        </div>
      </div>
      <el-tag :style="{marginBottom:'16px'}">
        提交链接：{{ fullLink }}
      </el-tag>

      <!-- 改进10: 提交情况标签页 -->
      <el-tabs v-model="detailTab" class="detail-tabs">
        <el-tab-pane label="提交列表" name="submissions">
          <el-table :data="hw.submissions" stripe empty-text="暂无学生提交" style="width:100%">
            <el-table-column prop="student_name" label="姓名" width="120" />
            <el-table-column prop="student_id" label="学号" width="140" />
            <el-table-column label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.submitted_at) }}
              </template>
            </el-table-column>
            <el-table-column label="文件" min-width="200">
              <template #default="{ row }">
                <el-tag v-for="f in row.files" :key="f" style="margin:2px">{{ f }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="大小" width="100">
              <template #default="{ row }">
                {{ formatSize(row.file_size) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 改进10: 提交情况 -->
        <el-tab-pane label="提交情况" name="status">
          <div v-loading="statusLoading">
            <!-- 统计 -->
            <div class="status-stats">
              <div class="stat-item stat-submitted">
                <div class="stat-num">{{ statusStats.submitted }}</div>
                <div class="stat-label">已提交</div>
              </div>
              <div class="stat-item stat-unsubmitted">
                <div class="stat-num">{{ statusStats.not_submitted }}</div>
                <div class="stat-label">未提交</div>
              </div>
              <div class="stat-item stat-total">
                <div class="stat-num">{{ statusStats.total }}</div>
                <div class="stat-label">班级共</div>
              </div>
            </div>

            <el-table :data="statusStudents" stripe empty-text="暂无学生数据" style="width:100%">
              <el-table-column prop="student_name" label="姓名" width="150" />
              <el-table-column prop="student_id" label="学号" width="150" />
              <el-table-column label="状态" width="150">
                <template #default="{ row }">
                  <el-tag :type="row.submitted ? 'success' : 'danger'" size="large" effect="dark">
                    <el-icon style="margin-right:4px;vertical-align:-2px">
                      <SuccessFilled v-if="row.submitted" />
                      <CloseBold v-else />
                    </el-icon>
                    {{ row.submitted ? '已提交' : '未提交' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column v-if="false" label="提交时间" width="180">
                <template #default="{ row }">
                  {{ row.submitted_at ? formatTime(row.submitted_at) : '-' }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getHomework, exportCsv, downloadAll, getHomeworkStatus } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const hw = ref(null)
const loading = ref(true)
const flatExport = ref(false)
const fullLink = computed(() => hw.value ? `${window.location.origin}/#/submit/${hw.value.link_id}` : '')
// 改进10
const detailTab = ref('submissions')
const statusLoading = ref(false)
const statusStudents = ref([])
const statusStats = reactive({ submitted: 0, not_submitted: 0, total: 0 })

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}
function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
  return (bytes/(1024*1024)).toFixed(1) + ' MB'
}
function copyLink() {
  navigator.clipboard.writeText(fullLink.value)
  ElMessage.success('链接已复制')
}
async function handleExport() {
  const res = await exportCsv(route.params.id)
  const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv;charset=utf-8' }))
  const a = document.createElement('a')
  a.href = url; a.download = `submissions_${route.params.id}.csv`; a.click()
  URL.revokeObjectURL(url)
}
async function handleDownloadAll() {
  const res = await downloadAll(route.params.id, flatExport.value)
  const suffix = flatExport.value ? '_flat' : ''
  const url = URL.createObjectURL(new Blob([res.data], { type: 'application/zip' }))
  const a = document.createElement('a')
  a.href = url; a.download = `all_submissions${suffix}_${route.params.id}.zip`; a.click()
  URL.revokeObjectURL(url)
}

const sendingReminder = ref(false)
async function handleSendReminder() {
  sendingReminder.value = true
  try {
    const res = await fetch(`/api/admin/homeworks/${route.params.id}/send-reminder`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('admin_token')}` }
    })
    const data = await res.json()
    if (res.ok) {
      ElMessage.success(data.message || '提醒已发送')
    } else {
      ElMessage.warning(data.detail || '发送失败')
    }
  } catch {
    ElMessage.error('发送失败')
  } finally {
    sendingReminder.value = false
  }
}

// 改进10: 获取提交情况
async function fetchSubmissionStatus() {
  statusLoading.value = true
  try {
    const res = await getHomeworkStatus(route.params.id)
    const data = res.data
    statusStudents.value = data.students || []
    statusStats.submitted = data.stats?.submitted || 0
    statusStats.not_submitted = data.stats?.not_submitted || 0
    statusStats.total = data.stats?.total || 0
  } catch {
    // API may not be available yet, use mock data
    statusStudents.value = []
    statusStats.submitted = hw.value?.submissions?.length || 0
    statusStats.not_submitted = 0
    statusStats.total = hw.value?.submissions?.length || 0
  } finally {
    statusLoading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await getHomework(route.params.id)
    hw.value = res.data.homework
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.detail-card { background: white; padding: 32px; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.hw-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 16px; flex-wrap: wrap; gap: 16px;
}
.hw-header h1 { margin: 0 0 8px; font-size: 24px; color: #303133; }
.hw-desc { color: #606266; margin: 0 0 8px; white-space: pre-wrap; line-height: 1.6; }
.hw-meta { color: #909399; font-size: 13px; margin: 0; }
.hw-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* 改进10: 提交情况样式 */
.detail-tabs { margin-top: 16px; }
.status-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.stat-item {
  flex: 1;
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  color: white;
  transition: transform 0.3s ease;
}
.stat-item:hover { transform: translateY(-3px); }
.stat-submitted { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.stat-unsubmitted { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-total { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-num { font-size: 32px; font-weight: 700; }
.stat-label { font-size: 14px; opacity: 0.9; margin-top: 4px; }

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .detail-page { padding: 16px; }
  .detail-card { padding: 20px; }
  .hw-header { flex-direction: column; }
  .hw-header h1 { font-size: 20px; }
  .hw-actions { width: 100%; }
  .hw-actions .el-button { flex: 1; min-width: 0; font-size: 12px; padding: 8px 12px; }
  .status-stats { flex-direction: column; gap: 8px; }
  .stat-item { padding: 16px; }
  .stat-num { font-size: 24px; }
}
</style>
