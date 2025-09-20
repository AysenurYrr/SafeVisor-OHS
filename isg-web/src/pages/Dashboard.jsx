import React, { useEffect, useState } from 'react'
import { EventsAPI, EmployeesAPI, CamerasAPI } from '../services/api'
import Table from '../components/Table'
import StatsCard from '../components/StatsCard'

export default function Dashboard() {
  const [violations, setViolations] = useState([])
  const [poseAlerts, setPoseAlerts] = useState([])
  const [employees, setEmployees] = useState([])
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const [v, p, emp, cam] = await Promise.all([
        EventsAPI.violations(),
        EventsAPI.pose(),
        EmployeesAPI.list(),
        CamerasAPI.list(),
      ])
      setViolations(v)
      setPoseAlerts(p)
      setEmployees(emp)
      setCameras(cam)
      setLoading(false)
    })()
  }, [])

  // Calculate statistics
  const todayViolations = violations.filter(v => v.date === '2025-01-09').length
  const todayPoseAlerts = poseAlerts.filter(p => p.date === '2025-01-09').length
  const criticalViolations = violations.filter(v => v.severity === 'Critical').length
  const onlineCameras = cameras.filter(c => c.status === 'Online').length
  const offlineCameras = cameras.filter(c => c.status === 'Offline' || c.status === 'Maintenance').length

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Safety Dashboard</h1>
        <div className="mt-2 sm:mt-0 text-sm text-gray-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Today's Violations"
          value={todayViolations}
          subtitle="PPE violations today"
          icon="⚠️"
          trend="2 less than yesterday"
          trendDirection="down"
          color="red"
        />
        <StatsCard
          title="Pose Alerts"
          value={todayPoseAlerts}
          subtitle="Ergonomic alerts today"
          icon="🏃"
          trend="1 more than yesterday"
          trendDirection="up"
          color="yellow"
        />
        <StatsCard
          title="Critical Issues"
          value={criticalViolations}
          subtitle="Require immediate attention"
          icon="🚨"
          trend="Same as yesterday"
          trendDirection="flat"
          color="red"
        />
        <StatsCard
          title="Active Employees"
          value={employees.length}
          subtitle={`${onlineCameras} cameras online`}
          icon="👥"
          trend={`${offlineCameras} cameras offline`}
          trendDirection="down"
          color="green"
        />
      </div>

      {/* Recent Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Latest PPE Violations</h2>
            <a href="/events/violations" className="text-sm text-blue-600 hover:text-blue-800">View all →</a>
          </div>
          {loading ? <div className="card p-6">Loading...</div> : (
            <Table
              columns={[
                { header: 'Employee', accessor: 'employee' },
                { 
                  header: 'Severity', 
                  accessor: 'severity',
                  cell: (row) => (
                    <span className={`badge ${
                      row.severity === 'Critical' ? 'bg-red-100 text-red-800' :
                      row.severity === 'High' ? 'bg-orange-100 text-orange-800' :
                      row.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {row.severity}
                    </span>
                  )
                },
                { header: 'Date', accessor: 'date' },
                { header: 'Type', accessor: 'type' },
              ]}
              data={violations.slice(0, 5)}
            />
          )}
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Latest Pose Alerts</h2>
            <a href="/events/pose" className="text-sm text-blue-600 hover:text-blue-800">View all →</a>
          </div>
          {loading ? <div className="card p-6">Loading...</div> : (
            <Table
              columns={[
                { header: 'Employee', accessor: 'employee' },
                { header: 'Camera', accessor: 'camera' },
                { header: 'Date', accessor: 'date' },
                { header: 'Risk', accessor: 'risk' },
              ]}
              data={poseAlerts.slice(0, 5)}
            />
          )}
        </div>
      </div>
    </div>
  )
}
