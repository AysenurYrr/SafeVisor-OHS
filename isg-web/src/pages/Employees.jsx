import React, { useEffect, useMemo, useState } from 'react'
import { EmployeesAPI } from '../services/api'
import Table from '../components/Table'

export default function Employees() {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await EmployeesAPI.list()
      setList(data)
      setLoading(false)
    })()
  }, [])

  const filtered = useMemo(() => list.filter(e => (
    e.name.toLowerCase().includes(q.toLowerCase()) || e.email.toLowerCase().includes(q.toLowerCase())
  )), [list, q])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Employees</h1>
        <button className="btn">Add Employee</button>
      </div>
      <div className="card p-4">
        <input className="input" placeholder="Search by name or email" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {loading ? <div className="card p-6">Loading...</div> : (
        <Table
          columns={[
            { header: 'Name', accessor: 'name' },
            { header: 'Email', accessor: 'email' },
            { header: 'Company', accessor: 'company' },
          ]}
          data={filtered}
        />
      )}
    </div>
  )
}
