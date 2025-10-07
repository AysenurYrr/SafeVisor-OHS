import axios from 'axios'

// Demo data for when backend is not available
const DEMO_EMPLOYEES = [
  { id: 1, uuid: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', first_name: 'John', last_name: 'Doe', email: 'john.doe@company.com', department: 'Manufacturing', position: 'Floor Supervisor', status: 'active', last_activity: '2 hours ago' },
  { id: 2, uuid: 'b2c3d4e5-f6a7-8901-bcde-f23456789012', first_name: 'Jane', last_name: 'Smith', email: 'jane.smith@company.com', department: 'Safety', position: 'HSE Officer', status: 'active', last_activity: '30 minutes ago' },
  { id: 3, uuid: 'c3d4e5f6-a7b8-9012-cdef-345678901234', first_name: 'Mike', last_name: 'Johnson', email: 'mike.johnson@company.com', department: 'Manufacturing', position: 'Machine Operator', status: 'active', last_activity: '1 hour ago' },
  { id: 4, uuid: 'd4e5f6a7-b8c9-0123-defa-456789012345', first_name: 'Sarah', last_name: 'Williams', email: 'sarah.williams@company.com', department: 'Quality Control', position: 'Quality Inspector', status: 'active', last_activity: '3 hours ago' },
  { id: 5, uuid: 'e5f6a7b8-c9d0-1234-efab-567890123456', first_name: 'David', last_name: 'Brown', email: 'david.brown@company.com', department: 'Maintenance', position: 'Maintenance Tech', status: 'inactive', last_activity: '1 day ago' },
]

const DEMO_VIOLATIONS = [
  { id: 1, employee: 'John Doe', camera: 'Camera 01 - Main Floor', date: '2025-01-14 09:30', desc: 'Missing Hard Hat' },
  { id: 2, employee: 'Mike Johnson', camera: 'Camera 03 - Assembly Line', date: '2025-01-14 08:15', desc: 'No Safety Glasses' },
  { id: 3, employee: 'Sarah Williams', camera: 'Camera 02 - QC Station', date: '2025-01-13 15:45', desc: 'Improper Gloves' },
  { id: 4, employee: 'David Brown', camera: 'Camera 04 - Maintenance Area', date: '2025-01-13 11:20', desc: 'Missing Safety Vest' },
  { id: 5, employee: 'Jane Smith', camera: 'Camera 01 - Main Floor', date: '2025-01-12 14:10', desc: 'No Steel Toe Boots' },
]

const DEMO_POSE_ALERTS = [
  { id: 1, employee: 'John Doe', camera: 'Camera 01 - Main Floor', date: '2025-01-14 10:15', alert: 'Improper Lifting Posture' },
  { id: 2, employee: 'Mike Johnson', camera: 'Camera 03 - Assembly Line', date: '2025-01-14 09:30', alert: 'Repetitive Strain Risk' },
  { id: 3, employee: 'Sarah Williams', camera: 'Camera 02 - QC Station', date: '2025-01-13 16:20', alert: 'Poor Ergonomic Position' },
  { id: 4, employee: 'David Brown', camera: 'Camera 04 - Maintenance Area', date: '2025-01-13 12:45', alert: 'Awkward Body Position' },
  { id: 5, employee: 'Jane Smith', camera: 'Camera 01 - Main Floor', date: '2025-01-12 13:30', alert: 'Excessive Bending' },
]

// Helper function to detect if backend is available
const isDemoMode = () => {
  return localStorage.getItem('token')?.startsWith('demo-token-')
}
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
          const response = await api.post(`/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`)
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
    // Use x-www-form-urlencoded for OAuth2 password flow
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    const response = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
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
    // Backend expects refresh_token as a query parameter
    const response = await api.post(`/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`)
    return response.data
  }
}

