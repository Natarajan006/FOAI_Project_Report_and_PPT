import api from './api'

export const authService = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  me: () => api.get('/api/auth/me'),
  logout: () => api.post('/api/auth/logout'),
  updateProfile: (data) => api.put('/api/auth/profile', data),
}

export const loanService = {
  create: (data) => api.post('/api/loans', data),
  list: () => api.get('/api/loans'),
  get: (id) => api.get(`/api/loans/${id}`),
  dashboardStats: () => api.get('/api/loans/dashboard/stats'),
}

export const assessmentService = {
  evaluate: (applicationId) =>
    api.post('/api/assessment/evaluate', { application_id: applicationId }),
  get: (id) => api.get(`/api/assessment/${id}`),
  history: () => api.get('/api/assessment/history'),
  downloadReport: (id) =>
    api.get(`/api/assessment/${id}/report`, { responseType: 'blob' }),
}

export const aiService = {
  advisor: (message, applicationId = null, context = null) =>
    api.post('/api/ai/advisor', {
      message,
      application_id: applicationId,
      context,
    }),
  whatIf: (payload) => api.post('/api/ai/what-if', payload),
  emi: (payload) => api.post('/api/ai/emi/public', payload),
}

export const adminService = {
  dashboard: () => api.get('/api/admin/dashboard'),
  users: () => api.get('/api/admin/users'),
  applications: (params = {}) => api.get('/api/admin/applications', { params }),
  applicationDetail: (id) => api.get(`/api/admin/applications/${id}`),
  decide: (loanId, data) => api.post(`/api/admin/applications/${loanId}/decision`, data),
  contact: (loanId, data) => api.post(`/api/admin/applications/${loanId}/contact`, data),
  contacts: () => api.get('/api/admin/contacts'),
  review: (assessmentId, data) =>
    api.post(`/api/admin/assessments/${assessmentId}/review`, data),
  rules: () => api.get('/api/admin/rules'),
  createRule: (data) => api.post('/api/admin/rules', data),
  updateRule: (id, data) => api.put(`/api/admin/rules/${id}`, data),
  deleteRule: (id) => api.delete(`/api/admin/rules/${id}`),
}
