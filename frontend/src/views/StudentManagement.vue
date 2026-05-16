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
            style="width:220px"
            @clear="fetchStudents"
            @keyup.enter="fetchStudents"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="classFilter" placeholder="全部班级" clearable style="width:160px" @change="onClassChange">
            <el-option label="全部班级" value="" />
            <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button type="primary" @click="fetchStudents">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button type="success" @click="openAdd">
            <el-icon><Plus /></el-icon> 添加学生
          </el-button>
        </div>
      </div>
    </header>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6" v-for="stat in statistics" :key="stat.label">
        <div class="stat-card" :style="{ background: stat.bg }">
          <div class="stat-icon">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 批量操作栏 -->
    <div class="batch-bar" v-if="selectedIds.length > 0">
      <span class="batch-info">已选 {{ selectedIds.length }} 项</span>
      <el-button size="small" type="danger" :loading="batchRemoving" @click="batchRemove">
        <el-icon><Remove /></el-icon> 批量移除
      </el-button>
    </div>

    <!-- 学生列表 -->
    <el-card shadow="never" class="table-card">
      <el-table
        ref="tableRef"
        :data="filteredStudents"
        stripe
        v-loading="loadingTable"
        empty-text="暂无学生数据"
        style="width:100%"
        @selection-change="onSelectionChange"
        :default-sort="{ prop: 'registered_at', order: 'descending' }"
        :row-class-name="rowClassName"
      >
        <el-table-column type="selection" width="45" />
        <el-table-column prop="student_name" label="姓名" width="110" />
        <el-table-column prop="student_id" label="学号" width="130" />
        <el-table-column prop="phone" label="手机" width="130">
          <template #default="{ row }">{{ row.phone || '-' }}</template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="160">
          <template #default="{ row }">{{ row.email || '-' }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column prop="submission_count" label="提交次数" width="95" align="center" sortable="custom">
          <template #default="{ row }">{{ row.submission_count ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="last_submitted_at" label="最后提交" width="170" sortable="custom">
          <template #default="{ row }">{{ row.last_submitted_at ? formatTime(row.last_submitted_at) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="registered_at" label="注册时间" width="170" sortable="custom">
          <template #default="{ row }">{{ formatTime(row.registered_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '正常' : '已移除' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
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

    <!-- 添加学生对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加学生" width="480px">
      <el-form :model="addForm" label-width="80px" v-loading="addSaving">
        <el-form-item label="姓名" required>
          <el-input v-model="addForm.student_name" placeholder="请输入姓名" maxlength="50" />
        </el-form-item>
        <el-form-item label="学号" required>
          <el-input v-model="addForm.student_id" placeholder="请输入学号" maxlength="30" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="addForm.phone" placeholder="请输入手机号" maxlength="20" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="addForm.class_name" placeholder="请选择班级" style="width:100%">
            <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddSave" :loading="addSaving">添加</el-button>
      </template>
    </el-dialog>

    <!-- 编辑学生信息对话框 -->
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudents, updateStudent, getClasses, deleteStudent, listHomeworks, registerStudent } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Remove,
  UserFilled, Reading, Collection, Warning
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(true)
const loadingTable = ref(false)
const allStudents = ref([])
const keyword = ref('')
const classFilter = ref('')
const classes = ref([])

