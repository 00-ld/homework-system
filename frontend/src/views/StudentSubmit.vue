<template>
  <!-- 改进9: 提交状态检查 + 改进11: 反馈按钮 + 改进12: 手机自适应 -->
  <div class="submit-page" v-loading="loading">
    <div class="page-inner">
      <el-button text @click="$router.push('/student/dashboard')" style="margin-bottom:16px">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>

      <!-- 链接无效 -->
      <div v-if="!loading && !hw" class="submit-card" style="text-align:center;padding:60px">
        <el-icon :size="64" color="#f56c6c"><WarningFilled /></el-icon>
        <h2>链接无效</h2>
        <p>该提交链接不存在或已过期。</p>
      </div>

      <!-- 已提交成功状态 -->
      <div v-if="hw && alreadySubmitted && !showResubmit" class="submit-card submit-success-card">
        <div class="success-icon-wrapper">
          <el-icon :size="72" color="#67c23a"><SuccessFilled /></el-icon>
        </div>
        <h2>提交成功！</h2>
        <p class="success-desc">你的作业已成功提交。</p>
        <div class="success-meta" v-if="submitRecord">
          <el-tag>提交时间：{{ formatTime(submitRecord.submitted_at) }}</el-tag>
          <el-tag v-if="submitRecord.file_count" type="info">{{ submitRecord.file_count }} 个文件</el-tag>
        </div>
        <!-- 改进9: 再次提交按钮（允许重交时显示） -->
        <el-button v-if="hw.allow_resubmit && !isPastDue" type="primary" @click="showResubmit = true" size="large" class="resubmit-btn">
          再次提交
        </el-button>
      </div>

      <!-- 提交表单（首次或再次提交） -->
      <div v-if="hw && (!alreadySubmitted || showResubmit)" class="submit-card">
        <div class="user-bar" v-if="student">
          <el-icon><User /></el-icon>
          <span>{{ student.student_name }} ({{ student.student_id }})</span>
        </div>
        <h1>{{ hw.title }}</h1>
        <div class="hw-info">
          <p class="hw-desc">{{ hw.description }}</p>
          <div class="hw-tags">
            <el-tag :type="isPastDue ? 'danger' : 'success'" effect="dark">
              {{ isPastDue ? '已截止' : '进行中' }}
            </el-tag>
            <el-tag>截止日期：{{ hw.due_date }}</el-tag>
          </div>
        </div>

        <!-- 改进9: 作业已截止提示 -->
        <el-alert v-if="isPastDue" title="作业已截止，无法提交" type="error" :closable="false" show-icon style="margin:16px 0" />

        <el-alert v-if="!isPastDue && alreadySubmitted" title="您已提交过作业，再次提交将覆盖之前的文件" type="warning" :closable="false" show-icon style="margin:16px 0" />

        <el-divider />
        <h2>{{ alreadySubmitted ? '重新提交作业' : '提交作业' }}</h2>

        <FolderUploader ref="uploaderRef" @files-change="onFilesChange" />

        <div style="margin-top:20px">
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="uploading"
            size="large"
            :disabled="!canSubmit || isPastDue"
            class="submit-btn">
            <el-icon v-if="!uploading"><Upload /></el-icon>
            {{ uploading ? '上传中...' : (alreadySubmitted ? '再次提交' : '提交作业') }}
          </el-button>
        </div>

        <el-progress v-if="uploading" :percentage="progress" style="margin-top:16px" :stroke-width="16" :color="uploadColors" />
        <div v-if="errorMsg" style="margin-top:12px">
          <el-alert :title="errorMsg" type="error" :closable="false" />
        </div>
      </div>

      <!-- 改进11: 意见与Bug反馈 -->
      <div class="feedback-section">
        <el-button type="info" plain @click="feedbackVisible = true" class="feedback-btn">
          <el-icon><ChatDotSquare /></el-icon>
          意见与Bug反馈
        </el-button>
      </div>

      <!-- 改进11: 反馈对话框 -->
      <el-dialog v-model="feedbackVisible" title="意见与Bug反馈" width="500px" :close-on-click-modal="false" class="feedback-dialog">
        <el-form ref="fbFormRef" :model="fbForm" :rules="fbRules" label-width="0">
          <el-form-item prop="type">
            <el-radio-group v-model="fbForm.type">
              <el-radio value="bug">Bug 反馈</el-radio>
              <el-radio value="suggestion">改进建议</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item prop="name">
            <el-input v-model="fbForm.name" placeholder="你的姓名（选填）" />
          </el-form-item>
          <el-form-item prop="contact">
            <el-input v-model="fbForm.contact" placeholder="联系方式（选填，邮箱/QQ/微信）" />
          </el-form-item>
          <el-form-item prop="content">
            <el-input v-model="fbForm.content" type="textarea" :rows="5" placeholder="请详细描述你遇到的问题或改进建议..." />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="feedbackVisible = false">取消</el-button>
          <el-button type="primary" @click="submitFeedback" :loading="fbSubmitting">提交反馈</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSubmitPage, submitHomework, checkSubmission, submitFeedback as apiSubmitFeedback } from '@/api'
import { ElMessage } from 'element-plus'
import FolderUploader from '@/components/FolderUploader.vue'

const route = useRoute()
const router = useRouter()
const hw = ref(null)
const loading = ref(true)
const student = ref(null)
const uploading = ref(false)
const alreadySubmitted = ref(false)
const showResubmit = ref(false)
const submitRecord = ref(null)
const errorMsg = ref('')
const progress = ref(0)
const uploaderRef = ref(null)
const MAX_SIZE = 500 * 1024 * 1024

const currentFiles = ref([])
const currentTotalSize = ref(0)
const canSubmit = computed(() => currentFiles.value.length > 0 && currentTotalSize.value <= MAX_SIZE)

