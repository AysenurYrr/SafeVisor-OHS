import axios from 'axios'

// For demo, use jsonplaceholder and build mock-like helpers
export const api = axios.create({ baseURL: 'https://jsonplaceholder.typicode.com' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Helper functions to simulate domain data
export const EmployeesAPI = {
  async list() {
    const { data } = await api.get('/users')
    return data.map(u => ({ id: u.id, name: u.name, email: u.email, company: u.company?.name }))
  },
}

export const CamerasAPI = {
  async list() {
    const { data } = await api.get('/albums')
    return data.slice(0, 10).map(a => ({ id: a.id, name: `Camera ${a.id}`, location: `Zone ${a.userId}`, status: a.id % 2 ? 'Online' : 'Offline' }))
  },
}

export const EventsAPI = {
  async violations() {
    const { data } = await api.get('/posts')
    return data.slice(0, 20).map(p => ({ id: p.id, employee: `Emp ${p.userId}`, camera: `Cam ${p.userId}`, date: new Date().toISOString().slice(0,10), type: 'PPE', desc: p.title }))
  },
  async pose() {
    const { data } = await api.get('/comments')
    return data.slice(0, 20).map(c => ({ id: c.id, employee: `Emp ${c.postId}`, camera: `Cam ${c.postId}`, date: new Date().toISOString().slice(0,10), alert: c.name }))
  },
}

export const UsersAPI = {
  async list() {
    const { data } = await api.get('/users')
    return data.map(u => ({ id: u.id, name: u.name, email: u.email, role: ['Admin (IT)','Manager','AssistantManager','HSEExpert'][u.id % 4] }))
  },
}