// ---------- 统计卡片 ----------
const statistics = computed(() => {
  const list = allStudents.value
  const total = list.length
  const active = list.filter(s => s.status === 'active').length
  const inactive = list.filter(s => s.status === 'inactive').length
  const classCount = new Set(list.map(s => s.class_name).filter(Boolean)).size || classes.value.length
  return [
    { label: '总人数', value: total, icon: 'UserFilled', bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { label: '活跃人数', value: active, icon: 'Reading', bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
    { label: '已移除', value: inactive, icon: 'Warning', bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
    { label: '班级数量', value: classCount, icon: 'Collection', bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
  ]
})

// ---------- 班级筛选（前端过滤） ----------
const filteredStudents = computed(() => {
  if (!classFilter.value) return allStudents.value
  return allStudents.value.filter(s => s.class_name === classFilter.value)
})

function onClassChange() {
  // 班级切换时不需要重新请求后端（前端过滤即可）
}

// ---------- 批量选择 ----------
const selectedIds = ref([])
const batchRemoving = ref(false)
const tableRef = ref(null)

function onSelectionChange(selection) {
  selectedIds.value = selection.map(s => s.student_id)
}

function rowClassName({ row }) {
  return row.status === 'inactive' ? 'row-inactive' : ''
}

// ---------- 工具函数 ----------
function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

// ---------- 数据加载 ----------
async function fetchStudents() {
  loadingTable.value = true
  try {
    const res = await getStudents(keyword.value)
    const students = res.data.students || []

    // 并行获取作业列表，统计每个学生的提交次数和最后提交时间
    let subMap = {}
    try {
      const hwRes = await listHomeworks()
      const homeworks = hwRes.data.homeworks || []
      for (const hw of homeworks) {
        for (const sub of (hw.submissions || [])) {
          const sid = sub.student_id
          if (!subMap[sid]) {
            subMap[sid] = { count: 0, last: '' }
          }
          subMap[sid].count++
          if (sub.submitted_at > (subMap[sid].last || '')) {
            subMap[sid].last = sub.submitted_at
          }
        }
      }
    } catch {
      // 提交统计非关键功能，静默失败
    }

    allStudents.value = students.map(s => ({
      ...s,
      submission_count: subMap[s.student_id]?.count ?? 0,
      last_submitted_at: subMap[s.student_id]?.last || ''
    }))
  } catch {
    /* handled by interceptor */
  } finally {
    loadingTable.value = false
  }
}

async function fetchClasses() {
  try {
    const res = await getClasses()
    classes.value = res.data.classes || []
  } catch {
    /* ignored */
  }
}

// ---------- 添加学生 ----------
const addDialogVisible = ref(false)
const addSaving = ref(false)
const addForm = ref({
  student_name: '',
  student_id: '',
  phone: '',
  class_name: ''
})

function openAdd() {
  addForm.value = { student_name: '', student_id: '', phone: '', class_name: '' }
  addDialogVisible.value = true
}

async function handleAddSave() {
  const { student_name, student_id, phone, class_name } = addForm.value
  if (!student_name.trim()) {
    ElMessage.warning('姓名不能为空')
    return
  }
  if (!student_id.trim()) {
    ElMessage.warning('学号不能为空')
    return
  }
  addSaving.value = true
  try {
    await registerStudent({
      student_name: student_name.trim(),
      student_id: student_id.trim(),
      phone: phone.trim(),
      class_name: class_name || undefined
    })
    ElMessage.success('学生添加成功')
    addDialogVisible.value = false
    fetchStudents()
  } catch {
    /* handled by interceptor */
  } finally {
    addSaving.value = false
  }
}

// ---------- 编辑学生 ----------
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
  } catch {
    /* handled by interceptor */
  } finally {
    editSaving.value = false
  }
}

// ---------- 移除学生 ----------
async function handleRemove(row) {
  try {
    await deleteStudent(row.student_id)
    ElMessage.success(`已移除 ${row.student_name}（${row.student_id}）`)
    fetchStudents()
  } catch {
    /* handled by interceptor */
  }
}

// ---------- 批量移除 ----------
async function batchRemove() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定批量移除 ${selectedIds.value.length} 名学生？移除后仍可查看记录。`,
      '批量移除',
      { confirmButtonText: '确定移除', cancelButtonText: '取消', type: 'warning' }
    )
    batchRemoving.value = true
    for (const id of selectedIds.value) {
      await deleteStudent(id)
    }
    ElMessage.success(`已批量移除 ${selectedIds.value.length} 名学生`)
    selectedIds.value = []
    fetchStudents()
  } catch {
    // 用户取消或拦截器已处理错误
  } finally {
    batchRemoving.value = false
  }
}

// ---------- 生命周期 ----------
onMounted(async () => {
  await Promise.all([fetchStudents(), fetchClasses()])
  loading.value = false
})
</script>

<style scoped>
.student-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h1 { margin: 0 0 16px; font-size: 24px; color: #303133; }
.header-row {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
}
.header-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }

/* ---- 统计卡片 ---- */
.stats-row { margin-bottom: 20px; }
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
  flex-shrink: 0;
}
.stat-info { flex: 1; min-width: 0; }
.stat-value { font-size: 26px; font-weight: 700; line-height: 1.2; }
.stat-label { font-size: 13px; opacity: 0.9; margin-top: 2px; }

/* ---- 批量操作栏 ---- */
.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin-bottom: 16px;
  background: #ecf5ff;
  border-radius: 8px;
  border: 1px solid #d9ecff;
}
.batch-info {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

/* ---- 表格卡片 ---- */
.table-card { border-radius: 12px; }

/* 已移除学生行灰色 */
:deep(.row-inactive) {
  color: #bbb !important;
}
:deep(.row-inactive td) {
  background-color: #fafafa !important;
}
:deep(.row-inactive .el-tag--danger) {
  opacity: 0.7;
}

/* ---- 手机自适应 ---- */
@media (max-width: 768px) {
  .student-page { padding: 16px; }
  .page-header h1 { font-size: 20px; }
  .header-row { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-input,
  .header-actions .el-select { width: 100% !important; }
  .stat-value { font-size: 22px; }
  .stat-card { padding: 16px; }
  .stat-icon { width: 40px; height: 40px; }
  .table-card { padding: 0 4px; }
  :deep(.el-table .el-table__cell) { padding: 6px 4px !important; }
}
</style>
