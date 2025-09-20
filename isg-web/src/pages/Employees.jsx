import React, { useEffect, useMemo, useState } from 'react'
import { EmployeesAPI } from '../services/api'
import Table from '../components/Table'

export default function Employees() {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    (async () => {
      try {
        setError(null)
        setLoading(true)
        const resp = await EmployeesAPI.list()
        // Backend returns { employees, total, page, per_page }
        const employees = Array.isArray(resp?.employees) ? resp.employees : Array.isArray(resp) ? resp : []
        setList(employees)
      } catch (e) {
        console.error('Failed to load employees', e)
        setError('Failed to load employees')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const filtered = useMemo(() => list.filter((e) => {
    const fullName = `${e.first_name ?? ''} ${e.last_name ?? ''}`.trim()
    const email = e.email ?? ''
    return fullName.toLowerCase().includes(q.toLowerCase()) || email.toLowerCase().includes(q.toLowerCase())
  }), [list, q])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Employees</h1>
        <button className="btn">Add Employee</button>
      </div>
      <div className="card p-4">
        <input className="input" placeholder="Search by name or email" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {error && <div className="card p-6 text-red-600">{error}</div>}
      {loading ? (
        <div className="card p-6">Loading...</div>
      ) : (
        <Table
          columns={[
            { header: 'Name', accessor: 'full_name', key: 'name', cell: (r) => `${r.first_name ?? ''} ${r.last_name ?? ''}`.trim() || '-' },
            { header: 'Email', accessor: 'email' },
            { header: 'Department', accessor: 'department' },
            { header: 'Position', accessor: 'position' },
          ]}
          data={filtered}
        />
      )}
    </div>
  )
}
