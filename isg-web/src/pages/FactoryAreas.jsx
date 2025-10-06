import React, { useState, useEffect } from 'react'
import { FactoryAreasAPI, CamerasAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import Icon from '../components/Icon'
import Button from '../components/Button'
import Table from '../components/Table'
import Loading from '../components/Loading'

export default function FactoryAreas() {
  // Bring in hasRole to centralize permission checks
  const { user, hasRole } = useAuth()
  const [areas, setAreas] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingArea, setEditingArea] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    camera_ids: [],
    safety_rules: [],
    is_active: true
  })
  const [cameras, setCameras] = useState([])
  const [safetyRules, setSafetyRules] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [error, setError] = useState(null)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [debounceTimer, setDebounceTimer] = useState(null)

  // Permissions using centralized role helper (handles aliases internally)
  const canManageAreas = hasRole(['ADMIN', 'ADMIN (IT)', 'MANAGER'])
  const canDeleteAreas = hasRole(['ADMIN', 'ADMIN (IT)'])

  useEffect(() => {
    loadAreas()
    loadCameras()
    loadSafetyRules()
  }, [])

  // Debounce search input reload
  useEffect(() => {
    if (!showForm) {
      if (debounceTimer) clearTimeout(debounceTimer)
      const t = setTimeout(() => {
        loadAreas()
      }, 500)
      setDebounceTimer(t)
      return () => clearTimeout(t)
    }
  }, [searchTerm])

  const loadAreas = async () => {
    try {
      setLoading(true)
      // When includeInactive is false, request only active areas
  // Always fetch all areas (active + inactive)
  const response = await FactoryAreasAPI.list(0, 100, null, searchTerm)
      // Support both wrapped object {areas: [...]} and plain list responses
      const listCandidate = Array.isArray(response) ? response : response?.areas
      if (!Array.isArray(listCandidate)) {
        console.warn('Unexpected factory areas response shape', response)
        setAreas([])
      } else {
        setAreas(listCandidate)
      }
      setError(null)
    } catch (err) {
      console.error('Error loading factory areas:', err)
      setError('Failed to load factory areas')
    } finally {
      setLoading(false)
    }
  }

  const loadCameras = async () => {
    try {
      const response = await CamerasAPI.list(0, 100)
      setCameras(response.cameras || [])
    } catch (err) {
      console.error('Error loading cameras:', err)
    }
  }

  const loadSafetyRules = async () => {
    try {
      const rules = await FactoryAreasAPI.getSafetyRules()
      setSafetyRules(rules || [])
    } catch (err) {
      console.error('Error loading safety rules:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    
    try {
      if (editingArea) {
        await FactoryAreasAPI.update(editingArea.id, formData)
      } else {
        await FactoryAreasAPI.create(formData)
      }
      
      setShowForm(false)
      setEditingArea(null)
      resetForm()
      loadAreas()
    } catch (err) {
      console.error('Error saving factory area:', err)
      setError(err.response?.data?.detail || 'Failed to save factory area')
    }
  }

  const handleEdit = (area) => {
    setEditingArea(area)
    setFormData({
      name: area.name,
      description: area.description || '',
      camera_ids: area.cameras?.map(c => c.id) || [],
      safety_rules: area.safety_rules || [],
      is_active: area.is_active
    })
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this factory area?')) {
      return
    }

    try {
      await FactoryAreasAPI.delete(id)
      // Optimistic removal then fetch to ensure consistency
      setAreas(prev => prev.filter(a => a.id !== id))
      // Full refresh (handles pagination / server-side filters)
      loadAreas()
    } catch (err) {
      console.error('Error deleting factory area:', err)
      setError(err.response?.data?.detail || 'Failed to delete factory area')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      camera_ids: [],
      safety_rules: [],
      is_active: true
    })
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingArea(null)
    resetForm()
  }

  const toggleCameraSelection = (cameraId) => {
    setFormData(prev => ({
      ...prev,
      camera_ids: prev.camera_ids.includes(cameraId)
        ? prev.camera_ids.filter(id => id !== cameraId)
        : [...prev.camera_ids, cameraId]
    }))
  }

  const toggleSafetyRule = (rule) => {
    setFormData(prev => ({
      ...prev,
      safety_rules: prev.safety_rules.includes(rule)
        ? prev.safety_rules.filter(r => r !== rule)
        : [...prev.safety_rules, rule]
    }))
  }

  // Adapted to Table component API (header, accessor, cell)
  const columns = [
    {
      key: 'name',
      header: 'Area Name',
      accessor: 'name',
      cell: (row) => <span className="font-medium text-neutral-900">{row.name}</span>
    },
    {
      key: 'cameras',
      header: 'Cameras',
      accessor: 'cameras',
      cell: (row) => (
        <span className="text-sm">{row.cameras?.length || 0} camera(s)</span>
      )
    },
    {
      key: 'safety_rules',
      header: 'Safety Rules',
      accessor: 'safety_rules',
      cell: (row) => (
        <div className="flex flex-wrap gap-1">
          {(row.safety_rules || []).slice(0, 3).map(rule => (
            <span key={rule} className="badge badge-primary text-xs">{rule}</span>
          ))}
          {(row.safety_rules?.length || 0) > 3 && (
            <span className="text-xs text-neutral-500">+{row.safety_rules.length - 3} more</span>
          )}
        </div>
      )
    },
    {
      key: 'is_active',
      header: 'Status',
      accessor: 'is_active',
      cell: (row) => (
        <span className={`badge ${row.is_active ? 'badge-success' : 'badge-secondary'}`}>
          {row.is_active ? 'Active' : 'Inactive'}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      accessor: 'id',
      cell: (row) => (
        <div className="flex gap-2">
          {canManageAreas && (
            <button
              onClick={() => handleEdit(row)}
              className="text-primary-600 hover:text-primary-700"
              title="Edit"
            >
              <Icon name="edit" className="w-4 h-4" />
            </button>
          )}
          {canDeleteAreas && (
            <button
              onClick={() => handleDelete(row.id)}
              className="text-danger-600 hover:text-danger-700"
              title="Delete"
            >
              <Icon name="trash" className="w-4 h-4" />
            </button>
          )}
        </div>
      )
    }
  ]

  if (loading && !showForm) {
    return <Loading />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900">Factory Areas</h1>
          <p className="text-neutral-600 mt-1">Manage factory areas with cameras and safety rules</p>
        </div>
        {canManageAreas && !showForm && (
          <Button onClick={() => setShowForm(true)} variant="primary">
            <Icon name="plus" className="w-4 h-4 mr-2" />
            Add Factory Area
          </Button>
        )}
      </div>

      {error && (
        <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-soft p-6">
          <h2 className="text-xl font-semibold mb-4">
            {editingArea ? 'Edit Factory Area' : 'Add New Factory Area'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="area-name" className="block text-sm font-medium text-neutral-700 mb-2">
                  Area Name *
                </label>
                <input
                  id="area-name"
                  name="name"
                  type="text"
                  required
                  autoComplete="off"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input w-full"
                  placeholder="e.g., Factory Area-1, Main Gate"
                />
              </div>

              <div>
                <label htmlFor="area-status" className="block text-sm font-medium text-neutral-700 mb-2">
                  Status
                </label>
                <select
                  id="area-status"
                  name="is_active"
                  value={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.value === 'true' })}
                  className="input w-full"
                >
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="area-description" className="block text-sm font-medium text-neutral-700 mb-2">
                Description
              </label>
              <textarea
                id="area-description"
                name="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input w-full"
                rows="3"
                placeholder="Optional description of the area"
              />
            </div>

            {/* Safety Rules Selection */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Safety Rules
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {safetyRules.map(rule => {
                  const id = `sr-${rule}`
                  return (
                    <label key={rule} htmlFor={id} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        id={id}
                        name="safety_rules"
                        type="checkbox"
                        value={rule}
                        checked={formData.safety_rules.includes(rule)}
                        onChange={() => toggleSafetyRule(rule)}
                        className="form-checkbox h-4 w-4 text-primary-600 rounded"
                      />
                      <span className="text-sm text-neutral-700">{rule}</span>
                    </label>
                  )
                })}
              </div>
            </div>

            {/* Cameras Selection */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Cameras
              </label>
              <div className="border border-neutral-200 rounded-lg max-h-60 overflow-y-auto">
                {cameras.length === 0 ? (
                  <p className="text-neutral-500 p-4 text-sm">No cameras available</p>
                ) : (
                  <div className="divide-y divide-neutral-200">
                    {cameras.map(camera => {
                      const id = `cam-${camera.id}`
                      return (
                        <label key={camera.id} htmlFor={id} className="flex items-center p-3 hover:bg-neutral-50 cursor-pointer">
                          <input
                            id={id}
                            name="camera_ids"
                            type="checkbox"
                            value={camera.id}
                            checked={formData.camera_ids.includes(camera.id)}
                            onChange={() => toggleCameraSelection(camera.id)}
                            className="form-checkbox h-4 w-4 text-primary-600 rounded mr-3"
                          />
                          <div className="flex-1">
                            <div className="font-medium text-neutral-900">{camera.name}</div>
                            <div className="text-sm text-neutral-600">{camera.location}</div>
                          </div>
                          <span className={`badge ${camera.is_active ? 'badge-success' : 'badge-secondary'} text-xs`}>
                            {camera.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </label>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-neutral-200">
              <Button type="button" onClick={handleCancel} variant="secondary">
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                {editingArea ? 'Update Area' : 'Create Area'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Areas List */}
      {!showForm && (
        <div className="bg-white rounded-lg shadow-soft">
          <div className="p-4 border-b border-neutral-200 flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
            <div className="flex items-center gap-3 w-full md:w-auto">
              <input
                id="factory-areas-search"
                name="factoryAreasSearch"
                type="text"
                placeholder="Search areas..."
                aria-label="Search factory areas"
                autoComplete="off"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input w-full md:w-96"
              />
              <Button type="button" variant="secondary" onClick={loadAreas}>
                <Icon name="refresh" className="w-4 h-4 mr-1" />
                Refresh
              </Button>
            </div>
            <div className="text-xs text-neutral-500 w-full md:w-auto">Showing {areas.length} area{areas.length !== 1 && 's'}</div>
          </div>
          
          {areas.length === 0 ? (
            <div className="p-8 text-center">
              <Icon name="info" className="w-12 h-12 text-neutral-400 mx-auto mb-3" />
              <p className="text-neutral-600">No factory areas found</p>
              {canManageAreas && (
                <Button onClick={() => setShowForm(true)} variant="primary" className="mt-4">
                  Create First Area
                </Button>
              )}
            </div>
          ) : (
            <Table columns={columns} data={areas} />
          )}
        </div>
      )}
    </div>
  )
}
