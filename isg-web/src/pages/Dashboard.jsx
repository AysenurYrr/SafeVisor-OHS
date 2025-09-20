import React, { useEffect, useState } from 'react'
import { EventsAPI } from '../services/api'
import Table from '../components/Table'
import { StatsGrid } from '../components/StatsCard'
import { SkeletonStats, SkeletonTable } from '../components/Loading'
import Icon from '../components/Icon'
import Button from '../components/Button'

export default function Dashboard() {
  const [violations, setViolations] = useState([])
  const [poseAlerts, setPoseAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const [v, p] = await Promise.all([
        EventsAPI.violations(),
        EventsAPI.pose(),
      ])
      setViolations(v.slice(0, 5))
      setPoseAlerts(p.slice(0, 5))
      setLoading(false)
    })()
  }, [])

  // Mock statistics - in real app, this would come from API
  const stats = [
    {
      title: 'Total Employees',
      value: '247',
      change: '+12 this month',
      changeType: 'positive',
      icon: 'employees',
      iconColor: 'text-primary-600'
    },
    {
      title: 'Active Cameras',
      value: '18',
      change: '2 offline',
      changeType: 'negative',
      icon: 'cameras',
      iconColor: 'text-success-600'
    },
    {
      title: 'PPE Violations',
      value: '23',
      change: '-15% from last week',
      changeType: 'positive',
      icon: 'violations',
      iconColor: 'text-warning-600'
    },
    {
      title: 'Safety Score',
      value: '94%',
      change: '+2% improvement',
      changeType: 'positive',
      icon: 'safety',
      iconColor: 'text-success-600'
    }
  ]

  const recentViolationColumns = [
    { 
      header: 'Employee', 
      accessor: 'employee',
      icon: 'person',
      cell: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <Icon name="person" className="w-4 h-4 text-primary-600" />
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
      accessor: 'desc',
      cell: (row) => (
        <span className="badge-warning">{row.desc}</span>
      )
    },
  ]

  const recentPoseColumns = [
    { 
      header: 'Employee', 
      accessor: 'employee',
      icon: 'person',
      cell: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-warning-100 rounded-full flex items-center justify-center">
            <Icon name="person" className="w-4 h-4 text-warning-600" />
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
      header: 'Alert Type', 
      accessor: 'alert',
      cell: (row) => (
        <span className="badge-danger">{row.alert}</span>
      )
    },
  ]

  return (
    <div className="space-y-8 animate-fade-in-custom">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Safety Dashboard</h1>
          <p className="text-neutral-600 mt-1">Monitor your workplace safety in real-time</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" icon="document" size="sm">
            Export Report
          </Button>
          <Button variant="primary" icon="add">
            New Alert
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      {loading ? (
        <SkeletonStats count={4} />
      ) : (
        <StatsGrid stats={stats} />
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-interactive p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary-100 rounded-xl">
              <Icon name="employees" className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Manage Employees</h3>
              <p className="text-sm text-neutral-600">Add, edit, or review employee records</p>
            </div>
          </div>
        </div>
        
        <div className="card-interactive p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-success-100 rounded-xl">
              <Icon name="cameras" className="w-6 h-6 text-success-600" />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Camera Status</h3>
              <p className="text-sm text-neutral-600">Monitor camera health and coverage</p>
            </div>
          </div>
        </div>
        
        <div className="card-interactive p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-warning-100 rounded-xl">
              <Icon name="violations" className="w-6 h-6 text-warning-600" />
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">Safety Events</h3>
              <p className="text-sm text-neutral-600">Review recent violations and alerts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-neutral-900 flex items-center gap-2">
              <Icon name="violations" className="w-5 h-5 text-warning-600" />
              Recent PPE Violations
            </h2>
            <Button variant="ghost" size="sm" icon="view">
              View All
            </Button>
          </div>
          {loading ? (
            <SkeletonTable rows={5} cols={4} />
          ) : (
            <Table
              columns={recentViolationColumns}
              data={violations}
              className="card"
            />
          )}
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-neutral-900 flex items-center gap-2">
              <Icon name="clock" className="w-5 h-5 text-danger-600" />
              Recent Pose Alerts
            </h2>
            <Button variant="ghost" size="sm" icon="view">
              View All
            </Button>
          </div>
          {loading ? (
            <SkeletonTable rows={5} cols={4} />
          ) : (
            <Table
              columns={recentPoseColumns}
              data={poseAlerts}
              className="card"
            />
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Icon name="heart" className="w-5 h-5 text-success-600" />
          System Health
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center justify-between p-4 bg-success-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="status-online"></div>
              <span className="font-medium text-success-900">API Server</span>
            </div>
            <span className="text-sm text-success-700">Operational</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-success-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="status-online"></div>
              <span className="font-medium text-success-900">Database</span>
            </div>
            <span className="text-sm text-success-700">Operational</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-warning-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="status-warning"></div>
              <span className="font-medium text-warning-900">Camera Network</span>
            </div>
            <span className="text-sm text-warning-700">2 offline</span>
          </div>
        </div>
      </div>
    </div>
  )
}
