import React, { useEffect, useMemo, useState } from 'react'
import { DepartmentsAPI } from '../services/api'
import Table from '../components/Table'
import { SkeletonTable } from '../components/Loading'
import Button from '../components/Button'
import Icon from '../components/Icon'

export default function Departments() {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAdd, setShowAdd] = useState(false)
  const [editDept, setEditDept] = useState(null)
  const [form, setForm] = useState({ name: '', description: '', is_active: true })

  const user = useMemo(() => {
    try { return JSON.parse(localStorage.getItem('user') || '{}') } catch { return {} }
  }, [])
  const roleNames = useMemo(() => {
    const roles = user?.roles || []
    const single = user?.role?.name ? [user.role.name] : []
    return [...single, ...roles.map(r => r.name)].map(r => (r || '').toUpperCase())
  }, [user])
  const canManage = roleNames.includes('ADMIN')

  useEffect(() => {
    (async () => {
      try {
        setError(null)
        setLoading(true)
        const data = await DepartmentsAPI.list()
        setList(Array.isArray(data) ? data : [])
      } catch (e) {
        console.error('Failed to load departments', e)
        setError('Failed to load departments. Please try again.')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const filtered = useMemo(() => list.filter((d) => {
    const name = d.name || ''
    const description = d.description || ''
    const searchTerm = q.toLowerCase()
    
    return name.toLowerCase().includes(searchTerm) || 
           description.toLowerCase().includes(searchTerm)
  }), [list, q])

  const handleAddDepartment = () => {
    setForm({ name: '', description: '', is_active: true })
    setShowAdd(true)
  }

  const handleEditDepartment = (dept) => {
    setForm({ name: dept.name, description: dept.description || '', is_active: dept.is_active })
    setEditDept(dept)
  }

  const handleSaveDepartment = async () => {
    try {
      if (!form.name.trim()) {
        alert('Department name is required')
        return
      }

      if (editDept) {
        const updated = await DepartmentsAPI.update(editDept.id, form)
        setList(list.map(d => d.id === updated.id ? updated : d))
        setEditDept(null)
      } else {
        const created = await DepartmentsAPI.create(form)
        setList([created, ...list])
        setShowAdd(false)
      }
      setForm({ name: '', description: '', is_active: true })
    } catch (e) {
      console.error('Failed to save department', e)
      alert('Failed to save department: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleDeleteDepartment = async (dept) => {
    if (!window.confirm(`Are you sure you want to delete department "${dept.name}"?${dept.employee_count > 0 ? '\n\nThis department has ' + dept.employee_count + ' employees. It will be marked as inactive instead of deleted.' : ''}`)) {
      return
    }
    
    try {
      await DepartmentsAPI.delete(dept.id)
      setList(list.filter(d => d.id !== dept.id))
    } catch (e) {
      console.error('Failed to delete department', e)
      alert('Failed to delete department: ' + (e.response?.data?.detail || e.message))
    }
  }

  const columns = [
    { 
      header: 'Department', 
      accessor: 'name', 
      icon: 'building',
      cell: (row) => (
        <div className="flex items-center gap-2">
          <Icon name="building" className="w-5 h-5 text-primary-600" />
          <span className="font-medium text-neutral-900">{row.name}</span>
        </div>
      )
    },
    { 
      header: 'Description', 
      accessor: 'description',
      cell: (row) => (
        <span className="text-neutral-600">{row.description || 'No description'}</span>
      )
    },
    {
      header: 'Employees',
      accessor: 'employee_count',
      cell: (row) => (
        <span className="badge-primary">{row.employee_count || 0}</span>
      )
    },
    {
      header: 'Positions',
      accessor: 'position_count',
      cell: (row) => (
        <span className="badge-secondary">{row.position_count || 0}</span>
      )
    },
    {
      header: 'Status',
      accessor: 'is_active',
      cell: (row) => (
        <span className={`badge ${row.is_active ? 'badge-success' : 'badge-danger'}`}>
          {row.is_active ? 'Active' : 'Inactive'}
        </span>
      )
    }
  ]

  const actions = canManage ? [
    {
      icon: 'edit',
      title: 'Edit Department',
      onClick: handleEditDepartment,
      className: 'text-neutral-600 hover:text-neutral-700'
    },
    {
      icon: 'delete',
      title: 'Delete Department',
      onClick: handleDeleteDepartment,
      className: 'text-danger-600 hover:text-danger-700'
    }
  ] : []

  return (
    <div className="space-y-6">
      {/* Search and Actions */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="search" className="w-5 h-5 text-neutral-400" />
            </div>
            <input 
              className="input pl-10" 
              placeholder="Search departments..." 
              value={q} 
              onChange={(e) => setQ(e.target.value)} 
            />
          </div>
        </div>
        {canManage && (
          <Button variant="primary" icon="add" onClick={handleAddDepartment}>
            Add Department
          </Button>
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

      {/* Table */}
      {loading ? (
        <SkeletonTable rows={5} cols={5} />
      ) : (
        <Table
          columns={columns}
          data={filtered}
          actions={actions}
          empty={
            q ? 
            `No departments found matching "${q}"` : 
            'No departments found. Add your first department to get started.'
          }
        />
      )}

      {/* Add/Edit Modal */}
      {(showAdd || editDept) && canManage && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3 className="text-xl font-semibold">{editDept ? 'Edit Department' : 'Add Department'}</h3>
              <button onClick={() => { setShowAdd(false); setEditDept(null); setForm({ name: '', description: '', is_active: true }) }} className="icon-button">
                <Icon name="close" />
              </button>
            </div>
            <div className="modal-body space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Department Name *</label>
                <input 
                  className="input" 
                  placeholder="e.g., Engineering, Manufacturing" 
                  value={form.name} 
                  onChange={e => setForm({ ...form, name: e.target.value })} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
                <textarea 
                  className="input" 
                  rows="3" 
                  placeholder="Optional description of the department" 
                  value={form.description} 
                  onChange={e => setForm({ ...form, description: e.target.value })} 
                />
              </div>
              <div className="flex items-center gap-2">
                <input 
                  type="checkbox" 
                  id="is_active" 
                  checked={form.is_active} 
                  onChange={e => setForm({ ...form, is_active: e.target.checked })} 
                  className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="is_active" className="text-sm font-medium text-neutral-700">Active</label>
              </div>
            </div>
            <div className="modal-footer">
              <Button variant="secondary" onClick={() => { setShowAdd(false); setEditDept(null); setForm({ name: '', description: '', is_active: true }) }}>Cancel</Button>
              <Button variant="primary" onClick={handleSaveDepartment}>Save</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
