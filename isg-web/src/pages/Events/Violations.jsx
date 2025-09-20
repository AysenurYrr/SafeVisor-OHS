import React, { useEffect, useMemo, useState } from 'react'
import { EventsAPI } from '../../services/api'
import Table from '../../components/Table'

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
          employee: v.employee_name || (v.employee_id != null ? `#${v.employee_id}` : '-'),
          camera: v.camera_name || (v.camera_id != null ? `#${v.camera_id}` : '-'),
          date: v.created_at ? new Date(v.created_at).toISOString().slice(0, 10) : '-',
          type: v.violation_type || '-',
          desc: v.description || '-',
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

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">PPE Violations</h1>
      <div className="card p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <input className="input" placeholder="Filter by employee" value={employee} onChange={(e) => setEmployee(e.target.value)} />
        <input className="input" placeholder="Filter by camera" value={camera} onChange={(e) => setCamera(e.target.value)} />
        <input className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <button className="btn btn-secondary" onClick={() => { setEmployee(''); setCamera(''); setDate('') }}>Clear</button>
      </div>
      {error && <div className="card p-6 text-red-600">{error}</div>}
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
