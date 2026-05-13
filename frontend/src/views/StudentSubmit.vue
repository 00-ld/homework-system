<template>
  <div class="submit-page" v-loading="loading">
    <div style="max-width:700px;margin:0 auto;width:100%">
      <el-button text @click="$router.push('/student/dashboard')" style="margin-bottom:16px">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
    </div>

    <div v-if="!loading && !hw" class="submit-card" style="text-align:center;padding:60px">
      <el-icon :size="64" color="#f56c6c"><WarningFilled /></el-icon>
      <h2>链接无效</h2>
      <p>该提交链接不存在或已过期。</p>
    </div>

    <div v-if="hw && !submitted" class="submit-card">
      <div class="user-bar" v-if="student">
        <span>{{ student.student_name }} ({{ student.student_id }})</span>
      </div>
      <h1>{{ hw.title }}</h1>
      <div class="hw-info">
        <p>{{ hw.description }}</p>
        <el-tag>截止日期：{{ hw.due_date }}</el-tag>
      </div>

      <el-alert title="重复提交将覆盖之前的文件" type="info" :closable="false" show-icon style="margin:16px 0" />

      <el-divider />
      <h2>提交作业</h2>

      <FolderUploader ref="uploaderRef" @files-change="onFilesChange" />

      <div style="margin-top:20px">
        <el-button type="primary" @click="handleSubmit" :loading="uploading" size="large"
          :disabled="!canSubmit" style="width:100%">
          {{ uploading ? '上传中...' : '提交作业' }}
        </el-button>
      </div>

      <el-progress v-if="uploading" :percentage="progress" style="margin-top:16px" :stroke-width="16" />
      <div v-if="errorMsg" style="margin-top:12px">
        <el-alert :title="errorMsg" type="error" :closable="false" />
      </div>
    </div>

    <div v-if="submitted" class="submit-card" style="text-align:center;padding:60px">
      <el-icon :size="64" color="#67c23a"><SuccessFilled /></el-icon>
      <h2>提交成功！</h2>
      <p style="color:#909399;margin-bottom:24px">你的作业已成功提交。</p>
      <el-button type="primary" @click="$router.push('/student/dashboard')">返回作业列表</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSubmitPage, submitHomework } from '@/api'
import { ElMessage } from 'element-plus'
import FolderUploader from '@/components/FolderUploader.vue'

const route = useRoute()
const router = useRouter()
const hw = ref(null)
const loading = ref(true)
const student = ref(null)
const uploading = ref(false)
const submitted = ref(false)
const errorMsg = ref('')
const progress = ref(0)
const uploaderRef = ref(null)
const MAX_SIZE = 500 * 1024 * 1024

const currentFiles = ref([])
const currentTotalSize = ref(0)
const canSubmit = computed(() => currentFiles.value.length > 0 && currentTotalSize.value <= MAX_SIZE)

function onFilesChange(files, totalSize) {
  currentFiles.value = files
  currentTotalSize.value = totalSize
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
    submitted.value = true
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '提交失败，请重试'
  }
}

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
  } catch {
    hw.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.submit-page {
  min-height: 100vh; background: #f5f7fa; padding: 40px 16px;
}
.submit-card {
  background: white; padding: 40px; border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); max-width: 700px; margin: 0 auto;
}
.submit-card h1 { margin: 0 0 12px; font-size: 22px; }
.submit-card h2 { font-size: 18px; margin: 0 0 16px; }
.hw-info p { color: #606266; margin: 0 0 12px; white-space: pre-wrap; }
.hw-info .el-tag { margin-right: 8px; }
.user-bar {
  background: #f0f9eb; padding: 8px 16px; border-radius: 8px;
  margin-bottom: 16px; color: #67c23a; font-size: 14px;
}
</style>
