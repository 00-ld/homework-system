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
}
.home-card {
  background: white; padding: 60px 48px; border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15); text-align: center;
  max-width: 440px; width: 90%;
}
.logo { margin-bottom: 16px; }
.home-card h1 { margin: 0 0 8px; font-size: 24px; color: #303133; }
.subtitle { margin: 0 0 36px; color: #909399; font-size: 15px; }
.role-buttons { display: flex; flex-direction: column; gap: 16px; }
.role-btn {
  height: 56px; font-size: 17px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; gap: 10px;
}
</style>
