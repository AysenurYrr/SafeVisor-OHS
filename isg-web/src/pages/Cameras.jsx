import React, { useMemo, useState, useEffect, useRef, useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Cameras() {
  const { token, user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [selected, setSelected] = useState(1)
  const [isDetectionMode, setIsDetectionMode] = useState(false)
  const isDetectionModeRef = useRef(false)
  const [detectionStatus, setDetectionStatus] = useState({})
  const [violations, setViolations] = useState([])
  const [loading, setLoading] = useState(false)
  const intervalRef = useRef(null)
  const [nonce, setNonce] = useState(0)
  const videoRef = useRef(null)
  const overlayRef = useRef(null)
  const detectLoopRef = useRef(null)
  const processingRef = useRef(false)
  const latestDetectionsRef = useRef([])
  const latestFrameRef = useRef({ canvas: null, width: 0, height: 0, capturedAt: 0, annotated: false })
  const captureCanvasRef = useRef(null)
  const displayCanvasRef = useRef(null)
  const [detectionsTick, setDetectionsTick] = useState(0)
  const hasDetectionFrame = !!latestFrameRef.current?.canvas
  
  // Factory area information from navigation state
  const [factoryAreaInfo, setFactoryAreaInfo] = useState(null)
  const [autoStartDetection, setAutoStartDetection] = useState(false)
  
  const cameras = useMemo(() => ([
    { id: 1, name: 'Camera-1', desc: 'Demo stream 1 (demo.mp4)' },
    { id: 2, name: 'Camera-2', desc: 'Demo stream 2 (demo2.mp4)' },
    { id: 3, name: 'Camera-3', desc: 'Demo stream 3 (demo3.mp4)' },
  ]), [])

  const normalSrc = `${api.defaults.baseURL}/api/v1/cameras/${selected}/stream?token=${encodeURIComponent(token || '')}`
  // detectionSrc removed; detection handled client-side via frame capture

  // Handle navigation from Factory Areas
  useEffect(() => {
    if (location.state) {
      const { cameraId, factoryArea } = location.state
      if (cameraId && factoryArea) {
        setSelected(cameraId)
        setFactoryAreaInfo(factoryArea)
        setAutoStartDetection(true)
        // Clear the state to prevent re-triggering
        navigate(location.pathname, { replace: true, state: {} })
      }
    }
  }, [location.state, navigate])

  // Auto-start detection when coming from Factory Areas
  useEffect(() => {
    if (autoStartDetection && !isDetectionMode && videoRef.current) {
      // Wait for video to be ready
      const timer = setTimeout(() => {
        startDetection()
        setAutoStartDetection(false)
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [autoStartDetection, isDetectionMode])

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

  const paintDetections = useCallback((ctx, detections, baseWidth, baseHeight, scaleX, scaleY) => {
    if (!ctx || !detections?.length || !baseWidth || !baseHeight) {
      return
    }
    for (const det of detections) {
      const { box, class_name, confidence, recognized_name } = det || {}
      if (!box) continue
      let { x1, y1, x2, y2 } = box
      if ([x1, y1, x2, y2].some(v => typeof v !== 'number' || Number.isNaN(v))) continue
      x1 = Math.max(0, Math.min(baseWidth, x1))
      x2 = Math.max(0, Math.min(baseWidth, x2))
      y1 = Math.max(0, Math.min(baseHeight, y1))
      y2 = Math.max(0, Math.min(baseHeight, y2))
      const cx1 = x1 * scaleX
      const cy1 = y1 * scaleY
      const w = (x2 - x1) * scaleX
      const h = (y2 - y1) * scaleY
      if (w <= 2 || h <= 2) continue
      let color = '#ffffff'
      const cls = (class_name || '').toLowerCase()
      if (cls.includes('helmet')) color = '#16a34a'
      else if (cls.includes('vest')) color = '#eab308'
      else if (cls.includes('face')) color = '#3b82f6'
      else if (cls.includes('glove')) color = '#f97316'
      else if (cls.includes('mask')) color = '#9333ea'
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(cx1, cy1, w, h)
      const labelParts = [class_name]
      if (confidence !== undefined) labelParts.push(`${(confidence * 100).toFixed(1)}%`)
      if (recognized_name && recognized_name !== 'Unknown') labelParts.push(recognized_name)
      const label = labelParts.filter(Boolean).join(' ')
      if (!label) continue
      ctx.font = '12px sans-serif'
      const metrics = ctx.measureText(label)
      const textWidth = metrics.width + 8
      const textHeight = 16
      const labelY = cy1 - textHeight - 2 < 0 ? cy1 + textHeight : cy1 - 2
      ctx.fillStyle = color
      ctx.fillRect(cx1, labelY - textHeight, textWidth, textHeight)
      ctx.fillStyle = '#000'
      ctx.fillText(label, cx1 + 4, labelY - 4)
    }
  }, [])

  const drawDetections = useCallback(() => {
    const canvas = overlayRef.current
    const container = canvas?.parentElement
    const video = videoRef.current
    if (!canvas || !container || !video) return
    const rect = container.getBoundingClientRect()
    // Set canvas size to rendered size
    canvas.width = rect.width
    canvas.height = rect.height
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    const frameInfo = latestFrameRef.current
    const baseWidth = frameInfo?.width || video.videoWidth || 1
    const baseHeight = frameInfo?.height || video.videoHeight || 1
    if (isDetectionModeRef.current && frameInfo?.canvas) {
      ctx.drawImage(frameInfo.canvas, 0, 0, rect.width, rect.height)
    }
    const scaleX = rect.width / baseWidth
    const scaleY = rect.height / baseHeight
    if (!frameInfo?.annotated) {
      paintDetections(ctx, latestDetectionsRef.current || [], baseWidth, baseHeight, scaleX, scaleY)
    }
  }, [paintDetections])

  useEffect(() => { drawDetections() }, [detectionsTick, drawDetections])

  // Keep ref in sync to avoid stale closure in interval callbacks
  useEffect(() => { isDetectionModeRef.current = isDetectionMode }, [isDetectionMode])

  useEffect(() => {
    return () => {
      if (detectLoopRef.current) {
        cancelAnimationFrame(detectLoopRef.current)
        detectLoopRef.current = null
      }
    }
  }, [])

  const captureAndDetect = useCallback(async () => {
    const video = videoRef.current
    if (!isDetectionModeRef.current || !video) return
    if (processingRef.current) return
    if (video.readyState < 2 || !video.videoWidth || !video.videoHeight) return
    processingRef.current = true
    const startedAt = performance.now()
    try {
      let captureCanvas = captureCanvasRef.current
      if (!captureCanvas) {
        captureCanvas = document.createElement('canvas')
        captureCanvasRef.current = captureCanvas
      }
      const vw = video.videoWidth
      const vh = video.videoHeight
      captureCanvas.width = vw
      captureCanvas.height = vh
      const cctx = captureCanvas.getContext('2d')
      cctx.drawImage(video, 0, 0, vw, vh)
      const dataUrl = captureCanvas.toDataURL('image/jpeg', 0.6)
      const payload = { frame: dataUrl, selected_rules: ['helmet', 'safety-vest', 'face'] }
      const resp = await api.post('/api/v1/live-camera/detect', payload)
      if (resp?.data?.detections) {
        latestDetectionsRef.current = resp.data.detections
      } else {
        latestDetectionsRef.current = []
      }
      let displayCanvas = displayCanvasRef.current
      if (!displayCanvas) {
        displayCanvas = document.createElement('canvas')
        displayCanvasRef.current = displayCanvas
      }
      displayCanvas.width = vw
      displayCanvas.height = vh
      const dctx = displayCanvas.getContext('2d')
      dctx.drawImage(captureCanvas, 0, 0, vw, vh)
      paintDetections(dctx, latestDetectionsRef.current, vw, vh, 1, 1)
      latestFrameRef.current = {
        canvas: displayCanvas,
        width: vw,
        height: vh,
        capturedAt: performance.now(),
        latency: performance.now() - startedAt,
        annotated: true,
      }
      drawDetections()
      setDetectionsTick(t => t + 1)
      console.log(`[PPE] Detection result (n=${latestDetectionsRef.current.length}) in ${(performance.now() - startedAt).toFixed(0)}ms`)
    } catch (error) {
      console.log('[PPE] Detection error')
    } finally {
      processingRef.current = false
    }
  }, [drawDetections, paintDetections])

  // Ensure the video element has enough data to extract frames
  const ensureVideoReady = useCallback(() => {
    return new Promise((resolve) => {
      const video = videoRef.current
      if (!video) {
        return resolve(false)
      }
      // HAVE_CURRENT_DATA = 2, HAVE_ENOUGH_DATA = 4
      if (video.readyState >= 2 && video.videoWidth && video.videoHeight) {
        return resolve(true)
      }
      let attempts = 0
      const maxAttempts = 25 // ~2.5s at 100ms
      const interval = setInterval(() => {
        attempts++
        const vs = video.readyState
        if (vs >= 2 && video.videoWidth && video.videoHeight) {
          clearInterval(interval)
          resolve(true)
        } else if (attempts >= maxAttempts) {
          clearInterval(interval)
          resolve(false)
        }
      }, 100)
    })
  }, [])

  const startDetection = async () => {
    setLoading(true)
    try {
  try { const response = await api.post(`/api/v1/detections/run/${selected}`, {}); setDetectionStatus(response.data || {}) } catch (_) {}
  if (detectLoopRef.current) { cancelAnimationFrame(detectLoopRef.current); detectLoopRef.current = null }
  setIsDetectionMode(true)
  isDetectionModeRef.current = true
      setNonce(Date.now())
      console.log(`[PPE] Detection started (camera=${selected})`)
      // Wait until video metadata & data are ready before starting loop
      await ensureVideoReady()
      const loop = () => {
        if (!isDetectionModeRef.current) return
        captureAndDetect().finally(() => {
          if (!isDetectionModeRef.current) return
          detectLoopRef.current = requestAnimationFrame(loop)
        })
      }
      // Kick off loop immediately
      loop()
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
    isDetectionModeRef.current = false
    setDetectionStatus({})
    setNonce(Date.now())
    if (detectLoopRef.current) { cancelAnimationFrame(detectLoopRef.current); detectLoopRef.current = null }
    latestDetectionsRef.current = []
  latestFrameRef.current = { canvas: null, width: 0, height: 0, capturedAt: 0, annotated: false }
    // Clear overlay
    const canvas = overlayRef.current
    if (canvas) {
      const ctx = canvas.getContext('2d')
      ctx && ctx.clearRect(0,0,canvas.width,canvas.height)
    }
    setDetectionsTick(t => t + 1)
  }

  const fetchViolations = async () => {
    try {
      const response = await api.get(`/api/v1/detections/reports?limit=10&camera_id=${selected}`)
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
      {/* Factory Area Information Banner */}
      {factoryAreaInfo && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                Factory Area: {factoryAreaInfo.name}
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                Active Safety Rules: {factoryAreaInfo.safetyRules.length > 0 ? (
                  <span className="font-medium">{factoryAreaInfo.safetyRules.join(', ')}</span>
                ) : (
                  <span>No rules defined</span>
                )}
              </p>
              <p className="text-xs text-blue-600 mt-2">
                🔴 PPE Detection is running automatically with the factory area's safety rules
              </p>
            </div>
            <button
              onClick={() => setFactoryAreaInfo(null)}
              className="text-blue-600 hover:text-blue-800"
              title="Clear factory area context"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Cameras</h1>
        <div className="space-x-2">
          {!factoryAreaInfo && !isDetectionMode ? (
            <button
              onClick={startDetection}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Starting...' : 'Run PPE Detection'}
            </button>
          ) : factoryAreaInfo && isDetectionMode ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-green-600 font-medium">
                ✓ Detection Active
              </span>
              <button
                onClick={stopDetection}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Stop Detection
              </button>
            </div>
          ) : isDetectionMode ? (
            <button
              onClick={stopDetection}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Stop Detection
            </button>
          ) : null}
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
                onClick={() => { setSelected(cam.id); setNonce(Date.now()); if (isDetectionMode) { stopDetection(); setTimeout(startDetection, 50) } }}
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
              {isDetectionMode && (
                <></>
              )}
              <span className={`px-2 py-1 rounded text-xs ${isDetectionMode ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                {isDetectionMode ? 'Detection ON' : 'Normal Video'}
              </span>
            </div>
          </div>
          
          <div className="relative" style={{ width: '100%', maxHeight: 540 }}>
            <video
              key={`video-${selected}`}
              ref={videoRef}
              src={normalSrc + '&v=' + nonce}
              loop
              autoPlay
              muted
              playsInline
              controls={false}
              crossOrigin="anonymous"
              onLoadedMetadata={() => { try { videoRef.current?.play() } catch (_) {} }}
              onLoadedData={() => { /* video data loaded */ }}
              onPlay={() => { /* video playing */ }}
              onEnded={(e) => { try { e.currentTarget.currentTime = 0; e.currentTarget.play() } catch (_) {} }}
              style={{ width: '100%', maxHeight: 540, background: '#000', display: 'block', opacity: isDetectionMode && hasDetectionFrame ? 0 : 1, transition: 'opacity 120ms ease' }}
              className="rounded"
            />
            <canvas
              ref={overlayRef}
              className="absolute inset-0 pointer-events-none"
              style={{ width: '100%', height: '100%', zIndex: 5, opacity: isDetectionMode && hasDetectionFrame ? 1 : 0, transition: 'opacity 120ms ease' }}
            />
          </div>
          
          <p className="mt-2 text-xs text-gray-500">
            {isDetectionMode
              ? 'PPE Detection active. Showing most recent AI-annotated frame (Green=helmet, Yellow=vest, Blue=face).'
              : "Looping demo video. Ensure demo files exist under /static/videos (demo.mp4, demo2.mp4, demo3.mp4)."}
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
