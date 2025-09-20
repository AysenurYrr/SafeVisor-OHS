import React, { useEffect, useState } from 'react'
import { UsersAPI } from '../../services/api'
import Table from '../../components/Table'

const roles = ['Admin (IT)', 'Manager', 'AssistantManager', 'HSEExpert']

export default function Users() {
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await UsersAPI.list()
      setList(data)
      setLoading(false)
    })()
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">User Management</h1>
        <button className="btn">Add User</button>
      </div>
      {loading ? <div className="card p-6">Loading...</div> : (
        <Table
          columns={[
            { header: 'Name', accessor: 'name' },
            { header: 'Email', accessor: 'email' },
            { header: 'Role', key: 'role', cell: (row) => (
              <select className="input" value={row.role} onChange={(e) => setList(prev => prev.map(u => u.id === row.id ? { ...u, role: e.target.value } : u))}>
                {roles.map(r => <option value={r} key={r}>{r}</option>)}
              </select>
            ) },
          ]}
          data={list}
        />
      )}
    </div>
  )
}
