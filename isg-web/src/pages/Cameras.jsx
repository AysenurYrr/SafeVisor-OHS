import React, { useEffect, useState } from 'react'
import { CamerasAPI } from '../services/api'
import Table from '../components/Table'

export default function Cameras() {
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await CamerasAPI.list()
      setList(data)
      setLoading(false)
    })()
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Cameras</h1>
        <button className="btn">Add Camera</button>
      </div>
      {loading ? <div className="card p-6">Loading...</div> : (
        <Table
          columns={[
            { header: 'Name', accessor: 'name' },
            { header: 'Location', accessor: 'location' },
            { header: 'Status', accessor: 'status' },
            { header: 'Actions', key: 'actions', cell: (row) => (
              <div className="flex gap-2">
                <button className="btn btn-secondary">Edit</button>
                <button className="btn bg-red-600 hover:bg-red-700">Delete</button>
              </div>
            ) },
          ]}
          data={list}
        />
      )}
    </div>
  )
}
