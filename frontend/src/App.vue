<template>
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup>
</script>

<style>
/* 全局样式和UI美化 */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --info-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --card-shadow: 0 2px 12px rgba(0,0,0,0.06);
  --card-hover-shadow: 0 4px 20px rgba(0,0,0,0.1);
  --border-radius: 12px;
  --border-radius-lg: 16px;
}

body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  background-color: #f5f7fa;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 淡入淡出页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Element Plus 全局覆盖 - 美化 */
.el-button {
  border-radius: 8px;
  transition: all 0.25s ease;
}
.el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.el-button--primary {
  background: var(--primary-gradient);
  border: none;
}
.el-button--primary:hover {
  background: linear-gradient(135deg, #5a6fdb 0%, #6a4198 100%);
}
.el-button--success {
  background: var(--success-gradient);
  border: none;
}
.el-button--warning {
  background: var(--warning-gradient);
  border: none;
}

.el-card {
  border-radius: var(--border-radius-lg) !important;
  border: none !important;
  box-shadow: var(--card-shadow) !important;
}

.el-table {
  border-radius: var(--border-radius);
  overflow: hidden;
}
.el-table th.el-table__cell {
  background: linear-gradient(135deg, #f5f7ff 0%, #f0f4ff 100%) !important;
  color: #303133;
  font-weight: 600;
}

.el-tag {
  border-radius: 6px;
}

.el-dialog {
  border-radius: var(--border-radius-lg);
}
.el-dialog__header {
  border-bottom: 1px solid #ebeef5;
  padding: 20px 24px;
  margin-right: 0;
}
.el-dialog__body {
  padding: 20px 24px;
}
.el-dialog__footer {
  border-top: 1px solid #ebeef5;
  padding: 16px 24px;
}

.el-tabs__item {
  font-size: 15px;
  font-weight: 500;
  transition: color 0.25s;
}
.el-tabs__item.is-active {
  color: #667eea;
}
.el-tabs__active-bar {
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.el-input__wrapper {
  border-radius: 8px !important;
  transition: box-shadow 0.25s !important;
}
.el-input__wrapper:focus,
.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px #667eea inset !important;
}

.el-select .el-input__wrapper {
  border-radius: 8px !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 改进12: 全局自适应 */
@media (max-width: 768px) {
  .el-dialog {
    width: 90% !important;
    max-width: 90vw !important;
  }
  .el-message-box {
    width: 85% !important;
  }
  .el-table {
    font-size: 13px;
  }
  .el-button {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .el-table {
    font-size: 12px;
  }
  body {
    font-size: 14px;
  }
}
</style>
