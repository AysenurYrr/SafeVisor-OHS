import React, { useEffect, useMemo, useState } from 'react'
import { PositionsAPI, DepartmentsAPI } from '../services/api'
import Table from '../components/Table'
import { SkeletonTable } from '../components/Loading'
import Button from '../components/Button'
import Icon from '../components/Icon'

export default function Positions() {
  const [list, setList] = useState([])
  const [departments, setDepartments] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAdd, setShowAdd] = useState(false)
  const [editPos, setEditPos] = useState(null)
  const [form, setForm] = useState({ name: '', description: '', department_id: null, is_active: true })

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
        const [posData, deptData] = await Promise.all([
          PositionsAPI.list(),
          DepartmentsAPI.list()
        ])
        setList(Array.isArray(posData) ? posData : [])
        setDepartments(Array.isArray(deptData) ? deptData : [])
      } catch (e) {
        console.error('Failed to load positions', e)
        setError('Failed to load positions. Please try again.')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const filtered = useMemo(() => list.filter((p) => {
    const name = p.name || ''
    const description = p.description || ''
    const deptName = p.department_name || ''
    const searchTerm = q.toLowerCase()
    
    return name.toLowerCase().includes(searchTerm) || 
           description.toLowerCase().includes(searchTerm) ||
           deptName.toLowerCase().includes(searchTerm)
  }), [list, q])

  const handleAddPosition = () => {
    setForm({ name: '', description: '', department_id: null, is_active: true })
    setShowAdd(true)
  }

  const handleEditPosition = (pos) => {
    setForm({ 
      name: pos.name, 
      description: pos.description || '', 
      department_id: pos.department_id, 
      is_active: pos.is_active 
    })
    setEditPos(pos)
  }

  const handleSavePosition = async () => {
    try {
      if (!form.name.trim()) {
        alert('Position name is required')
        return
      }

      if (editPos) {
        const updated = await PositionsAPI.update(editPos.id, form)
        setList(list.map(p => p.id === updated.id ? updated : p))
        setEditPos(null)
      } else {
        const created = await PositionsAPI.create(form)
        setList([created, ...list])
        setShowAdd(false)
      }
      setForm({ name: '', description: '', department_id: null, is_active: true })
    } catch (e) {
      console.error('Failed to save position', e)
      alert('Failed to save position: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleDeletePosition = async (pos) => {
    if (!window.confirm(`Are you sure you want to delete position "${pos.name}"?${pos.employee_count > 0 ? '\n\nThis position has ' + pos.employee_count + ' employees. It will be marked as inactive instead of deleted.' : ''}`)) {
      return
    }
    
    try {
      await PositionsAPI.delete(pos.id)
      setList(list.filter(p => p.id !== pos.id))
    } catch (e) {
      console.error('Failed to delete position', e)
      alert('Failed to delete position: ' + (e.response?.data?.detail || e.message))
    }
  }

  const columns = [
    { 
      header: 'Position', 
      accessor: 'name', 
      icon: 'tag',
      cell: (row) => (
        <div className="flex items-center gap-2">
          <Icon name="tag" className="w-5 h-5 text-primary-600" />
          <span className="font-medium text-neutral-900">{row.name}</span>
        </div>
      )
    },
    { 
      header: 'Department', 
      accessor: 'department_name',
      cell: (row) => (
        <span className="text-neutral-600">{row.department_name || 'No department'}</span>
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
      title: 'Edit Position',
      onClick: handleEditPosition,
      className: 'text-neutral-600 hover:text-neutral-700'
    },
    {
      icon: 'delete',
      title: 'Delete Position',
      onClick: handleDeletePosition,
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
              placeholder="Search positions..." 
              value={q} 
              onChange={(e) => setQ(e.target.value)} 
            />
          </div>
        </div>
        {canManage && (
          <Button variant="primary" icon="add" onClick={handleAddPosition}>
            Add Position
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
            `No positions found matching "${q}"` : 
            'No positions found. Add your first position to get started.'
          }
        />
      )}

      {/* Add/Edit Modal */}
      {(showAdd || editPos) && canManage && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3 className="text-xl font-semibold">{editPos ? 'Edit Position' : 'Add Position'}</h3>
              <button onClick={() => { setShowAdd(false); setEditPos(null); setForm({ name: '', description: '', department_id: null, is_active: true }) }} className="icon-button">
                <Icon name="close" />
              </button>
            </div>
            <div className="modal-body space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Position Name *</label>
                <input 
                  className="input" 
                  placeholder="e.g., Software Engineer, Technician" 
                  value={form.name} 
                  onChange={e => setForm({ ...form, name: e.target.value })} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Department</label>
                <select 
                  className="input" 
                  value={form.department_id || ''} 
                  onChange={e => setForm({ ...form, department_id: e.target.value ? parseInt(e.target.value) : null })}
                >
                  <option value="">Select department (optional)</option>
                  {departments.filter(d => d.is_active).map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
                <textarea 
                  className="input" 
                  rows="3" 
                  placeholder="Optional description of the position" 
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
              <Button variant="secondary" onClick={() => { setShowAdd(false); setEditPos(null); setForm({ name: '', description: '', department_id: null, is_active: true }) }}>Cancel</Button>
              <Button variant="primary" onClick={handleSavePosition}>Save</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
