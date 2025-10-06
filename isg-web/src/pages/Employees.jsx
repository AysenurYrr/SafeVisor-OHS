import React, { useEffect, useMemo, useState } from 'react'
import { EmployeesAPI } from '../services/api'
import Table, { StatusBadge } from '../components/Table'
import { SkeletonTable } from '../components/Loading'
import Button from '../components/Button'
import Icon from '../components/Icon'
import EditEmployeeModal from '../components/EditEmployeeModal'

export default function Employees() {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAdd, setShowAdd] = useState(false)
  const [editEmployee, setEditEmployee] = useState(null)
  const [form, setForm] = useState({ 
    employee_id: '', 
    first_name: '', 
    last_name: '', 
    email: '', 
    phone: '', 
    department: '', 
    position: '', 
    hire_date: '', 
    emergency_contact: '',
    emergency_phone: '', 
    notes: '' 
  })
  const [files, setFiles] = useState([null, null, null])
  const [filePreviews, setFilePreviews] = useState([null, null, null])

  const user = useMemo(() => {
    try { return JSON.parse(localStorage.getItem('user') || '{}') } catch { return {} }
  }, [])
  const roleNames = useMemo(() => {
    const roles = user?.roles || []
    const single = user?.role?.name ? [user.role.name] : []
    return [...single, ...roles.map(r => r.name)].map(r => (r || '').toUpperCase())
  }, [user])
  const canManage = roleNames.includes('ADMIN')  // Only Admin can manage

  useEffect(() => {
    (async () => {
      try {
        setError(null)
        setLoading(true)
        const resp = await EmployeesAPI.list()
        // Backend returns { employees, total, page, per_page }
        const employees = Array.isArray(resp?.employees) ? resp.employees : Array.isArray(resp) ? resp : []
        setList(employees)
      } catch (e) {
        console.error('Failed to load employees', e)
        setError('Failed to load employees. Please try again.')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const filtered = useMemo(() => list.filter((e) => {
    const fullName = `${e.first_name ?? ''} ${e.last_name ?? ''}`.trim()
    const email = e.email ?? ''
    const department = e.department ?? ''
    const position = e.position ?? ''
    const searchTerm = q.toLowerCase()
    
    return fullName.toLowerCase().includes(searchTerm) || 
           email.toLowerCase().includes(searchTerm) ||
           department.toLowerCase().includes(searchTerm) ||
           position.toLowerCase().includes(searchTerm)
  }), [list, q])

  const handleAddEmployee = () => setShowAdd(true)

  const handleEditEmployee = (employee) => {
    setEditEmployee(employee)
  }

  const handleUpdateEmployee = (updated) => {
    setList(list.map(emp => emp.id === updated.id ? updated : emp))
  }

  const handleDeleteEmployee = async (employee) => {
    if (!window.confirm(`Are you sure you want to delete ${employee.first_name} ${employee.last_name}?`)) {
      return
    }
    
    try {
      await EmployeesAPI.delete(employee.uuid)
      setList(list.filter(emp => emp.id !== employee.id))
    } catch (e) {
      console.error('Failed to delete employee', e)
      alert('Failed to delete employee: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleViewEmployee = (employee) => {
    // TODO: Implement view employee details
    console.log('View employee:', employee)
  }

  const columns = [
    { 
      header: 'Employee', 
      accessor: 'full_name', 
      key: 'name',
      icon: 'person',
      cell: (row) => {
        const fullName = `${row.first_name ?? ''} ${row.last_name ?? ''}`.trim() || 'Unknown'
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        const photoUrl = row.photo_front_path 
          ? `${API_BASE_URL}${row.photo_front_path}` 
          : `https://i.pravatar.cc/150?img=${Math.abs(row.id % 70)}`
        
        return (
          <div className="flex items-center gap-3">
            <img 
              src={photoUrl} 
              alt={fullName}
              className="w-10 h-10 rounded-full object-cover border-2 border-primary-100"
              onError={(e) => {
                // Fallback to placeholder if image fails to load
                e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=random`
              }}
            />
            <div>
              <div className="font-medium text-neutral-900">{fullName}</div>
              <div className="text-sm text-neutral-600">{row.email || 'No email'}</div>
            </div>
          </div>
        )
      }
    },
    { 
      header: 'Department', 
      accessor: 'department',
      icon: 'building',
      cell: (row) => (
        <div className="flex items-center gap-2">
          <Icon name="building" className="w-4 h-4 text-neutral-400" />
          <span>{row.department || 'Unassigned'}</span>
        </div>
      )
    },
    { 
      header: 'Position', 
      accessor: 'position',
      icon: 'tag',
      cell: (row) => (
        <span className="badge-primary">{row.position || 'No position'}</span>
      )
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (row) => (
        <StatusBadge status={row.status || 'active'} />
      )
    },
    {
      header: 'Last Activity',
      accessor: 'last_activity',
      icon: 'clock',
      cell: (row) => (
        <div className="flex items-center gap-2 text-sm text-neutral-600">
          <Icon name="clock" className="w-4 h-4" />
          {row.last_activity || 'Never'}
        </div>
      )
    }
  ]

  const actions = [
    {
      icon: 'view',
      title: 'View Details',
      onClick: handleViewEmployee,
      className: 'text-primary-600 hover:text-primary-700'
    },
    canManage ? {
      icon: 'edit',
      title: 'Edit Employee',
      onClick: handleEditEmployee,
      className: 'text-neutral-600 hover:text-neutral-700'
    } : null,
    canManage ? {
      icon: 'delete',
      title: 'Delete Employee',
      onClick: handleDeleteEmployee,
      className: 'text-danger-600 hover:text-danger-700'
    } : null
  ]

  return (
    <div className="space-y-6 animate-fade-in-custom">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
            <Icon name="employees" className="w-8 h-8 text-primary-600" />
            Employee Management
          </h1>
          <p className="text-neutral-600 mt-1">
            Manage your workforce and track employee information
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" icon="document" size="sm">
            Export List
          </Button>
          {canManage && (
            <Button variant="primary" icon="add" onClick={handleAddEmployee}>
            Add Employee
            </Button>
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Total Employees</p>
              <p className="stat-value">{list.length}</p>
            </div>
            <Icon name="employees" className="w-8 h-8 text-primary-600" />
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Active Today</p>
              <p className="stat-value">{Math.floor(list.length * 0.85)}</p>
            </div>
            <Icon name="check" className="w-8 h-8 text-success-600" />
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Departments</p>
              <p className="stat-value">{new Set(list.map(e => e.department)).size}</p>
            </div>
            <Icon name="building" className="w-8 h-8 text-warning-600" />
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">New This Month</p>
              <p className="stat-value">12</p>
            </div>
            <Icon name="add" className="w-8 h-8 text-neutral-600" />
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Icon name="search" className="w-5 h-5 text-neutral-400" />
              </div>
              <input 
                className="input pl-10" 
                placeholder="Search employees by name, email, department, or position..." 
                value={q} 
                onChange={(e) => setQ(e.target.value)} 
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" icon="tag">
              Filter by Department
            </Button>
            <Button variant="secondary" size="sm" icon="settings">
              More Filters
            </Button>
          </div>
        </div>
        {q && (
          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-neutral-600">
              Showing {filtered.length} of {list.length} employees
            </span>
            {q && (
              <button 
                onClick={() => setQ('')}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Clear search
              </button>
            )}
          </div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="card p-6">
          <div className="flex items-center gap-3 text-danger-600">
            <Icon name="info" className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Employee Table */}
      {loading ? (
        <SkeletonTable rows={10} cols={5} />
      ) : (
        <Table
          columns={columns}
          data={filtered}
          actions={actions}
          empty={
            q ? 
            `No employees found matching "${q}"` : 
            'No employees found. Add your first employee to get started.'
          }
        />
      )}

      {/* Add Employee Modal */}
      {showAdd && canManage && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3 className="text-xl font-semibold">Add Employee</h3>
              <button onClick={() => setShowAdd(false)} className="icon-button">
                <Icon name="close" />
              </button>
            </div>
            <div className="modal-body space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input className="input" placeholder="Employee ID" value={form.employee_id} onChange={e => setForm({ ...form, employee_id: e.target.value })} />
                <input className="input" placeholder="First Name *" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} />
                <input className="input" placeholder="Last Name *" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} />
                <input className="input" placeholder="Email *" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
                <input className="input" placeholder="Phone" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
                <input className="input" placeholder="Department *" value={form.department} onChange={e => setForm({ ...form, department: e.target.value })} />
                <input className="input" placeholder="Position *" value={form.position} onChange={e => setForm({ ...form, position: e.target.value })} />
                <input className="input" type="date" placeholder="Hire Date *" value={form.hire_date} onChange={e => setForm({ ...form, hire_date: e.target.value })} />
                <input className="input" placeholder="Emergency Contact Name" value={form.emergency_contact} onChange={e => setForm({ ...form, emergency_contact: e.target.value })} />
                <input className="input" placeholder="Emergency Phone" value={form.emergency_phone} onChange={e => setForm({ ...form, emergency_phone: e.target.value })} />
              </div>
              <div>
                <textarea className="input" rows="3" placeholder="Notes" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
              </div>
              <div className="space-y-3">
                <label className="block text-sm font-medium text-neutral-700">
                  Profile Photos (3 Required) *
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {['Front Profile', 'Left Profile', 'Right Profile'].map((label, i) => (
                    <div key={i} className="space-y-2">
                      <label className="text-xs text-neutral-600">{label}</label>
                      {filePreviews[i] && (
                        <div className="relative">
                          <img 
                            src={filePreviews[i]} 
                            alt={label}
                            className="w-full h-32 object-cover rounded border-2 border-primary-200"
                          />
                          <button
                            type="button"
                            onClick={() => {
                              const newFiles = [...files]
                              const newPreviews = [...filePreviews]
                              newFiles[i] = null
                              newPreviews[i] = null
                              setFiles(newFiles)
                              setFilePreviews(newPreviews)
                            }}
                            className="absolute top-1 right-1 bg-danger-600 text-white rounded-full p-1 hover:bg-danger-700"
                          >
                            <Icon name="close" className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                      <input 
                        type="file" 
                        accept="image/*" 
                        className="block w-full text-sm text-neutral-600
                          file:mr-4 file:py-2 file:px-4
                          file:rounded file:border-0
                          file:text-sm file:font-semibold
                          file:bg-primary-50 file:text-primary-700
                          hover:file:bg-primary-100"
                        onChange={(e) => {
                          const file = e.target.files?.[0] || null
                          const newFiles = [...files]
                          newFiles[i] = file
                          setFiles(newFiles)
                          
                          // Create preview
                          if (file) {
                            const reader = new FileReader()
                            reader.onloadend = () => {
                              const newPreviews = [...filePreviews]
                              newPreviews[i] = reader.result
                              setFilePreviews(newPreviews)
                            }
                            reader.readAsDataURL(file)
                          } else {
                            const newPreviews = [...filePreviews]
                            newPreviews[i] = null
                            setFilePreviews(newPreviews)
                          }
                        }} 
                      />
                    </div>
                  ))}
                </div>
                <p className="text-xs text-neutral-500">
                  Please upload all three profile photos (front, left, and right view) to create an employee.
                </p>
              </div>
            </div>
            <div className="modal-footer">
              <Button variant="secondary" onClick={() => setShowAdd(false)}>Cancel</Button>
              <Button variant="primary" onClick={async () => {
                try {
                  // Validate required fields
                  if (!form.first_name || !form.last_name || !form.email || !form.department || !form.position) {
                    alert('Please fill in all required fields (marked with *)')
                    return
                  }
                  
                  // Validate that all 3 photos are uploaded
                  if (!files[0] || !files[1] || !files[2]) {
                    alert('All three photos (Front, Left, and Right Profile) are required')
                    return
                  }
                  
                  const data = new FormData()
                  data.append('first_name', form.first_name)
                  data.append('last_name', form.last_name)
                  data.append('email', form.email)
                  if (form.employee_id) data.append('employee_id', form.employee_id)
                  if (form.phone) data.append('phone', form.phone)
                  if (form.department) data.append('department', form.department)
                  if (form.position) data.append('position', form.position)
                  if (form.hire_date) data.append('hire_date', form.hire_date)
                  if (form.emergency_phone) data.append('emergency_phone', form.emergency_phone)
                  if (form.emergency_contact) data.append('emergency_contact', form.emergency_contact)
                  if (form.notes) data.append('notes', form.notes)
                  
                  // Append photos with specific field names
                  data.append('photo_front', files[0])
                  data.append('photo_left', files[1])
                  data.append('photo_right', files[2])
                  
                  const created = await EmployeesAPI.createMultipart(data)
                  setList([created, ...list])
                  setShowAdd(false)
                  setForm({ 
                    employee_id: '', 
                    first_name: '', 
                    last_name: '', 
                    email: '', 
                    phone: '', 
                    department: '', 
                    position: '', 
                    hire_date: '', 
                    emergency_phone: '',
                    emergency_contact: '', 
                    notes: '' 
                  })
                  setFiles([null, null, null])
                  setFilePreviews([null, null, null])
                } catch (e) {
                  console.error('Failed to create employee', e)
                  const errorMsg = e.response?.data?.detail || e.message
                  alert('Failed to create employee: ' + errorMsg)
                }
              }}>Save</Button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Employee Modal */}
      {editEmployee && canManage && (
        <EditEmployeeModal
          employee={editEmployee}
          onClose={() => setEditEmployee(null)}
          onUpdate={handleUpdateEmployee}
        />
      )}
    </div>
  )
}
