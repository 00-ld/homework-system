import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 600000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.hash = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export function login(username, password) {
  return api.post('/admin/login', { username, password })
}

export function adminRegister(username, password, className) {
  return api.post('/admin/register', { username, password, class_name: className })
}

export function getClasses() {
  return api.get('/admin/classes')
}

export function createClass(name) {
  return api.post('/admin/classes', { name })
}

export function createHomework(data) {
  return api.post('/admin/homeworks', data)
}

export function listHomeworks() {
  return api.get('/admin/homeworks')
}

export function getHomework(id) {
  return api.get(`/admin/homeworks/${id}`)
}

export function deleteHomework(id) {
  return api.delete(`/admin/homeworks/${id}`)
}

export function exportCsv(id) {
  return api.get(`/admin/homeworks/${id}/export-csv`, { responseType: 'blob' })
}

export function downloadAll(id, flat = false) {
  return api.get(`/admin/homeworks/${id}/download-all`, { params: { flat }, responseType: 'blob' })
}

export function getSubmitPage(linkId) {
  return api.get(`/submit/${linkId}`)
}

export function submitHomework(linkId, formData, onProgress) {
  return api.post(`/submit/${linkId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  })
}

export function checkSubmission(linkId, name, studentId) {
  return api.get(`/submit/${linkId}/check`, { params: { student_name: name, student_id: studentId } })
}

export function studentRegister(studentName, studentId, className = '', phone = '') {
  return api.post('/student/register', { student_name: studentName, student_id: studentId, class_name: className, phone })
}

export function registerStudent(data) {
  return api.post('/student/register', data)
}

export function studentLogin(studentName, studentId) {
  return api.post('/student/login', { student_name: studentName, student_id: studentId })
}

export function getPublicClasses() {
  return api.get('/student/classes')
}

export function getStudents(keyword = '', class_name = '') {
  const params = {}
  if (keyword) params.keyword = keyword
  if (class_name) params.class_name = class_name
  return api.get('/admin/students', { params })
}

export function getAllAdmins() {
  return api.get('/admin/all-admins')
}

export function deleteAdmin(username) {
  return api.delete(`/admin/admins/${username}`)
}

export function updateStudent(studentId, data) {
  return api.put(`/admin/students/${studentId}`, data)
}

export function searchStudents(keyword) {
  return api.get('/admin/students', { params: { keyword } })
}

export function addManualSubmission(hwId, data) {
  return api.post(`/admin/homeworks/${hwId}/students`, data)
}

export function deleteStudent(studentId) {
  return api.delete(`/admin/students/${studentId}`)
}

// 改进7: 系统概览
export function getSystemOverview() {
  return api.get('/admin/system-overview')
}

export function getRecentActivities(limit = 10) {
  return api.get('/admin/system/recent-activities', { params: { limit } })
}

// 改进11: 反馈相关
export function submitFeedback(data) {
  return api.post('/feedback', data)
}

export function getFeedbacks(params = {}) {
  return api.get('/admin/feedbacks', { params })
}

export function deleteFeedback(id) {
  return api.delete(`/admin/feedbacks/${id}`)
}

// 改进10: 作业提交状态
export function getHomeworkStatus(id) {
  return api.get(`/admin/homeworks/${id}/status`)
}

export default api