// 改进9: 检查是否已过截止日期
const isPastDue = computed(() => {
  if (!hw.value?.due_date) return false
  return new Date() > new Date(hw.value.due_date)
})

const uploadColors = [
  { color: '#f56c6c', percentage: 30 },
  { color: '#e6a23c', percentage: 60 },
  { color: '#67c23a', percentage: 100 },
]

function onFilesChange(files, totalSize) {
  currentFiles.value = files
  currentTotalSize.value = totalSize
}

// 改进9: 检查提交状态
async function fetchSubmitStatus() {
  if (!student.value || !route.params.linkId) return
  try {
    const res = await checkSubmission(
      route.params.linkId,
      student.value.student_name,
      student.value.student_id
    )
    if (res.data.submitted) {
      alreadySubmitted.value = true
      submitRecord.value = res.data.submission || null
    }
  } catch {
    // API may not exist or error
  }
}

async function handleSubmit() {
  if (!currentFiles.value.length) {
    errorMsg.value = '请先选择要上传的文件夹'
    return
  }
  if (currentTotalSize.value > MAX_SIZE) {
    errorMsg.value = '文件总大小超过 500MB 限制，请减少文件后重试'
    return
  }

  const formData = new FormData()
  formData.append('student_name', student.value.student_name)
  formData.append('student_id', student.value.student_id)
  for (const file of currentFiles.value) {
    formData.append('files', file, file.relativePath || file.name)
  }

  errorMsg.value = ''
  try {
    await submitHomework(route.params.linkId, formData, (e) => {
      progress.value = Math.round((e.loaded / e.total) * 100)
    })
    ElMessage.success('提交成功！')
    alreadySubmitted.value = true
    showResubmit.value = false
    submitRecord.value = { submitted_at: new Date().toISOString() }
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '提交失败，请重试'
  }
}

// 改进11: 反馈相关
const feedbackVisible = ref(false)
const fbSubmitting = ref(false)
const fbFormRef = ref(null)

const fbForm = reactive({
  type: 'bug',
  name: '',
  contact: '',
  content: ''
})

const fbRules = {
  content: [{ required: true, message: '请输入反馈内容', trigger: 'blur' }]
}

async function submitFeedbackHandler() {
  const valid = await fbFormRef.value.validate().catch(() => false)
  if (!valid) return
  fbSubmitting.value = true
  try {
    await apiSubmitFeedback({
      type: fbForm.type,
      name: fbForm.name || (student.value?.student_name || '匿名'),
      contact: fbForm.contact || '',
      content: fbForm.content
    })
    ElMessage.success('感谢您的反馈！')
    feedbackVisible.value = false
    fbForm.content = ''
    fbForm.name = ''
    fbForm.contact = ''
  } catch {
    // handled by interceptor
  } finally {
    fbSubmitting.value = false
  }
}

// Renamed to avoid conflict with imported submitFeedback
// Using original imported function name, the component handler is different
const submitFeedback = submitFeedbackHandler

onMounted(async () => {
  const saved = sessionStorage.getItem('student_info')
  if (!saved) {
    router.push('/student/login')
    return
  }
  student.value = JSON.parse(saved)

  try {
    const res = await getSubmitPage(route.params.linkId)
    hw.value = res.data.homework
    // 改进9: 检查提交状态
    await fetchSubmitStatus()
  } catch {
    hw.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.submit-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
  padding: 40px 16px;
}
.page-inner {
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
}
.submit-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.06);
  margin-bottom: 24px;
  transition: transform 0.3s ease;
}
.submit-card:hover {
  box-shadow: 0 4px 30px rgba(0,0,0,0.08);
}
.submit-card h1 { margin: 0 0 12px; font-size: 24px; color: #303133; }
.submit-card h2 { font-size: 18px; margin: 0 0 16px; color: #303133; }
.hw-info .hw-desc { color: #606266; margin: 0 0 12px; white-space: pre-wrap; line-height: 1.6; }
.hw-info { margin-bottom: 8px; }
.hw-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.hw-tags .el-tag { margin-right: 0; }

.user-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e9 100%);
  padding: 10px 16px;
  border-radius: 10px;
  margin-bottom: 20px;
  color: #67c23a;
  font-size: 14px;
  font-weight: 500;
}

/* 改进9: 提交成功样式 */
.submit-success-card {
  text-align: center;
  padding: 60px 40px;
}
.success-icon-wrapper {
  margin-bottom: 16px;
  animation: successPop 0.5s ease;
}
@keyframes successPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}
.submit-success-card h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}
.success-desc {
  color: #909399;
  margin: 0 0 20px;
  font-size: 15px;
}
.success-meta {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.resubmit-btn {
  min-width: 180px;
  border-radius: 10px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 10px;
  letter-spacing: 1px;
}

/* 改进11: 反馈区域 */
.feedback-section {
  text-align: center;
  margin-top: 8px;
  margin-bottom: 40px;
}
.feedback-btn {
  border-radius: 20px;
  padding: 10px 24px;
  font-size: 14px;
  transition: all 0.3s;
}
.feedback-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.feedback-dialog :deep(.el-dialog__body) {
  padding-top: 8px;
}

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .submit-page { padding: 16px 12px; }
  .submit-card { padding: 24px 16px; }
  .submit-card h1 { font-size: 20px; }
  .submit-card h2 { font-size: 16px; }
  .submit-success-card { padding: 40px 20px; }
  .user-bar { font-size: 13px; padding: 8px 12px; }
  .submit-btn { height: 44px; font-size: 15px; }
  .hw-tags { flex-direction: column; align-items: flex-start; }
  .success-meta { flex-direction: column; align-items: center; }
  .feedback-dialog { width: 90% !important; max-width: 90vw; }
}
</style>
