import React, { useEffect, useMemo, useState } from 'react'
import { EventsAPI } from '../../services/api'
import Table from '../../components/Table'
import StatsCard from '../../components/StatsCard'

export default function Violations() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [employee, setEmployee] = useState('')
  const [camera, setCamera] = useState('')
  const [date, setDate] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await EventsAPI.violations()
      setRows(data)
      setLoading(false)
    })()
  }, [])

  // Calculate statistics
  const totalViolations = rows.length
  const todayViolations = rows.filter(r => r.date === '2025-01-09').length
  const criticalViolations = rows.filter(r => r.severity === 'Critical').length
  const highViolations = rows.filter(r => r.severity === 'High').length

  // Get unique values for filters
  const uniqueTypes = useMemo(() => [...new Set(rows.map(r => r.type))].sort(), [rows])
  const uniqueEmployees = useMemo(() => [...new Set(rows.map(r => r.employee))].sort(), [rows])
  const uniqueCameras = useMemo(() => [...new Set(rows.map(r => r.camera))].sort(), [rows])

  const filtered = useMemo(() => rows.filter(r => (
    (!employee || r.employee.toLowerCase().includes(employee.toLowerCase())) &&
    (!camera || r.camera.toLowerCase().includes(camera.toLowerCase())) &&
    (!date || r.date === date) &&
    (!severityFilter || r.severity === severityFilter) &&
    (!typeFilter || r.type === typeFilter)
  )), [rows, employee, camera, date, severityFilter, typeFilter])

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Critical': return 'bg-red-100 text-red-800'
      case 'High': return 'bg-orange-100 text-orange-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type) => {
    const icons = {
      'Hard Hat': '🪖',
      'Safety Goggles': '🥽',
      'Safety Vest': '🦺',
      'Gloves': '🧤',
      'Hair Net': '🧢',
      'Safety Shoes': '👟',
      'Respirator': '😷'
    }
    return icons[type] || '⚠️'
  }

  const clearFilters = () => {
    setEmployee('')
    setCamera('')
    setDate('')
    setSeverityFilter('')
    setTypeFilter('')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">PPE Violations</h1>
          <p className="text-gray-600 mt-1">Monitor and track Personal Protective Equipment violations</p>
        </div>
        <button className="btn bg-red-600 hover:bg-red-700">
          <span className="text-lg mr-2">📊</span>
          Generate Report
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Violations"
          value={totalViolations}
          subtitle="All time recorded"
          icon="⚠️"
          color="red"
        />
        <StatsCard
          title="Today's Violations"
          value={todayViolations}
          subtitle="Current day incidents"
          icon="📅"
          trend="2 less than yesterday"
          trendDirection="down"
          color="yellow"
        />
        <StatsCard
          title="Critical Issues"
          value={criticalViolations}
          subtitle="Immediate attention needed"
          icon="🚨"
          trend="Requires urgent action"
          trendDirection="up"
          color="red"
        />
        <StatsCard
          title="High Priority"
          value={highViolations}
          subtitle="High severity violations"
          icon="⚡"
          trend="Monitor closely"
          trendDirection="flat"
          color="yellow"
        />
      </div>

      {/* Filters */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Violations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="label">Search Employee</label>
            <select 
              className="input" 
              value={employee} 
              onChange={(e) => setEmployee(e.target.value)}
            >
              <option value="">All Employees</option>
              {uniqueEmployees.map(emp => (
                <option key={emp} value={emp}>{emp}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Filter by Camera</label>
            <select 
              className="input" 
              value={camera} 
              onChange={(e) => setCamera(e.target.value)}
            >
              <option value="">All Cameras</option>
              {uniqueCameras.map(cam => (
                <option key={cam} value={cam}>{cam}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Filter by Date</label>
            <input 
              className="input" 
              type="date" 
              value={date} 
              onChange={(e) => setDate(e.target.value)} 
            />
          </div>
          <div>
            <label className="label">Filter by Severity</label>
            <select 
              className="input" 
              value={severityFilter} 
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          <div>
            <label className="label">Filter by PPE Type</label>
            <select 
              className="input" 
              value={typeFilter} 
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="">All Types</option>
              {uniqueTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button 
              className="btn btn-secondary w-full" 
              onClick={clearFilters}
            >
              Clear All Filters
            </button>
          </div>
        </div>
        {(employee || camera || date || severityFilter || typeFilter) && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <div className="text-sm text-blue-900">
              Showing {filtered.length} of {totalViolations} violations
              {filtered.length !== totalViolations && (
                <button 
                  onClick={clearFilters}
                  className="ml-2 text-blue-600 hover:text-blue-800 underline"
                >
                  Show all
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Violations Table */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Violation Records</h2>
        {loading ? (
          <div className="card p-6 text-center">
            <div className="animate-pulse">Loading violations...</div>
          </div>
        ) : (
          <Table
            columns={[
              { 
                header: 'Employee', 
                accessor: 'employee',
                cell: (row) => (
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center text-red-600 font-medium">
                      {row.employee.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="font-medium text-gray-900">{row.employee}</div>
                  </div>
                )
              },
              { 
                header: 'PPE Type', 
                accessor: 'type',
                cell: (row) => (
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getTypeIcon(row.type)}</span>
                    <span className="text-sm font-medium">{row.type}</span>
                  </div>
                )
              },
              { 
                header: 'Severity', 
                accessor: 'severity',
                cell: (row) => (
                  <span className={`badge ${getSeverityColor(row.severity)}`}>
                    {row.severity}
                  </span>
                )
              },
              { header: 'Date', accessor: 'date' },
              { 
                header: 'Location', 
                accessor: 'camera',
                cell: (row) => (
                  <div className="text-sm text-gray-700">{row.camera}</div>
                )
              },
              { 
                header: 'Description', 
                accessor: 'desc',
                cell: (row) => (
                  <div className="text-sm text-gray-600 max-w-xs truncate" title={row.desc}>
                    {row.desc}
                  </div>
                )
              },
              {
                header: 'Actions',
                accessor: 'actions',
                cell: (row) => (
                  <div className="flex items-center gap-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">View</button>
                    <button className="text-red-600 hover:text-red-800 text-sm">Report</button>
                  </div>
                )
              }
            ]}
            data={filtered}
            empty="No violations found. Try adjusting your filters."
          />
        )}
      </div>
    </div>
  )
}
