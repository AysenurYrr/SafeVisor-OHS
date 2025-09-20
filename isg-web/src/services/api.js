import axios from 'axios'

// ISG API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({ 
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Handle 401 errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
          const { access_token, refresh_token } = response.data
          
          localStorage.setItem('token', access_token)
          localStorage.setItem('refreshToken', refresh_token)
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }
    
    return Promise.reject(error)
  }
)

// Authentication API
export const AuthAPI = {
  async login(email, password) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    })
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  async logout() {
    const response = await api.post('/auth/logout')
    return response.data
  },

  async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  }
}

// Employees API
export const EmployeesAPI = {
  async list(skip = 0, limit = 100) {
    const response = await api.get(`/api/v1/employees/?skip=${skip}&limit=${limit}`)
    return response.data
  },

  async get(id) {
    const response = await api.get(`/api/v1/employees/${id}`)
    return response.data
  },

  async create(employeeData) {
    const response = await api.post('/api/v1/employees/', employeeData)
    return response.data
  },

  async update(id, employeeData) {
    const response = await api.put(`/api/v1/employees/${id}`, employeeData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/employees/${id}`)
    return response.data
  }
}

// Cameras API
export const CamerasAPI = {
  async list(skip = 0, limit = 100) {
    const response = await api.get(`/api/v1/cameras/?skip=${skip}&limit=${limit}`)
    return response.data
  },

  async get(id) {
    const response = await api.get(`/api/v1/cameras/${id}`)
    return response.data
  },

  async create(cameraData) {
    const response = await api.post('/api/v1/cameras/', cameraData)
    return response.data
  },

  async update(id, cameraData) {
    const response = await api.put(`/api/v1/cameras/${id}`, cameraData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/cameras/${id}`)
    return response.data
  }
}

// Events API
export const EventsAPI = {
  async violations(skip = 0, limit = 100, employee_id = null, camera_id = null, start_date = null, end_date = null) {
    let url = `/api/v1/violations/?skip=${skip}&limit=${limit}`
    if (employee_id) url += `&employee_id=${employee_id}`
    if (camera_id) url += `&camera_id=${camera_id}`
    if (start_date) url += `&start_date=${start_date}`
    if (end_date) url += `&end_date=${end_date}`
    
    const response = await api.get(url)
    return response.data
  },

  async getViolation(id) {
    const response = await api.get(`/api/v1/violations/${id}`)
    return response.data
  },

  async acknowledgeViolation(id, acknowledgmentData) {
    const response = await api.put(`/api/v1/violations/${id}`, {
      ...acknowledgmentData,
      is_acknowledged: true
    })
    return response.data
  },

  async getViolationStats() {
    const response = await api.get('/api/v1/violations/stats/summary')
    return response.data
  },

  async pose(skip = 0, limit = 100, employee_id = null, start_date = null, end_date = null) {
    let url = `/api/v1/pose-alerts/?skip=${skip}&limit=${limit}`
    if (employee_id) url += `&employee_id=${employee_id}`
    if (start_date) url += `&start_date=${start_date}`
    if (end_date) url += `&end_date=${end_date}`
    
    const response = await api.get(url)
    return response.data
  },

  async getPoseAlert(id) {
    const response = await api.get(`/api/v1/pose-alerts/${id}`)
    return response.data
  },

  async acknowledgePoseAlert(id, acknowledgmentData) {
    const response = await api.put(`/api/v1/pose-alerts/${id}`, {
      ...acknowledgmentData,
      is_acknowledged: true
    })
    return response.data
  }
}

// Users API (Admin functionality)
export const UsersAPI = {
  async list(skip = 0, limit = 100) {
    const response = await api.get(`/api/v1/users/?skip=${skip}&limit=${limit}`)
    return response.data
  },

  async get(id) {
    const response = await api.get(`/api/v1/users/${id}`)
    return response.data
  },

  async create(userData) {
    const response = await api.post('/api/v1/users/', userData)
    return response.data
  },

  async update(id, userData) {
    const response = await api.put(`/api/v1/users/${id}`, userData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/users/${id}`)
    return response.data
  }
}
