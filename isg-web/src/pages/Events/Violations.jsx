import React, { useEffect, useMemo, useState } from 'react'
import { EventsAPI } from '../../services/api'
import Table, { StatusBadge } from '../../components/Table'
import { SkeletonTable } from '../../components/Loading'
import Button from '../../components/Button'
import Icon from '../../components/Icon'
import { StatsGrid } from '../../components/StatsCard'

export default function Violations() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [employee, setEmployee] = useState('')
  const [camera, setCamera] = useState('')
  const [date, setDate] = useState('')

  useEffect(() => {
    (async () => {
      try {
        setError(null)
        setLoading(true)
        const resp = await EventsAPI.violations()
        const list = Array.isArray(resp?.violations) ? resp.violations : Array.isArray(resp) ? resp : []
        // Normalize to UI-friendly shape expected by the table
        const normalized = list.map((v) => ({
          id: v.id,
          employee: v.employee_name || v.employee || (v.employee_id != null ? `#${v.employee_id}` : '-'),
          camera: v.camera_name || v.camera || (v.camera_id != null ? `#${v.camera_id}` : '-'),
          date: v.created_at ? new Date(v.created_at).toLocaleDateString() : v.date || '-',
          type: v.violation_type || v.desc || '-',
          desc: v.description || v.desc || '-',
          severity: v.severity || 'medium',
          status: v.status || 'unresolved'
        }))
        setRows(normalized)
      } catch (e) {
        console.error('Failed to load violations', e)
        setError('Failed to load violations')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const filtered = useMemo(() => rows.filter((r) => {
    const emp = (r.employee || '').toLowerCase()
    const cam = (r.camera || '').toLowerCase()
    const empQ = employee.toLowerCase()
    const camQ = camera.toLowerCase()
    return (!employee || emp.includes(empQ)) && (!camera || cam.includes(camQ)) && (!date || r.date === date)
  }), [rows, employee, camera, date])

  const clearFilters = () => {
    setEmployee('')
    setCamera('')
    setDate('')
  }

  // Mock statistics
  const stats = [
    {
      title: 'Total Violations',
      value: rows.length.toString(),
      change: '+3 this week',
      changeType: 'negative',
      icon: 'violations',
      iconColor: 'text-warning-600'
    },
    {
      title: 'Resolved Today',
      value: '8',
      change: '+2 from yesterday',
      changeType: 'positive',
      icon: 'check',
      iconColor: 'text-success-600'
    },
    {
      title: 'Critical Violations',
      value: '2',
      change: 'Immediate attention',
      changeType: 'negative',
      icon: 'info',
      iconColor: 'text-danger-600'
    },
    {
      title: 'Average Resolution',
      value: '4.2h',
      change: '-30min improvement',
      changeType: 'positive',
      icon: 'clock',
      iconColor: 'text-primary-600'
    }
  ]

  const columns = [
    { 
      header: 'Employee', 
      accessor: 'employee',
      icon: 'person',
      cell: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-warning-100 rounded-full flex items-center justify-center">
            <Icon name="person" className="w-5 h-5 text-warning-600" />
          </div>
          <span className="font-medium">{row.employee}</span>
        </div>
      )
    },
    { 
      header: 'Camera', 
      accessor: 'camera',
      icon: 'cameras',
      cell: (row) => (
        <div className="flex items-center gap-2">
          <Icon name="cameras" className="w-4 h-4 text-neutral-400" />
          {row.camera}
        </div>
      )
    },
    { 
      header: 'Date', 
      accessor: 'date',
      icon: 'calendar'
    },
    { 
      header: 'Violation Type', 
      accessor: 'type',
      cell: (row) => (
        <span className="badge-warning">{row.type}</span>
      )
    },
    { 
      header: 'Status', 
      accessor: 'status',
      cell: (row) => (
        <StatusBadge status={row.status} />
      )
    }
  ]

  const actions = [
    {
      icon: 'view',
      title: 'View Details',
      onClick: (row) => console.log('View violation:', row),
      className: 'text-primary-600 hover:text-primary-700'
    },
    {
      icon: 'check',
      title: 'Resolve Violation',
      onClick: (row) => console.log('Resolve violation:', row),
      className: 'text-success-600 hover:text-success-700'
    }
  ]

  return (
    <div className="space-y-6 animate-fade-in-custom">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
            <Icon name="violations" className="w-8 h-8 text-warning-600" />
            PPE Violations
          </h1>
          <p className="text-neutral-600 mt-1">
            Monitor and manage personal protective equipment violations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" icon="document" size="sm">
            Export Report
          </Button>
          <Button variant="primary" icon="add">
            Create Alert
          </Button>
        </div>
      </div>

      {/* Statistics */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="stat-card">
              <div className="skeleton-text w-16 mb-2" />
              <div className="skeleton-title w-20 mb-3" />
              <div className="skeleton-text w-12" />
            </div>
          ))}
        </div>
      ) : (
        <StatsGrid stats={stats} />
      )}

      {/* Filters */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Icon name="search" className="w-5 h-5 text-primary-600" />
          Filter Violations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="person" className="w-5 h-5 text-neutral-400" />
            </div>
            <input 
              className="input pl-10" 
              placeholder="Filter by employee" 
              value={employee} 
              onChange={(e) => setEmployee(e.target.value)} 
            />
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="cameras" className="w-5 h-5 text-neutral-400" />
            </div>
            <input 
              className="input pl-10" 
              placeholder="Filter by camera" 
              value={camera} 
              onChange={(e) => setCamera(e.target.value)} 
            />
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="calendar" className="w-5 h-5 text-neutral-400" />
            </div>
            <input 
              className="input pl-10" 
              type="date" 
              value={date} 
              onChange={(e) => setDate(e.target.value)} 
            />
          </div>
          <Button variant="secondary" onClick={clearFilters} icon="close">
            Clear Filters
          </Button>
        </div>
        {(employee || camera || date) && (
          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-neutral-600">
              Showing {filtered.length} of {rows.length} violations
            </span>
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

      {/* Violations Table */}
      {loading ? (
        <SkeletonTable rows={10} cols={5} />
      ) : (
        <Table
          columns={columns}
          data={filtered}
          actions={actions}
          empty={
            employee || camera || date ? 
            `No violations found matching your filters` : 
            'No violations found. This is great news for workplace safety!'
          }
        />
      )}
    </div>
  )
}
