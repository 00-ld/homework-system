<template>
  <div class="student-page" v-loading="loading">
    <header class="page-header">
      <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:12px;padding:0">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="header-row">
        <h1>学生管理</h1>
        <div class="header-actions">
          <el-input
            v-model="keyword"
            placeholder="搜索姓名或学号..."
            clearable
            style="width:260px"
            @clear="fetchStudents"
            @keyup.enter="fetchStudents"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="fetchStudents">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </div>
      </div>
    </header>

    <el-card shadow="never" class="table-card">
      <el-table :data="students" stripe v-loading="loadingTable" empty-text="暂无学生数据" style="width:100%">
        <el-table-column prop="student_name" label="姓名" width="120" />
        <el-table-column prop="student_id" label="学号" width="140" />
        <el-table-column prop="phone" label="手机" width="140">
          <template #default="{ row }">{{ row.phone || '-' }}</template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180">
          <template #default="{ row }">{{ row.email || '-' }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" width="150" />
        <el-table-column prop="registered_at" label="注册时间" width="180">
          <template #default="{ row }">{{ formatTime(row.registered_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '正常' : '已移除' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm
              v-if="row.status === 'active'"
              :title="`确定移除 ${row.student_name}（${row.student_id}）？`"
              @confirm="handleRemove(row)"
            >
              <template #reference>
                <el-button size="small" type="danger">移除</el-button>
              </template>
            </el-popconfirm>
            <el-tag v-else type="info" size="small">已移除</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑学生信息" width="480px">
      <el-form :model="editForm" label-width="80px" v-loading="editSaving">
        <el-form-item label="姓名">
          <el-input v-model="editForm.student_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="editForm.student_id_new" placeholder="请输入新学号（留空不修改）" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="editForm.class_name" placeholder="请选择班级" style="width:100%">
            <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave" :loading="editSaving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudents, updateStudent, getClasses, deleteStudent } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(true)
const loadingTable = ref(false)
const students = ref([])
const keyword = ref('')

const classes = ref([])

// 编辑对话框
const editDialogVisible = ref(false)
const editSaving = ref(false)
const editForm = ref({
  student_id: '',
  student_name: '',
  student_id_new: '',
  phone: '',
  class_name: ''
})
const editingStudentId = ref('')

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function fetchStudents() {
  loadingTable.value = true
  try {
    const res = await getStudents(keyword.value)
    students.value = res.data.students || []
  } catch { /* handled by interceptor */ }
  finally { loadingTable.value = false }
}

async function fetchClasses() {
  try {
    const res = await getClasses()
    classes.value = res.data.classes || []
  } catch { /* ignored */ }
}

function openEdit(row) {
  editingStudentId.value = row.student_id
  editForm.value = {
    student_id: row.student_id,
    student_name: row.student_name,
    student_id_new: '',
    phone: row.phone || '',
    class_name: row.class_name || ''
  }
  editDialogVisible.value = true
}

async function handleEditSave() {
  if (!editForm.value.student_name.trim()) {
    ElMessage.warning('姓名不能为空')
    return
  }
  editSaving.value = true
  try {
    const data = {
      student_name: editForm.value.student_name.trim()
    }
    if (editForm.value.student_id_new.trim()) {
      data.student_id_new = editForm.value.student_id_new.trim()
    }
    if (editForm.value.phone.trim()) {
      data.phone = editForm.value.phone.trim()
    }
    if (editForm.value.class_name) {
      data.class_name = editForm.value.class_name
    }
    await updateStudent(editingStudentId.value, data)
    ElMessage.success('学生信息已更新')
    editDialogVisible.value = false
    fetchStudents()
  } catch { /* handled by interceptor */ }
  finally { editSaving.value = false }
}

async function handleRemove(row) {
  try {
    await deleteStudent(row.student_id)
    ElMessage.success(`已移除 ${row.student_name}（${row.student_id}）`)
    fetchStudents()
  } catch { /* handled by interceptor */ }
}

onMounted(async () => {
  await Promise.all([fetchStudents(), fetchClasses()])
  loading.value = false
})
</script>

<style scoped>
.student-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { margin: 0 0 16px; font-size: 24px; color: #303133; }
.header-row {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
}
.header-actions { display: flex; gap: 8px; align-items: center; }
.table-card { border-radius: 12px; }

@media (max-width: 768px) {
  .student-page { padding: 16px; }
  .header-row { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-input { width: 100% !important; }
}
</style>
