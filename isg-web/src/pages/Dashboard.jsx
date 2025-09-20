import React, { useEffect, useState } from 'react'
import { EventsAPI } from '../services/api'
import Table from '../components/Table'

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

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h2 className="text-lg font-medium">Latest PPE Violations</h2>
          {loading ? <div className="card p-6">Loading...</div> : (
            <Table
              columns={[
                { header: 'Employee', accessor: 'employee' },
                { header: 'Camera', accessor: 'camera' },
                { header: 'Date', accessor: 'date' },
                { header: 'Description', accessor: 'desc' },
              ]}
              data={violations}
            />
          )}
        </div>
        <div className="space-y-3">
          <h2 className="text-lg font-medium">Latest Pose Alerts</h2>
          {loading ? <div className="card p-6">Loading...</div> : (
            <Table
              columns={[
                { header: 'Employee', accessor: 'employee' },
                { header: 'Camera', accessor: 'camera' },
                { header: 'Date', accessor: 'date' },
                { header: 'Alert', accessor: 'alert' },
              ]}
              data={poseAlerts}
            />
          )}
        </div>
      </div>
    </div>
  )
}
