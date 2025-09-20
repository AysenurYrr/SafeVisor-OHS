import React, { useEffect, useMemo, useState } from 'react'
import { CamerasAPI } from '../services/api'
import Table from '../components/Table'
import StatsCard from '../components/StatsCard'

export default function Cameras() {
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    (async () => {
      setLoading(true)
      const data = await CamerasAPI.list()
      setList(data)
      setLoading(false)
    })()
  }, [])

  // Calculate statistics
  const onlineCameras = list.filter(c => c.status === 'Online').length
  const offlineCameras = list.filter(c => c.status === 'Offline').length
  const maintenanceCameras = list.filter(c => c.status === 'Maintenance').length
  const totalCameras = list.length

  // Get unique locations for filter
  const locations = useMemo(() => {
    const locs = [...new Set(list.map(c => c.location.split(' - ')[0] || c.location))].sort()
    return locs
  }, [list])

  // Filter cameras
  const filteredCameras = useMemo(() => {
    return list.filter(camera => {
      const matchesSearch = camera.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           camera.location.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = !statusFilter || camera.status === statusFilter
      const matchesLocation = !locationFilter || camera.location.includes(locationFilter)
      return matchesSearch && matchesStatus && matchesLocation
    })
  }, [list, searchQuery, statusFilter, locationFilter])

  const getStatusColor = (status) => {
    switch (status) {
      case 'Online': return 'bg-green-100 text-green-800'
      case 'Offline': return 'bg-red-100 text-red-800'
      case 'Maintenance': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Online': return '🟢'
      case 'Offline': return '🔴'
      case 'Maintenance': return '🟡'
      default: return '⚪'
    }
  }

  const getLastCheckTime = (camera) => {
    if (!camera.lastCheck) return 'Unknown'
    const time = new Date(camera.lastCheck)
    return time.toLocaleTimeString()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Camera Monitoring</h1>
          <p className="text-gray-600 mt-1">Monitor security cameras and surveillance systems</p>
        </div>
        <button className="btn bg-green-600 hover:bg-green-700">
          <span className="text-lg mr-2">+</span>
          Add Camera
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Cameras"
          value={totalCameras}
          subtitle="Monitoring systems"
          icon="📹"
          color="blue"
        />
        <StatsCard
          title="Online"
          value={onlineCameras}
          subtitle="Active monitoring"
          icon="🟢"
          trend={`${Math.round((onlineCameras/totalCameras)*100)}% uptime`}
          trendDirection="up"
          color="green"
        />
        <StatsCard
          title="Offline"
          value={offlineCameras}
          subtitle="Needs attention"
          icon="🔴"
          trend={offlineCameras > 0 ? "Requires immediate action" : "All systems operational"}
          trendDirection={offlineCameras > 0 ? "up" : "flat"}
          color="red"
        />
        <StatsCard
          title="Maintenance"
          value={maintenanceCameras}
          subtitle="Under service"
          icon="🔧"
          trend="Scheduled maintenance"
          trendDirection="flat"
          color="yellow"
        />
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Search Cameras</label>
            <input 
              className="input" 
              placeholder="Search by name or location..." 
              value={searchQuery} 
              onChange={(e) => setSearchQuery(e.target.value)} 
            />
          </div>
          <div>
            <label className="label">Filter by Status</label>
            <select 
              className="input" 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="Online">Online</option>
              <option value="Offline">Offline</option>
              <option value="Maintenance">Maintenance</option>
            </select>
          </div>
          <div>
            <label className="label">Filter by Area</label>
            <select 
              className="input" 
              value={locationFilter} 
              onChange={(e) => setLocationFilter(e.target.value)}
            >
              <option value="">All Areas</option>
              {locations.map(location => (
                <option key={location} value={location}>{location}</option>
              ))}
            </select>
          </div>
        </div>
        {(searchQuery || statusFilter || locationFilter) && (
          <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
            <span>Showing {filteredCameras.length} of {totalCameras} cameras</span>
            {(searchQuery || statusFilter || locationFilter) && (
              <button 
                onClick={() => { setSearchQuery(''); setStatusFilter(''); setLocationFilter('') }}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Clear filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* Camera Grid View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 mb-6">
        {filteredCameras.slice(0, 6).map(camera => (
          <div key={camera.id} className="card p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{getStatusIcon(camera.status)}</span>
                <div>
                  <h3 className="font-medium text-gray-900">{camera.name}</h3>
                  <p className="text-sm text-gray-500">{camera.location}</p>
                </div>
              </div>
              <span className={`badge ${getStatusColor(camera.status)}`}>
                {camera.status}
              </span>
            </div>
            <div className="text-xs text-gray-500 mb-3">
              Last check: {getLastCheckTime(camera)}
            </div>
            <div className="flex gap-2">
              <button className="btn btn-secondary text-xs px-2 py-1">View</button>
              <button className="btn btn-secondary text-xs px-2 py-1">Settings</button>
              {camera.status === 'Offline' && (
                <button className="bg-red-600 text-white text-xs px-2 py-1 rounded hover:bg-red-700">
                  Restart
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Table */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">All Cameras</h2>
        {loading ? (
          <div className="card p-6 text-center">
            <div className="animate-pulse">Loading cameras...</div>
          </div>
        ) : (
          <Table
            columns={[
              { 
                header: 'Camera', 
                accessor: 'name',
                cell: (row) => (
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{getStatusIcon(row.status)}</span>
                    <div>
                      <div className="font-medium text-gray-900">{row.name}</div>
                      <div className="text-sm text-gray-500">{row.location}</div>
                    </div>
                  </div>
                )
              },
              { 
                header: 'Status', 
                accessor: 'status',
                cell: (row) => (
                  <span className={`badge ${getStatusColor(row.status)}`}>
                    {row.status}
                  </span>
                )
              },
              { 
                header: 'Last Check', 
                accessor: 'lastCheck',
                cell: (row) => (
                  <div className="text-sm text-gray-700">
                    {getLastCheckTime(row)}
                  </div>
                )
              },
              {
                header: 'Actions',
                accessor: 'actions',
                cell: (row) => (
                  <div className="flex items-center gap-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">View</button>
                    <button className="text-gray-600 hover:text-gray-800 text-sm">Edit</button>
                    {row.status === 'Offline' && (
                      <button className="text-red-600 hover:text-red-800 text-sm">Restart</button>
                    )}
                  </div>
                )
              }
            ]}
            data={filteredCameras}
            empty="No cameras found. Try adjusting your search or filters."
          />
        )}
      </div>
    </div>
  )
}
