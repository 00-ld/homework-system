import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/HomePage.vue') },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/AdminLogin.vue') },
  { path: '/admin/dashboard', name: 'AdminDashboard', component: () => import('@/views/AdminDashboard.vue') },
  { path: '/admin/homework/create', name: 'CreateHomework', component: () => import('@/views/CreateHomework.vue') },
  { path: '/admin/homework/:id', name: 'HomeworkDetail', component: () => import('@/views/HomeworkDetail.vue') },
  { path: '/admin/sms-config', name: 'AdminSmsConfig', component: () => import('@/views/AdminSmsConfig.vue') },
  { path: '/admin/register', name: 'AdminRegister', component: () => import('@/views/AdminRegister.vue') },
  { path: '/student/login', name: 'StudentLogin', component: () => import('@/views/StudentLogin.vue') },
  { path: '/student/dashboard', name: 'StudentDashboard', component: () => import('@/views/StudentDashboard.vue') },
  { path: '/student/submit/:linkId', name: 'StudentSubmit', component: () => import('@/views/StudentSubmit.vue') },
  // 改进7: 超管面板路由
  { path: '/admin/system', name: 'SystemAdmin', component: () => import('@/views/SystemAdmin.vue') },
  { path: '/admin/feedback', name: 'FeedbackList', component: () => import('@/views/FeedbackList.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const adminToken = localStorage.getItem('admin_token')
  const studentInfo = sessionStorage.getItem('student_info')

  if (to.path.startsWith('/admin') && !['/admin/login', '/admin/register'].includes(to.path) && !adminToken) {
    next('/admin/login')
  } else if (to.path.startsWith('/student/dashboard') && !studentInfo) {
    next('/student/login')
  } else if (to.path.startsWith('/student/submit') && !studentInfo) {
    next('/student/login')
  } else {
    next()
  }
})

export default router
