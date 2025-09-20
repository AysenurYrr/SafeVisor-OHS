import React, { useEffect, useMemo, useState } from 'react'
import { EmployeesAPI } from '../services/api'
import Table from '../components/Table'

export default function Employees() {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [departmentFilter, setDepartmentFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await EmployeesAPI.list()
      setList(data)
      setLoading(false)
    })()
  }, [])

  const departments = useMemo(() => {
    const depts = [...new Set(list.map(e => e.department))].sort()
    return depts
  }, [list])

  const filtered = useMemo(() => list.filter(e => {
    const matchesSearch = e.name.toLowerCase().includes(q.toLowerCase()) || 
                         e.email.toLowerCase().includes(q.toLowerCase())
    const matchesDepartment = !departmentFilter || e.department === departmentFilter
    return matchesSearch && matchesDepartment
  }), [list, q, departmentFilter])

  const getDepartmentColor = (department) => {
    const colors = {
      'Manufacturing': 'bg-blue-100 text-blue-800',
      'Quality Control': 'bg-green-100 text-green-800',
      'Maintenance': 'bg-yellow-100 text-yellow-800',
      'Operations': 'bg-purple-100 text-purple-800',
      'Safety': 'bg-red-100 text-red-800',
      'Engineering': 'bg-indigo-100 text-indigo-800',
      'Production': 'bg-orange-100 text-orange-800',
      'Logistics': 'bg-teal-100 text-teal-800',
    }
    return colors[department] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-600 mt-1">Manage your workforce and track employee information</p>
        </div>
        <button className="btn bg-green-600 hover:bg-green-700">
          <span className="text-lg mr-2">+</span>
          Add Employee
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4 border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Total Employees</div>
          <div className="text-2xl font-bold text-gray-900">{list.length}</div>
        </div>
        <div className="card p-4 border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Departments</div>
          <div className="text-2xl font-bold text-gray-900">{departments.length}</div>
        </div>
        <div className="card p-4 border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">Active Today</div>
          <div className="text-2xl font-bold text-gray-900">{Math.floor(list.length * 0.85)}</div>
        </div>
        <div className="card p-4 border-l-4 border-red-500">
          <div className="text-sm text-gray-600">Safety Training Due</div>
          <div className="text-2xl font-bold text-gray-900">{Math.floor(list.length * 0.15)}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">Search Employees</label>
            <input 
              className="input" 
              placeholder="Search by name or email..." 
              value={q} 
              onChange={(e) => setQ(e.target.value)} 
            />
          </div>
          <div>
            <label className="label">Filter by Department</label>
            <select 
              className="input" 
              value={departmentFilter} 
              onChange={(e) => setDepartmentFilter(e.target.value)}
            >
              <option value="">All Departments</option>
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
        </div>
        {(q || departmentFilter) && (
          <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
            <span>Showing {filtered.length} of {list.length} employees</span>
            {(q || departmentFilter) && (
              <button 
                onClick={() => { setQ(''); setDepartmentFilter('') }}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Clear filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* Employee Table */}
      {loading ? (
        <div className="card p-6 text-center">
          <div className="animate-pulse">Loading employees...</div>
        </div>
      ) : (
        <Table
          columns={[
            { 
              header: 'Employee', 
              accessor: 'name',
              cell: (row) => (
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-medium">
                    {row.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{row.name}</div>
                    <div className="text-sm text-gray-500">{row.email}</div>
                  </div>
                </div>
              )
            },
            { 
              header: 'Department', 
              accessor: 'department',
              cell: (row) => (
                <span className={`badge ${getDepartmentColor(row.department)}`}>
                  {row.department}
                </span>
              )
            },
            { 
              header: 'Company', 
              accessor: 'company',
              cell: (row) => (
                <div className="text-sm text-gray-700">{row.company}</div>
              )
            },
            { 
              header: 'Status', 
              accessor: 'status',
              cell: (row) => {
                // Simulate random status for demo
                const statuses = ['Active', 'Training', 'On Leave']
                const status = statuses[row.id % 3]
                const statusColors = {
                  'Active': 'bg-green-100 text-green-800',
                  'Training': 'bg-yellow-100 text-yellow-800',
                  'On Leave': 'bg-gray-100 text-gray-800'
                }
                return (
                  <span className={`badge ${statusColors[status]}`}>
                    {status}
                  </span>
                )
              }
            },
            {
              header: 'Actions',
              accessor: 'actions',
              cell: (row) => (
                <div className="flex items-center gap-2">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">Edit</button>
                  <button className="text-gray-600 hover:text-gray-800 text-sm">View</button>
                </div>
              )
            }
          ]}
          data={filtered}
          empty="No employees found. Try adjusting your search or filters."
        />
      )}
    </div>
  )
}
