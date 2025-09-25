import React, { useMemo, useState, useEffect, useRef } from 'react'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Cameras() {
  const { token, user } = useAuth()
  const [selected, setSelected] = useState(1)
  const [isDetectionMode, setIsDetectionMode] = useState(false)
  const [detectionStatus, setDetectionStatus] = useState({})
  const [violations, setViolations] = useState([])
  const [loading, setLoading] = useState(false)
  const intervalRef = useRef(null)
  
  const cameras = useMemo(() => ([
    { id: 1, name: 'Camera-1', desc: 'Demo stream 1 (demo.mp4)' },
    { id: 2, name: 'Camera-2', desc: 'Demo stream 2 (demo2.mp4)' },
    { id: 3, name: 'Camera-3', desc: 'Demo stream 3 (demo3.mp4)' },
  ]), [])

  const normalSrc = `${api.defaults.baseURL}/api/v1/cameras/${selected}/stream?token=${encodeURIComponent(token || '')}`
  const detectionSrc = `${api.defaults.baseURL}/api/v1/detections/stream/${selected}?token=${encodeURIComponent(token || '')}`

  // Fetch violations periodically when detection is active
  useEffect(() => {
    if (isDetectionMode) {
      // Fetch immediately
      fetchViolations()
      
      // Set up periodic fetching every 5 seconds
      intervalRef.current = setInterval(() => {
        fetchViolations()
      }, 5000)
    } else {
      // Clear interval when detection is stopped
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isDetectionMode])

  const startDetection = async () => {
    setLoading(true)
    try {
      const response = await api.post(`/api/v1/detections/run/${selected}`, {})
      setDetectionStatus(response.data)
      setIsDetectionMode(true)
      
      // Fetch recent violations
      await fetchViolations()
    } catch (error) {
      console.error('Failed to start detection:', error)
      alert('Failed to start PPE detection. Please check if the AI model is loaded.')
    } finally {
      setLoading(false)
    }
  }

  const stopDetection = () => {
    setIsDetectionMode(false)
    setDetectionStatus({})
  }

  const fetchViolations = async () => {
    try {
      const response = await api.get('/api/v1/detections/reports?limit=10')
      setViolations(response.data)
    } catch (error) {
      console.error('Failed to fetch violations:', error)
    }
  }

  const getViolationBadgeColor = (type) => {
    switch (type) {
      case 'no_helmet':
        return 'bg-red-100 text-red-800'
      case 'no_vest':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Cameras</h1>
        <div className="space-x-2">
          {!isDetectionMode ? (
            <button
              onClick={startDetection}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Starting...' : 'Run PPE Detection'}
            </button>
          ) : (
            <button
              onClick={stopDetection}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Stop Detection
            </button>
          )}
        </div>
      </div>

      {detectionStatus.message && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3">
          <p className="text-blue-800">{detectionStatus.message}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-1 card p-4">
          <h2 className="font-semibold mb-3">Select Camera</h2>
          <div className="space-y-2">
            {cameras.map(cam => (
              <button
                key={cam.id}
                className={`w-full text-left px-3 py-2 rounded border ${selected === cam.id ? 'bg-primary-50 border-primary-400' : 'bg-white border-neutral-200 hover:bg-neutral-50'}`}
                onClick={() => setSelected(cam.id)}
              >
                <div className="font-medium">{cam.name}</div>
                <div className="text-xs text-neutral-600">{cam.desc}</div>
              </button>
            ))}
          </div>
        </div>
        
        <div className="md:col-span-3 card p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-gray-600">Logged in as: {user?.full_name || user?.email}</p>
            <div className="flex items-center space-x-2">
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  checked={isDetectionMode}
                  onChange={(e) => {
                    if (e.target.checked) {
                      startDetection()
                    } else {
                      stopDetection()
                    }
                  }}
                  disabled={loading}
                  className="form-checkbox h-4 w-4 text-primary-600"
                />
                <span className="ml-2 text-sm">PPE Detection</span>
              </label>
              <span className={`px-2 py-1 rounded text-xs ${isDetectionMode ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                {isDetectionMode ? 'Detection ON' : 'Normal Video'}
              </span>
            </div>
          </div>
          
          <div className="relative">
            {/* Always use video element, but switch sources */}
            <video
              key={`video-${selected}-${isDetectionMode ? 'detection' : 'normal'}`}
              controls={!isDetectionMode}
              autoPlay
              muted
              loop
              style={{ width: '100%', maxHeight: 540, background: '#000' }}
              className="rounded"
              preload="metadata"
            >
              <source src={isDetectionMode ? detectionSrc : normalSrc} type={isDetectionMode ? "video/mjpeg" : "video/mp4"} />
              Your browser does not support the video tag.
            </video>
            
            {/* Fallback for MJPEG stream - use img element only if video fails */}
            {isDetectionMode && (
              <img
                src={detectionSrc}
                alt="PPE Detection Stream"
                style={{ width: '100%', maxHeight: 540, background: '#000', display: 'none' }}
                className="rounded absolute top-0 left-0"
                onError={(e) => {
                  // Show img element if video fails to display MJPEG
                  e.target.style.display = 'block'
                  e.target.previousElementSibling.style.display = 'none'
                }}
              />
            )}
          </div>
          
          <p className="mt-2 text-xs text-gray-500">
            {isDetectionMode 
              ? "PPE Detection active. Green boxes show helmets, yellow show vests, blue show faces. Violations are automatically saved to database."
              : "If the video doesn't start, ensure: backend is running and videos demo.mp4, demo2.mp4, demo3.mp4 exist under app/static/videos/."
            }
          </p>
        </div>
      </div>

      {/* Violations Table */}
      {violations.length > 0 && (
        <div className="card p-4">
          <h2 className="text-lg font-semibold mb-3">Recent PPE Violations</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Camera
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Violation Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bounding Box
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {violations.map((violation) => (
                  <tr key={violation.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      Camera-{violation.camera_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getViolationBadgeColor(violation.violation_type)}`}>
                        {violation.violation_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {violation.description}
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-500">
                      {violation.bbox_coordinates ? (
                        <div>
                          <div>X: {violation.bbox_coordinates.x}</div>
                          <div>Y: {violation.bbox_coordinates.y}</div>
                          <div>W: {violation.bbox_coordinates.width}</div>
                          <div>H: {violation.bbox_coordinates.height}</div>
                        </div>
                      ) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(violation.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(violation.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${violation.resolved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {violation.resolved ? 'Resolved' : 'Open'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
