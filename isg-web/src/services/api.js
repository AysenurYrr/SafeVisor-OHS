import axios from 'axios'

// Mock data for development/demo purposes
const mockEmployees = [
  { id: 1, name: 'John Smith', email: 'john.smith@safevisor.com', company: 'SafeVisor Corp', department: 'Manufacturing' },
  { id: 2, name: 'Sarah Johnson', email: 'sarah.johnson@safevisor.com', company: 'SafeVisor Corp', department: 'Quality Control' },
  { id: 3, name: 'Mike Wilson', email: 'mike.wilson@safevisor.com', company: 'SafeVisor Corp', department: 'Maintenance' },
  { id: 4, name: 'Emily Davis', email: 'emily.davis@safevisor.com', company: 'SafeVisor Corp', department: 'Operations' },
  { id: 5, name: 'David Brown', email: 'david.brown@safevisor.com', company: 'SafeVisor Corp', department: 'Safety' },
  { id: 6, name: 'Lisa Garcia', email: 'lisa.garcia@safevisor.com', company: 'SafeVisor Corp', department: 'Engineering' },
  { id: 7, name: 'James Miller', email: 'james.miller@safevisor.com', company: 'SafeVisor Corp', department: 'Production' },
  { id: 8, name: 'Anna Rodriguez', email: 'anna.rodriguez@safevisor.com', company: 'SafeVisor Corp', department: 'Logistics' }
]

const mockCameras = [
  { id: 1, name: 'Entrance Camera A1', location: 'Main Entrance', status: 'Online', lastCheck: '2025-01-09 14:30' },
  { id: 2, name: 'Production Line Cam B2', location: 'Production Floor - Line 1', status: 'Online', lastCheck: '2025-01-09 14:29' },
  { id: 3, name: 'Safety Zone Cam C3', location: 'Chemical Storage Area', status: 'Offline', lastCheck: '2025-01-09 12:15' },
  { id: 4, name: 'Loading Dock Cam D4', location: 'Loading Bay 1', status: 'Online', lastCheck: '2025-01-09 14:28' },
  { id: 5, name: 'Office Area Cam E5', location: 'Administrative Office', status: 'Online', lastCheck: '2025-01-09 14:31' },
  { id: 6, name: 'Warehouse Cam F6', location: 'Storage Warehouse', status: 'Online', lastCheck: '2025-01-09 14:27' },
  { id: 7, name: 'Emergency Exit Cam G7', location: 'Emergency Exit - East', status: 'Maintenance', lastCheck: '2025-01-09 10:45' }
]

const mockViolations = [
  { id: 1, employee: 'John Smith', camera: 'Production Line Cam B2', date: '2025-01-09', type: 'Hard Hat', desc: 'Employee not wearing hard hat in designated area', severity: 'High' },
  { id: 2, employee: 'Mike Wilson', camera: 'Chemical Storage Cam C3', date: '2025-01-09', type: 'Safety Goggles', desc: 'Missing safety goggles while handling chemicals', severity: 'Critical' },
  { id: 3, employee: 'David Brown', camera: 'Loading Dock Cam D4', date: '2025-01-08', type: 'Safety Vest', desc: 'High-visibility vest not worn in loading area', severity: 'Medium' },
  { id: 4, employee: 'James Miller', camera: 'Production Line Cam B2', date: '2025-01-08', type: 'Gloves', desc: 'Protective gloves missing during machinery operation', severity: 'High' },
  { id: 5, employee: 'Sarah Johnson', camera: 'Quality Control Cam H8', date: '2025-01-07', type: 'Hair Net', desc: 'Hair net not properly secured in food processing area', severity: 'Low' }
]

const mockPoseAlerts = [
  { id: 1, employee: 'Emily Davis', camera: 'Warehouse Cam F6', date: '2025-01-09', alert: 'Improper lifting posture detected', risk: 'Back injury risk' },
  { id: 2, employee: 'Lisa Garcia', camera: 'Production Line Cam B2', date: '2025-01-09', alert: 'Extended reaching detected', risk: 'Shoulder strain risk' },
  { id: 3, employee: 'Anna Rodriguez', camera: 'Loading Dock Cam D4', date: '2025-01-08', alert: 'Awkward bending position', risk: 'Lower back injury risk' },
  { id: 4, employee: 'John Smith', camera: 'Manufacturing Cam I9', date: '2025-01-08', alert: 'Repetitive motion detected', risk: 'Repetitive strain injury' },
  { id: 5, employee: 'Mike Wilson', camera: 'Maintenance Bay Cam J10', date: '2025-01-07', alert: 'Overhead work posture', risk: 'Neck and shoulder strain' }
]

const mockUsers = [
  { id: 1, name: 'Admin User', email: 'admin@safevisor.com', role: 'Admin (IT)', lastLogin: '2025-01-09 14:30', status: 'Active' },
  { id: 2, name: 'Safety Manager', email: 'manager@safevisor.com', role: 'Manager', lastLogin: '2025-01-09 08:15', status: 'Active' },
  { id: 3, name: 'Assistant Manager', email: 'assistant@safevisor.com', role: 'AssistantManager', lastLogin: '2025-01-08 16:45', status: 'Active' },
  { id: 4, name: 'HSE Specialist', email: 'hse@safevisor.com', role: 'HSEExpert', lastLogin: '2025-01-09 09:30', status: 'Active' },
  { id: 5, name: 'Operations Lead', email: 'ops@safevisor.com', role: 'Manager', lastLogin: '2025-01-08 14:20', status: 'Inactive' }
]

// Simulate API delay for realistic experience
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms))

export const api = axios.create({ baseURL: 'https://api.safevisor.com' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Mock API functions that return local data
export const EmployeesAPI = {
  async list() {
    await delay()
    return mockEmployees
  },
}

export const CamerasAPI = {
  async list() {
    await delay()
    return mockCameras
  },
}

export const EventsAPI = {
  async violations() {
    await delay()
    return mockViolations
  },
  async pose() {
    await delay()
    return mockPoseAlerts
  },
}

export const UsersAPI = {
  async list() {
    await delay()
    return mockUsers
  },
}