// Employees API
export const EmployeesAPI = {
  async list(skip = 0, limit = 100) {
    if (isDemoMode()) {
      return { employees: DEMO_EMPLOYEES, total: DEMO_EMPLOYEES.length }
    }
    const response = await api.get(`/api/v1/employees/?skip=${skip}&limit=${limit}`)
    return response.data
  },

  async get(uuid) {
    if (isDemoMode()) {
      return DEMO_EMPLOYEES.find(emp => emp.uuid === uuid)
    }
    const response = await api.get(`/api/v1/employees/${uuid}`)
    return response.data
  },

  async create(employeeData) {
    if (isDemoMode()) {
      const newEmployee = { ...employeeData, id: Date.now() }
      DEMO_EMPLOYEES.push(newEmployee)
      return newEmployee
    }
    const response = await api.post('/api/v1/employees/', employeeData)
    return response.data
  },

  async createMultipart(formData) {
    const response = await api.post('/api/v1/employees/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async update(uuid, employeeData) {
    if (isDemoMode()) {
      const index = DEMO_EMPLOYEES.findIndex(emp => emp.uuid === uuid)
      if (index !== -1) {
        DEMO_EMPLOYEES[index] = { ...DEMO_EMPLOYEES[index], ...employeeData }
        return DEMO_EMPLOYEES[index]
      }
      return null
    }
    const response = await api.put(`/api/v1/employees/${uuid}`, employeeData)
    return response.data
  },

  async updateMultipart(uuid, formData) {
    const response = await api.put(`/api/v1/employees/${uuid}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async delete(uuid) {
    if (isDemoMode()) {
      const index = DEMO_EMPLOYEES.findIndex(emp => emp.uuid === uuid)
      if (index !== -1) {
        DEMO_EMPLOYEES.splice(index, 1)
        return { success: true }
      }
      return { success: false }
    }
    const response = await api.delete(`/api/v1/employees/${uuid}`)
    return response.data
  }
}

// Departments API
export const DepartmentsAPI = {
  async list(skip = 0, limit = 100, is_active = null, search = null) {
    let url = `/api/v1/departments/?skip=${skip}&limit=${limit}`
    if (is_active !== null) url += `&is_active=${is_active}`
    if (search) url += `&search=${encodeURIComponent(search)}`
    const response = await api.get(url)
    return response.data
  },

  async get(id) {
    const response = await api.get(`/api/v1/departments/${id}`)
    return response.data
  },

  async create(departmentData) {
    const response = await api.post('/api/v1/departments/', departmentData)
    return response.data
  },

  async update(id, departmentData) {
    const response = await api.put(`/api/v1/departments/${id}`, departmentData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/departments/${id}`)
    return response.data
  }
}

// Positions API
export const PositionsAPI = {
  async list(skip = 0, limit = 100, department_id = null, is_active = null, search = null) {
    let url = `/api/v1/positions/?skip=${skip}&limit=${limit}`
    if (department_id) url += `&department_id=${department_id}`
    if (is_active !== null) url += `&is_active=${is_active}`
    if (search) url += `&search=${encodeURIComponent(search)}`
    const response = await api.get(url)
    return response.data
  },

  async get(id) {
    const response = await api.get(`/api/v1/positions/${id}`)
    return response.data
  },

  async create(positionData) {
    const response = await api.post('/api/v1/positions/', positionData)
    return response.data
  },

  async update(id, positionData) {
    const response = await api.put(`/api/v1/positions/${id}`, positionData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/positions/${id}`)
    return response.data
  }
}

// Employee Logs API
export const EmployeeLogsAPI = {
  async list(skip = 0, limit = 100, employee_id = null, action = null) {
    let url = `/api/v1/employee-logs/?skip=${skip}&limit=${limit}`
    if (employee_id) url += `&employee_id=${employee_id}`
    if (action) url += `&action=${encodeURIComponent(action)}`
    const response = await api.get(url)
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
    if (isDemoMode()) {
      return DEMO_VIOLATIONS
    }
    let url = `/api/v1/violations/?skip=${skip}&limit=${limit}`
    if (employee_id) url += `&employee_id=${employee_id}`
    if (camera_id) url += `&camera_id=${camera_id}`
    if (start_date) url += `&start_date=${start_date}`
    if (end_date) url += `&end_date=${end_date}`
    
    const response = await api.get(url)
    return response.data
  },

  async getViolation(id) {
    if (isDemoMode()) {
      return DEMO_VIOLATIONS.find(v => v.id === id)
    }
    const response = await api.get(`/api/v1/violations/${id}`)
    return response.data
  },

  async acknowledgeViolation(id, acknowledgmentData) {
    if (isDemoMode()) {
      return { success: true }
    }
    const response = await api.put(`/api/v1/violations/${id}`, {
      ...acknowledgmentData,
      is_acknowledged: true
    })
    return response.data
  },

  async getViolationStats() {
    if (isDemoMode()) {
      return { total: 23, this_week: 8, this_month: 35 }
    }
    const response = await api.get('/api/v1/violations/stats/summary')
    return response.data
  },

  async pose(skip = 0, limit = 100, employee_id = null, start_date = null, end_date = null) {
    if (isDemoMode()) {
      return DEMO_POSE_ALERTS
    }
    let url = `/api/v1/pose-alerts/?skip=${skip}&limit=${limit}`
    if (employee_id) url += `&employee_id=${employee_id}`
    if (start_date) url += `&start_date=${start_date}`
    if (end_date) url += `&end_date=${end_date}`
    
    const response = await api.get(url)
    return response.data
  },

  async getPoseAlert(id) {
    if (isDemoMode()) {
      return DEMO_POSE_ALERTS.find(p => p.id === id)
    }
    const response = await api.get(`/api/v1/pose-alerts/${id}`)
    return response.data
  },

  async acknowledgePoseAlert(id, acknowledgmentData) {
    if (isDemoMode()) {
      return { success: true }
    }
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

// Factory Areas API
export const FactoryAreasAPI = {
  async list(skip = 0, limit = 100, is_active = null, search = null) {
    let url = `/api/v1/factory-areas/?skip=${skip}&limit=${limit}`
    if (is_active !== null) url += `&is_active=${is_active}`
    if (search) url += `&search=${encodeURIComponent(search)}`
    
    const response = await api.get(url)
    return response.data
  },

  async get(id) {
    const response = await api.get(`/api/v1/factory-areas/${id}`)
    return response.data
  },

  async create(areaData) {
    const response = await api.post('/api/v1/factory-areas/', areaData)
    return response.data
  },

  async update(id, areaData) {
    const response = await api.put(`/api/v1/factory-areas/${id}`, areaData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/factory-areas/${id}`)
    return response.data
  },

  async getSafetyRules() {
    const response = await api.get('/api/v1/factory-areas/safety-rules')
    return response.data
  }
}

