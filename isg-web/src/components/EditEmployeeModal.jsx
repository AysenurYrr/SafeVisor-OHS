import React, { useState, useEffect } from 'react'
import Button from './Button'
import Icon from './Icon'
import { EmployeesAPI } from '../services/api'

export default function EditEmployeeModal({ employee, onClose, onUpdate }) {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    hire_date: '',
    emergency_contact: '',
    emergency_phone: '',
    notes: '',
    is_active: true
  })
  const [files, setFiles] = useState([null, null, null])
  const [filePreviews, setFilePreviews] = useState([null, null, null])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  useEffect(() => {
    if (employee) {
      setForm({
        first_name: employee.first_name || '',
        last_name: employee.last_name || '',
        email: employee.email || '',
        phone: employee.phone || '',
        department: employee.department || '',
        position: employee.position || '',
        hire_date: employee.hire_date || '',
        emergency_contact: employee.emergency_contact || '',
        emergency_phone: employee.emergency_phone || '',
        notes: employee.notes || '',
        is_active: employee.is_active ?? true
      })
      
      // Set existing photo previews
      const previews = [
        employee.photo_front_path ? `${API_BASE_URL}${employee.photo_front_path}` : null,
        employee.photo_left_path ? `${API_BASE_URL}${employee.photo_left_path}` : null,
        employee.photo_right_path ? `${API_BASE_URL}${employee.photo_right_path}` : null
      ]
      setFilePreviews(previews)
    }
  }, [employee, API_BASE_URL])

  const handleFileChange = (index, file) => {
    const newFiles = [...files]
    newFiles[index] = file
    setFiles(newFiles)

    // Create preview
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        const newPreviews = [...filePreviews]
        newPreviews[index] = reader.result
        setFilePreviews(newPreviews)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleRemovePreview = (index) => {
    const newFiles = [...files]
    const newPreviews = [...filePreviews]
    newFiles[index] = null
    
    // Keep existing photo URL if no new file uploaded
    if (!files[index]) {
      // Restore original preview
      if (index === 0 && employee.photo_front_path) {
        newPreviews[index] = `${API_BASE_URL}${employee.photo_front_path}`
      } else if (index === 1 && employee.photo_left_path) {
        newPreviews[index] = `${API_BASE_URL}${employee.photo_left_path}`
      } else if (index === 2 && employee.photo_right_path) {
        newPreviews[index] = `${API_BASE_URL}${employee.photo_right_path}`
      } else {
        newPreviews[index] = null
      }
    } else {
      newPreviews[index] = null
    }
    
    setFiles(newFiles)
    setFilePreviews(newPreviews)
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      setError(null)

      // Validate required fields
      if (!form.first_name || !form.last_name || !form.email || !form.department || !form.position) {
        setError('Please fill in all required fields')
        return
      }

      const data = new FormData()
      
      // Add text fields
      Object.keys(form).forEach(key => {
        if (form[key] !== null && form[key] !== undefined && form[key] !== '') {
          data.append(key, form[key])
        }
      })

      // Add photos if they were changed
      if (files[0]) data.append('photo_front', files[0])
      if (files[1]) data.append('photo_left', files[1])
      if (files[2]) data.append('photo_right', files[2])

      const updated = await EmployeesAPI.updateMultipart(employee.uuid, data)
      onUpdate(updated)
      onClose()
    } catch (e) {
      console.error('Failed to update employee', e)
      setError(e.response?.data?.detail || e.message || 'Failed to update employee')
    } finally {
      setLoading(false)
    }
  }

  if (!employee) return null

  return (
    <div className="modal-overlay">
      <div className="modal max-w-4xl">
        <div className="modal-header">
          <h3 className="text-xl font-semibold">Edit Employee</h3>
          <button onClick={onClose} className="icon-button" disabled={loading}>
            <Icon name="close" />
          </button>
        </div>
        
        <div className="modal-body space-y-4">
          {error && (
            <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">First Name *</label>
              <input 
                className="input" 
                value={form.first_name} 
                onChange={e => setForm({ ...form, first_name: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Last Name *</label>
              <input 
                className="input" 
                value={form.last_name} 
                onChange={e => setForm({ ...form, last_name: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Email *</label>
              <input 
                className="input" 
                type="email" 
                value={form.email} 
                onChange={e => setForm({ ...form, email: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Phone</label>
              <input 
                className="input" 
                value={form.phone} 
                onChange={e => setForm({ ...form, phone: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Department *</label>
              <input 
                className="input" 
                value={form.department} 
                onChange={e => setForm({ ...form, department: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Position *</label>
              <input 
                className="input" 
                value={form.position} 
                onChange={e => setForm({ ...form, position: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Hire Date</label>
              <input 
                className="input" 
                type="date" 
                value={form.hire_date} 
                onChange={e => setForm({ ...form, hire_date: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Emergency Contact</label>
              <input 
                className="input" 
                value={form.emergency_contact} 
                onChange={e => setForm({ ...form, emergency_contact: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Emergency Phone</label>
              <input 
                className="input" 
                value={form.emergency_phone} 
                onChange={e => setForm({ ...form, emergency_phone: e.target.value })} 
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Status</label>
              <select 
                className="input" 
                value={form.is_active ? 'active' : 'inactive'} 
                onChange={e => setForm({ ...form, is_active: e.target.value === 'active' })}
                disabled={loading}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Notes</label>
            <textarea 
              className="input" 
              rows="3" 
              value={form.notes} 
              onChange={e => setForm({ ...form, notes: e.target.value })} 
              disabled={loading}
            />
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-neutral-700">
              Profile Photos (Optional - update if needed)
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['Front Profile', 'Left Profile', 'Right Profile'].map((label, i) => (
                <div key={i} className="space-y-2">
                  <label className="text-xs text-neutral-600">{label}</label>
                  {filePreviews[i] && (
                    <div className="relative">
                      <img 
                        src={filePreviews[i]} 
                        alt={label}
                        className="w-full h-32 object-cover rounded border-2 border-primary-200"
                        onError={(e) => {
                          e.target.src = `https://ui-avatars.com/api/?name=${label}&background=random`
                        }}
                      />
                      <button
                        type="button"
                        onClick={() => handleRemovePreview(i)}
                        className="absolute top-1 right-1 bg-danger-600 text-white rounded-full p-1 hover:bg-danger-700"
                        disabled={loading}
                      >
                        <Icon name="close" className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                  <input 
                    type="file" 
                    accept="image/*" 
                    className="block w-full text-sm text-neutral-600
                      file:mr-4 file:py-2 file:px-4
                      file:rounded file:border-0
                      file:text-sm file:font-semibold
                      file:bg-primary-50 file:text-primary-700
                      hover:file:bg-primary-100"
                    onChange={(e) => handleFileChange(i, e.target.files?.[0] || null)}
                    disabled={loading}
                  />
                </div>
              ))}
            </div>
            <p className="text-xs text-neutral-500">
              Leave photo uploads empty to keep existing photos. Upload new photos to replace them.
            </p>
          </div>
        </div>

        <div className="modal-footer">
          <Button variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>
    </div>
  )
}
