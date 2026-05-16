<template>
  <div class="home-page">
    <div class="home-card">
      <div class="logo">
        <el-icon :size="48" color="#409eff"><Notebook /></el-icon>
      </div>
      <h1>班级作业提交系统</h1>
      <p class="subtitle">请选择您的角色进入系统</p>
      <div class="role-buttons">
        <el-button type="primary" size="large" @click="$router.push('/admin/login')" class="role-btn">
          <el-icon :size="20"><UserFilled /></el-icon>
          <span>管理员登录</span>
        </el-button>
        <el-button type="success" size="large" @click="$router.push('/student/login')" class="role-btn">
          <el-icon :size="20"><User /></el-icon>
          <span>学生登录</span>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Notebook, UserFilled, User } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-page {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.home-page::before {
  content: '';
  position: absolute;
  width: 600px; height: 600px;
  background: rgba(255,255,255,0.03);
  border-radius: 50%;
  top: -200px; right: -200px;
}
.home-page::after {
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  background: rgba(255,255,255,0.03);
  border-radius: 50%;
  bottom: -100px; left: -100px;
}
.home-card {
  background: white; padding: 60px 48px; border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15); text-align: center;
  max-width: 440px; width: 90%;
  position: relative;
  z-index: 1;
  animation: cardIn 0.5s ease;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(30px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.logo { margin-bottom: 16px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
.home-card h1 { margin: 0 0 8px; font-size: 26px; color: #303133; }
.subtitle { margin: 0 0 36px; color: #909399; font-size: 15px; }
.role-buttons { display: flex; flex-direction: column; gap: 16px; }
.role-btn {
  height: 56px; font-size: 17px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: all 0.3s ease;
}
.role-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* 改进12: 手机自适应 */
@media (max-width: 768px) {
  .home-card { padding: 40px 24px; }
  .home-card h1 { font-size: 22px; }
  .role-btn { height: 48px; font-size: 15px; }
}
</style>
