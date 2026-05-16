<template>
  <!-- 改进7: 反馈管理 -->
  <div class="feedback-page" v-loading="loading">
    <header class="fb-header">
      <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:12px;padding:0">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h1>意见与反馈</h1>
    </header>

    <div class="fb-card">
      <!-- 筛选 -->
      <div class="filter-bar">
        <el-select v-model="typeFilter" placeholder="筛选类型" clearable style="width:160px" @change="fetchFeedbacks">
          <el-option label="全部" value="" />
          <el-option label="Bug" value="bug" />
          <el-option label="建议" value="suggestion" />
        </el-select>
        <span class="filter-count" v-if="feedbacks.length">
          共 {{ feedbacks.length }} 条反馈
        </span>
      </div>

      <el-table :data="feedbacks" stripe empty-text="暂无反馈" style="width:100%">
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
              @confirm="handleDelete(row.id)">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFeedbacks, deleteFeedback } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(true)
const feedbacks = ref([])
const typeFilter = ref('')

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function fetchFeedbacks() {
  loading.value = true
  try {
    const params = typeFilter.value ? { type: typeFilter.value } : {}
    const res = await getFeedbacks({ params })
    feedbacks.value = res.data.feedbacks || []
  } catch {
    feedbacks.value = []
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
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

onMounted(() => {
  fetchFeedbacks()
})
</script>

<style scoped>
.feedback-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.fb-header { margin-bottom: 24px; }
.fb-header h1 { margin: 0; font-size: 24px; color: #303133; }

.fb-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
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

/* 改进12: 自适应 */
@media (max-width: 768px) {
  .feedback-page { padding: 16px; }
  .fb-card { padding: 16px; }
}
</style>
