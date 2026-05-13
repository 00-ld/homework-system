<template>
  <div class="create-page">
    <div class="create-card">
      <h1>创建新作业</h1>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" style="max-width:600px">
        <el-form-item label="作业名称" prop="title">
          <el-input v-model="form.title" placeholder="例：第三次作业" />
        </el-form-item>
        <el-form-item label="作业要求" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4"
            placeholder="描述作业内容、要求、注意事项等" />
        </el-form-item>
        <el-form-item label="截止时间" prop="due_date">
          <el-date-picker v-model="form.due_date" type="datetime" value-format="YYYY-MM-DD HH:mm"
            placeholder="选择截止日期和时间" style="width:100%" />
        </el-form-item>
        <el-form-item label="允许重交">
          <el-switch v-model="form.allow_resubmit" />
          <span style="margin-left:8px;color:#909399;font-size:13px">开启后学生可覆盖已提交的作业</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting" size="large">
            创建作业并生成链接
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>

      <el-alert v-if="created" type="success" :closable="false" style="margin-top:20px">
        <template #title>
          <p><strong>作业已创建！</strong></p>
          <p>提交链接：</p>
          <el-input :model-value="submitLink" readonly style="margin:8px 0">
            <template #append>
              <el-button @click="copyLink">复制链接</el-button>
            </template>
          </el-input>
          <p style="font-size:13px;color:#909399">将此链接发送给学生，他们打开后即可提交作业。</p>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createHomework } from '@/api'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const form = reactive({
  title: '',
  description: '',
  due_date: '',
  allow_resubmit: false
})
const rules = {
  title: [{ required: true, message: '请输入作业名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入作业要求', trigger: 'blur' }],
  due_date: [{ required: true, message: '请选择截止日期', trigger: 'change' }]
}
const submitting = ref(false)
const created = ref(false)
const submitLink = ref('')

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await createHomework(form)
    const linkId = res.data.homework.link_id
    submitLink.value = `${window.location.origin}/#/submit/${linkId}`
    created.value = true
    ElMessage.success('作业创建成功')
  } finally {
    submitting.value = false
  }
}

function copyLink() {
  navigator.clipboard.writeText(submitLink.value).then(() => {
    ElMessage.success('链接已复制')
  })
}
</script>

<style scoped>
.create-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
.create-card {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.create-card h1 { margin: 0 0 24px; font-size: 22px; }
</style>
