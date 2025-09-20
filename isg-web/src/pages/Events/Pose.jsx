import React, { useEffect, useState } from 'react'
import { EventsAPI } from '../../services/api'
import Table from '../../components/Table'

export default function Pose() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await EventsAPI.pose()
      setRows(data)
      setLoading(false)
    })()
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Pose Alerts</h1>
      {loading ? <div className="card p-6">Loading...</div> : (
        <Table
          columns={[
            { header: 'Employee', accessor: 'employee' },
            { header: 'Camera', accessor: 'camera' },
            { header: 'Date', accessor: 'date' },
            { header: 'Alert', accessor: 'alert' },
          ]}
          data={rows}
        />
      )}
    </div>
  )
}
