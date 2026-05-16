<template>
  <div class="config-page">
    <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:16px">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>
    <div class="config-card">
      <h1>邮件提醒设置</h1>
      <p class="tip">配置 SMTP 邮箱，在作业截止时向学生发送邮件提醒（免费，只需任意邮箱账号）。</p>

      <el-alert title="常见免费邮箱 SMTP" type="info" :closable="false" show-icon style="margin-bottom:20px">
        <template #default>
          <p>QQ邮箱: smtp.qq.com 端口465/587（需开启SMTP服务获取授权码）</p>
          <p>163邮箱: smtp.163.com 端口465/587</p>
          <p>126邮箱: smtp.126.com 端口465/587</p>
        </template>
      </el-alert>

      <el-form ref="formRef" :model="form" label-width="150px" style="max-width:560px">
        <el-form-item label="SMTP服务器" prop="smtp_server" :rules="[{required: true, message:'请输入SMTP服务器'}]">
          <el-input v-model="form.smtp_server" placeholder="例如：smtp.qq.com" />
        </el-form-item>
        <el-form-item label="SMTP端口" prop="smtp_port">
          <el-input-number v-model="form.smtp_port" :min="1" :max="65535" />
          <span style="margin-left:8px;color:#909399;font-size:12px">常用：587(TLS) 或 465(SSL)</span>
        </el-form-item>
        <el-form-item label="邮箱地址" prop="smtp_user" :rules="[{required: true, message:'请输入邮箱地址'}]">
          <el-input v-model="form.smtp_user" placeholder="发件邮箱地址" />
        </el-form-item>
        <el-form-item label="SMTP密码/授权码" prop="smtp_password">
          <el-input v-model="form.smtp_password" type="password" show-password
            :placeholder="hasPassword ? '留空保持原值' : 'SMTP密码或授权码'" />
        </el-form-item>
        <el-form-item label="开启邮件提醒">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
          <el-button @click="$router.push('/admin/dashboard')">完成</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const saving = ref(false)
const hasPassword = ref(false)

const form = reactive({
  smtp_server: '',
  smtp_port: 587,
  smtp_user: '',
  smtp_password: '',
  enabled: false
})

async function saveConfig() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const token = localStorage.getItem('admin_token')
    const res = await fetch('/api/admin/email-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(form)
    })
    const data = await res.json()
    if (res.ok) ElMessage.success('配置已保存')
    else ElMessage.error(data.detail || '保存失败')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await fetch('/api/admin/email-config', { headers: { 'Authorization': `Bearer ${token}` } })
    const data = await res.json()
    if (res.ok) {
      form.smtp_server = data.smtp_server || ''
      form.smtp_port = data.smtp_port || 587
      form.smtp_user = data.smtp_user || ''
      form.smtp_password = data.smtp_password || ''
      form.enabled = data.enabled || false
      hasPassword.value = !!data.smtp_password
    }
  } catch { /* ignore */ }
})
</script>

<style scoped>
.config-page { max-width: 800px; margin: 0 auto; padding: 24px; }
.config-card { background: white; padding: 32px; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.config-card h1 { margin: 0 0 8px; font-size: 22px; color: #303133; }
.tip { color: #909399; margin: 0 0 24px; font-size: 14px; }

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .config-page { padding: 16px; }
  .config-card { padding: 20px; }
  .config-card h1 { font-size: 20px; }
}
</style>
