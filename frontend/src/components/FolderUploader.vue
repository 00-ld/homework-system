<template>
  <div class="uploader">
    <div class="drop-zone" @dragover.prevent @drop.prevent="handleDrop"
      :class="{ 'is-dragover': dragging }" @dragenter="dragging=true" @dragleave="dragging=false">
      <el-icon :size="48" color="#409eff"><FolderAdd /></el-icon>
      <p v-if="!files.length">拖拽文件夹到此处，或点击下方按钮选择</p>
      <p v-else class="file-count">已选择 {{ files.length }} 个文件</p>
    </div>

    <div style="margin-top:12px;text-align:center">
      <el-button type="primary" @click="selectFolder">
        <el-icon><FolderOpened /></el-icon> 选择文件夹
      </el-button>
      <input ref="fileInput" type="file" webkitdirectory multiple @change="handleFileSelect" hidden />
    </div>

    <div v-if="files.length" class="file-list">
      <div v-for="(f, i) in files" :key="i" class="file-item">
        <el-icon><Document /></el-icon>
        <span class="file-path">{{ f.relativePath || f.webkitRelativePath || f.name }}</span>
        <span class="file-size">{{ formatSize(f.size) }}</span>
      </div>
      <p class="file-total">
        共 {{ files.length }} 个文件，总计 {{ formatSize(totalSize) }}
        <span v-if="totalSize > maxSize" class="over-limit">
          （超过 {{ maxSize / (1024*1024) }}MB 限制！）
        </span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['files-change'])
const MAX_SIZE = 500 * 1024 * 1024
const maxSize = MAX_SIZE

const dragging = ref(false)
const files = ref([])
const fileInput = ref(null)

const totalSize = computed(() => files.value.reduce((s, f) => s + f.size, 0))

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
  return (bytes/(1024*1024)).toFixed(1) + ' MB'
}

function processFiles(fileList) {
  const arr = Array.from(fileList).map(f => {
    f.relativePath = f.webkitRelativePath || f.name
    return f
  })
  files.value = arr
  emit('files-change', arr, totalSize.value)
}

function selectFolder() {
  fileInput.value.value = ''
  fileInput.value.click()
}

function handleFileSelect(e) {
  if (e.target.files.length) processFiles(e.target.files)
}

function handleDrop(e) {
  dragging.value = false
  const items = e.dataTransfer.items
  if (items) {
    const promises = []
    for (const item of items) {
      if (item.webkitGetAsEntry) {
        promises.push(traverseEntry(item.webkitGetAsEntry()))
      }
    }
    Promise.all(promises).then(results => {
      const allFiles = results.flat()
      if (allFiles.length) processFiles(allFiles)
    })
  } else if (e.dataTransfer.files.length) {
    processFiles(e.dataTransfer.files)
  }
}

function traverseEntry(entry) {
  return new Promise(resolve => {
    if (entry.isFile) {
      entry.file(file => {
        file.relativePath = entry.fullPath.replace(/^\//, '')
        resolve([file])
      })
    } else if (entry.isDirectory) {
      const reader = entry.createReader()
      const allEntries = []
      function readEntries() {
        reader.readEntries(entries => {
          if (entries.length) {
            allEntries.push(...entries)
            readEntries()
          } else {
            resolve(Promise.all(allEntries.map(e => traverseEntry(e))).then(r => r.flat()))
          }
        })
      }
      readEntries()
    } else {
      resolve([])
    }
  })
}

defineExpose({ files, totalSize, getFiles: () => files.value })
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}
.drop-zone:hover, .drop-zone.is-dragover {
  border-color: #409eff;
  background: #ecf5ff;
}
.drop-zone p { color: #909399; margin: 8px 0 0; }
.file-count { font-size: 16px; color: #409eff !important; }
.file-list { margin-top: 16px; max-height: 300px; overflow-y: auto; }
.file-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; font-size: 13px; color: #606266;
}
.file-item:nth-child(odd) { background: #fafafa; }
.file-path { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { color: #909399; white-space: nowrap; }
.file-total { font-size: 14px; font-weight: bold; margin: 8px 0 0; text-align: right; }
.over-limit { color: #f56c6c; }
</style>
