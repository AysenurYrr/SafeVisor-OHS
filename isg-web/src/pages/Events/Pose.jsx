import React, { useEffect, useMemo, useState } from 'react'
import { EventsAPI } from '../../services/api'
import Table from '../../components/Table'
import StatsCard from '../../components/StatsCard'

export default function Pose() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [employeeFilter, setEmployeeFilter] = useState('')
  const [cameraFilter, setCameraFilter] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [riskFilter, setRiskFilter] = useState('')

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await EventsAPI.pose()
      setRows(data)
      setLoading(false)
    })()
  }, [])

  // Calculate statistics
  const totalAlerts = rows.length
  const todayAlerts = rows.filter(r => r.date === '2025-01-09').length
  const backInjuryRisks = rows.filter(r => r.risk.toLowerCase().includes('back')).length
  const repetitiveStrainRisks = rows.filter(r => r.risk.toLowerCase().includes('repetitive')).length

  // Get unique values for filters
  const uniqueEmployees = useMemo(() => [...new Set(rows.map(r => r.employee))].sort(), [rows])
  const uniqueCameras = useMemo(() => [...new Set(rows.map(r => r.camera))].sort(), [rows])
  const uniqueRisks = useMemo(() => [...new Set(rows.map(r => r.risk))].sort(), [rows])

  // Filter data
  const filteredData = useMemo(() => {
    return rows.filter(row => {
      const matchesEmployee = !employeeFilter || row.employee.toLowerCase().includes(employeeFilter.toLowerCase())
      const matchesCamera = !cameraFilter || row.camera.toLowerCase().includes(cameraFilter.toLowerCase())
      const matchesDate = !dateFilter || row.date === dateFilter
      const matchesRisk = !riskFilter || row.risk === riskFilter
      return matchesEmployee && matchesCamera && matchesDate && matchesRisk
    })
  }, [rows, employeeFilter, cameraFilter, dateFilter, riskFilter])

  const getRiskColor = (risk) => {
    if (risk.toLowerCase().includes('back') || risk.toLowerCase().includes('injury')) {
      return 'bg-red-100 text-red-800'
    } else if (risk.toLowerCase().includes('strain')) {
      return 'bg-yellow-100 text-yellow-800'
    } else if (risk.toLowerCase().includes('shoulder') || risk.toLowerCase().includes('neck')) {
      return 'bg-orange-100 text-orange-800'
    }
    return 'bg-blue-100 text-blue-800'
  }

  const getAlertIcon = (alert) => {
    if (alert.toLowerCase().includes('lifting')) return '🏋️'
    if (alert.toLowerCase().includes('reaching')) return '🤸'
    if (alert.toLowerCase().includes('bending')) return '🧘'
    if (alert.toLowerCase().includes('repetitive')) return '🔄'
    if (alert.toLowerCase().includes('overhead')) return '🙋'
    return '🏃'
  }

  const getRiskIcon = (risk) => {
    if (risk.toLowerCase().includes('back')) return '🦴'
    if (risk.toLowerCase().includes('shoulder')) return '💪'
    if (risk.toLowerCase().includes('neck')) return '🦒'
    if (risk.toLowerCase().includes('strain')) return '⚡'
    return '⚠️'
  }

  const clearFilters = () => {
    setEmployeeFilter('')
    setCameraFilter('')
    setDateFilter('')
    setRiskFilter('')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ergonomic Pose Alerts</h1>
          <p className="text-gray-600 mt-1">Monitor workplace ergonomics and prevent musculoskeletal injuries</p>
        </div>
        <button className="btn bg-purple-600 hover:bg-purple-700">
          <span className="text-lg mr-2">🏥</span>
          Ergonomic Assessment
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Alerts"
          value={totalAlerts}
          subtitle="Ergonomic incidents"
          icon="🏃"
          color="blue"
        />
        <StatsCard
          title="Today's Alerts"
          value={todayAlerts}
          subtitle="Current day incidents"
          icon="📅"
          trend="1 more than yesterday"
          trendDirection="up"
          color="yellow"
        />
        <StatsCard
          title="Back Injury Risk"
          value={backInjuryRisks}
          subtitle="Lifting & bending issues"
          icon="🦴"
          trend="High priority area"
          trendDirection="up"
          color="red"
        />
        <StatsCard
          title="Repetitive Strain"
          value={repetitiveStrainRisks}
          subtitle="Motion-related risks"
          icon="🔄"
          trend="Requires intervention"
          trendDirection="flat"
          color="purple"
        />
      </div>

      {/* Filters */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Pose Alerts</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="label">Filter by Employee</label>
            <select 
              className="input" 
              value={employeeFilter} 
              onChange={(e) => setEmployeeFilter(e.target.value)}
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
              value={cameraFilter} 
              onChange={(e) => setCameraFilter(e.target.value)}
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
              value={dateFilter} 
              onChange={(e) => setDateFilter(e.target.value)} 
            />
          </div>
          <div>
            <label className="label">Filter by Risk Type</label>
            <select 
              className="input" 
              value={riskFilter} 
              onChange={(e) => setRiskFilter(e.target.value)}
            >
              <option value="">All Risk Types</option>
              {uniqueRisks.map(risk => (
                <option key={risk} value={risk}>{risk}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <button 
            className="btn btn-secondary" 
            onClick={clearFilters}
          >
            Clear All Filters
          </button>
          {(employeeFilter || cameraFilter || dateFilter || riskFilter) && (
            <div className="text-sm text-gray-600">
              Showing {filteredData.length} of {totalAlerts} alerts
            </div>
          )}
        </div>
      </div>

      {/* Ergonomic Risk Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card p-4 border-l-4 border-red-500">
          <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
            <span>🦴</span>
            Back & Spine Risks
          </h3>
          <div className="text-2xl font-bold text-red-600 mb-1">{backInjuryRisks}</div>
          <p className="text-sm text-gray-600">Improper lifting, bending postures</p>
        </div>
        <div className="card p-4 border-l-4 border-orange-500">
          <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
            <span>💪</span>
            Upper Body Strain
          </h3>
          <div className="text-2xl font-bold text-orange-600 mb-1">
            {rows.filter(r => r.risk.toLowerCase().includes('shoulder') || r.risk.toLowerCase().includes('neck')).length}
          </div>
          <p className="text-sm text-gray-600">Shoulder, neck, and arm stress</p>
        </div>
        <div className="card p-4 border-l-4 border-purple-500">
          <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
            <span>🔄</span>
            Repetitive Motion
          </h3>
          <div className="text-2xl font-bold text-purple-600 mb-1">{repetitiveStrainRisks}</div>
          <p className="text-sm text-gray-600">Repetitive strain injuries</p>
        </div>
      </div>

      {/* Pose Alerts Table */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Alert Records</h2>
        {loading ? (
          <div className="card p-6 text-center">
            <div className="animate-pulse">Loading pose alerts...</div>
          </div>
        ) : (
          <Table
            columns={[
              { 
                header: 'Employee', 
                accessor: 'employee',
                cell: (row) => (
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-medium">
                      {row.employee.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="font-medium text-gray-900">{row.employee}</div>
                  </div>
                )
              },
              { 
                header: 'Alert Type', 
                accessor: 'alert',
                cell: (row) => (
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getAlertIcon(row.alert)}</span>
                    <div>
                      <div className="text-sm font-medium">{row.alert}</div>
                    </div>
                  </div>
                )
              },
              { 
                header: 'Risk Assessment', 
                accessor: 'risk',
                cell: (row) => (
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getRiskIcon(row.risk)}</span>
                    <span className={`badge ${getRiskColor(row.risk)}`}>
                      {row.risk}
                    </span>
                  </div>
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
                header: 'Actions',
                accessor: 'actions',
                cell: (row) => (
                  <div className="flex items-center gap-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">Review</button>
                    <button className="text-purple-600 hover:text-purple-800 text-sm">Assess</button>
                  </div>
                )
              }
            ]}
            data={filteredData}
            empty="No pose alerts found. Try adjusting your filters."
          />
        )}
      </div>
    </div>
  )
}
