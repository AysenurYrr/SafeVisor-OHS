import React, { useEffect, useMemo, useState } from 'react'
import { EmployeesAPI } from '../services/api'
import Table, { StatusBadge } from '../components/Table'
import { SkeletonTable } from '../components/Loading'
import Button from '../components/Button'
import Icon from '../components/Icon'

export default function Employees() {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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

  const handleAddEmployee = () => {
    // TODO: Implement add employee modal/page
    console.log('Add employee clicked')
  }

  const handleEditEmployee = (employee) => {
    // TODO: Implement edit employee modal/page
    console.log('Edit employee:', employee)
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
        return (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <Icon name="person" className="w-5 h-5 text-primary-600" />
            </div>
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
    {
      icon: 'edit',
      title: 'Edit Employee',
      onClick: handleEditEmployee,
      className: 'text-neutral-600 hover:text-neutral-700'
    }
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
          <Button variant="primary" icon="add" onClick={handleAddEmployee}>
            Add Employee
          </Button>
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
    </div>
  )
}
