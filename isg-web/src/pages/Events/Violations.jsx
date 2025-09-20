import React, { useEffect, useMemo, useState } from 'react'
import { EventsAPI } from '../../services/api'
import Table from '../../components/Table'

export default function Violations() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [employee, setEmployee] = useState('')
  const [camera, setCamera] = useState('')
  const [date, setDate] = useState('')

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await EventsAPI.violations()
      setRows(data)
      setLoading(false)
    })()
  }, [])

  const filtered = useMemo(() => rows.filter(r => (
    (!employee || r.employee.toLowerCase().includes(employee.toLowerCase())) &&
    (!camera || r.camera.toLowerCase().includes(camera.toLowerCase())) &&
    (!date || r.date === date)
  )), [rows, employee, camera, date])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">PPE Violations</h1>
      <div className="card p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <input className="input" placeholder="Filter by employee" value={employee} onChange={(e) => setEmployee(e.target.value)} />
        <input className="input" placeholder="Filter by camera" value={camera} onChange={(e) => setCamera(e.target.value)} />
        <input className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <button className="btn btn-secondary" onClick={() => { setEmployee(''); setCamera(''); setDate('') }}>Clear</button>
      </div>
      {loading ? <div className="card p-6">Loading...</div> : (
        <Table
          columns={[
            { header: 'Employee', accessor: 'employee' },
            { header: 'Camera', accessor: 'camera' },
            { header: 'Date', accessor: 'date' },
            { header: 'Type', accessor: 'type' },
            { header: 'Description', accessor: 'desc' },
          ]}
          data={filtered}
        />
      )}
    </div>
  )
}
