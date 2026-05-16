<template>
  <div class="uploader">
    <div class="drop-zone" @dragover.prevent @drop.prevent="handleDrop"
      :class="{ 'is-dragover': dragging }" @dragenter="dragging=true" @dragleave="dragging=false">
      <el-icon :size="48" :color="dragging ? '#67c23a' : '#409eff'"><FolderAdd /></el-icon>
      <p v-if="!files.length" class="drop-hint">请拖拽文件夹到此处</p>
      <p v-else class="file-count">已选择 {{ files.length }} 个文件</p>
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
/* 改进2: 美化拖拽区域 */
.drop-zone {
  border: 2.5px dashed #c0c4cc;
  border-radius: 16px;
  padding: 50px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.35s ease;
  background: linear-gradient(135deg, #fafafe 0%, #f0f4ff 100%);
  position: relative;
  overflow: hidden;
}
.drop-zone::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(102,126,234,0.03) 0%, rgba(118,75,162,0.03) 100%);
  opacity: 0;
  transition: opacity 0.35s ease;
}
.drop-zone:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, #f0f4ff 0%, #ede8ff 100%);
  box-shadow: 0 4px 20px rgba(102,126,234,0.12);
  transform: translateY(-2px);
}
.drop-zone.is-dragover {
  border-color: #67c23a;
  border-style: solid;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e9 100%);
  box-shadow: 0 4px 25px rgba(103,194,58,0.2);
  transform: translateY(-2px) scale(1.01);
}
.drop-zone p { color: #909399; margin: 12px 0 0; }
.drop-hint {
  font-size: 16px;
  color: #909399;
  font-weight: 500;
  letter-spacing: 0.5px;
}
.drop-zone:hover .drop-hint {
  color: #667eea;
}
.file-count { font-size: 16px; color: #667eea !important; font-weight: 600; }
.file-list { margin-top: 16px; max-height: 300px; overflow-y: auto; border-radius: 8px; }
.file-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; font-size: 13px; color: #606266;
  transition: background 0.2s;
}
.file-item:hover { background: #f5f7ff; }
.file-item:nth-child(odd) { background: #fafafa; }
.file-item:nth-child(odd):hover { background: #f0f4ff; }
.file-path { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { color: #909399; white-space: nowrap; }
.file-total { font-size: 14px; font-weight: bold; margin: 8px 0 0; text-align: right; color: #606266; }
.over-limit { color: #f56c6c; }
</style>
