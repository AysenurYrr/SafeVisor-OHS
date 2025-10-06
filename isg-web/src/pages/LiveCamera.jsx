import React, { useState, useRef, useEffect } from 'react'
import api from '../services/api'
import Icon from '../components/Icon'
import Button from '../components/Button'

// Available PPE detection rules
const AVAILABLE_RULES = [
  { id: 'glasses', label: 'Glasses', icon: '👓' },
  { id: 'face-mask', label: 'Face Mask', icon: '😷' },
  { id: 'ear-muffs', label: 'Ear Muffs', icon: '🎧' },
  { id: 'hands', label: 'Hands', icon: '✋' },
  { id: 'gloves', label: 'Gloves', icon: '🧤' },
  { id: 'safety-vest', label: 'Safety Vest', icon: '🦺' },
  { id: 'tools', label: 'Tools', icon: '🔧' },
  { id: 'helmet', label: 'Helmet', icon: '⛑️' },
  { id: 'medical-suit', label: 'Medical Suit', icon: '🥼' },
  { id: 'safety-suit', label: 'Safety Suit', icon: '👔' },
]

export default function LiveCamera() {
  const [isDetecting, setIsDetecting] = useState(false)
  const [selectedRules, setSelectedRules] = useState([])
  const [cameraError, setCameraError] = useState(null)
  const [detections, setDetections] = useState([])
  const [stats, setStats] = useState({ total: 0, byType: {} })
  
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const detectionIntervalRef = useRef(null)

  // Initialize webcam
  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 }
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
      }
      
      setCameraError(null)
    } catch (error) {
      console.error('Error accessing camera:', error)
      setCameraError('Unable to access camera. Please ensure camera permissions are granted.')
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }

  const toggleRule = (ruleId) => {
    setSelectedRules(prev => {
      if (prev.includes(ruleId)) {
        return prev.filter(id => id !== ruleId)
      } else {
        return [...prev, ruleId]
      }
    })
  }

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null

    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')

    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Convert canvas to base64
    return canvas.toDataURL('image/jpeg', 0.8)
  }

  const drawDetections = (detectionResults) => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const context = canvas.getContext('2d')
    const video = videoRef.current

    // Clear previous drawings
    context.clearRect(0, 0, canvas.width, canvas.height)

    // Draw video frame
    if (video) {
      context.drawImage(video, 0, 0, canvas.width, canvas.height)
    }

    // Draw bounding boxes
    detectionResults.forEach(detection => {
      const { box, class_name, confidence } = detection
      const { x1, y1, x2, y2 } = box

      // Choose color based on class
      const colors = {
        'helmet': '#22c55e',
        'safety-vest': '#eab308',
        'gloves': '#3b82f6',
        'glasses': '#8b5cf6',
        'face-mask': '#ec4899',
      }
      const color = colors[class_name.toLowerCase()] || '#f59e0b'

      // Draw bounding box
      context.strokeStyle = color
      context.lineWidth = 3
      context.strokeRect(x1, y1, x2 - x1, y2 - y1)

      // Draw label background
      const label = `${class_name} (${(confidence * 100).toFixed(0)}%)`
      context.font = 'bold 14px sans-serif'
      const textMetrics = context.measureText(label)
      const textHeight = 20

      context.fillStyle = color
      context.fillRect(x1, y1 - textHeight - 4, textMetrics.width + 10, textHeight + 4)

      // Draw label text
      context.fillStyle = '#ffffff'
      context.fillText(label, x1 + 5, y1 - 8)
    })
  }

  const performDetection = async () => {
    try {
      const frameData = captureFrame()
      if (!frameData) return

      const response = await api.post('/api/v1/live-camera/detect', {
        frame: frameData,
        selected_rules: selectedRules
      })

      if (response.data.success) {
        const detectionResults = response.data.detections || []
        setDetections(detectionResults)
        
        // Update statistics
        const byType = {}
        detectionResults.forEach(det => {
          const className = det.class_name
          byType[className] = (byType[className] || 0) + 1
        })
        setStats({
          total: detectionResults.length,
          byType
        })

        // Draw detections on canvas
        drawDetections(detectionResults)
      }
    } catch (error) {
      console.error('Error during detection:', error)
    }
  }

  const startDetection = () => {
    if (selectedRules.length === 0) {
      alert('Please select at least one safety rule to detect.')
      return
    }

    setIsDetecting(true)
    
    // Perform detection every 500ms
    detectionIntervalRef.current = setInterval(() => {
      performDetection()
    }, 500)
  }

  const stopDetection = () => {
    setIsDetecting(false)
    
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current)
      detectionIntervalRef.current = null
    }

    // Clear canvas
    if (canvasRef.current) {
      const context = canvasRef.current.getContext('2d')
      context.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
      if (videoRef.current) {
        context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height)
      }
    }

    setDetections([])
    setStats({ total: 0, byType: {} })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Live Camera</h1>
          <p className="text-neutral-600 mt-1">Real-time PPE detection from webcam</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Feed */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold">Live Video Feed</h2>
              <div className="flex items-center gap-2">
                {isDetecting && (
                  <span className="flex items-center gap-2 text-sm text-success-600">
                    <span className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-success-500"></span>
                    </span>
                    Detecting
                  </span>
                )}
              </div>
            </div>
            <div className="card-body">
              {cameraError ? (
                <div className="bg-danger-50 border border-danger-200 text-danger-700 p-4 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Icon name="alert" className="w-5 h-5 mt-0.5" />
                    <div>
                      <p className="font-medium">Camera Error</p>
                      <p className="text-sm mt-1">{cameraError}</p>
                      <Button
                        onClick={startCamera}
                        className="mt-3"
                        size="sm"
                      >
                        Retry
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="relative bg-black rounded-lg overflow-hidden">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-auto"
                    style={{ display: isDetecting ? 'none' : 'block' }}
                  />
                  <canvas
                    ref={canvasRef}
                    className="w-full h-auto"
                    style={{ display: isDetecting ? 'block' : 'none' }}
                  />
                </div>
              )}

              {/* Controls */}
              <div className="flex gap-3 mt-4">
                {!isDetecting ? (
                  <Button
                    onClick={startDetection}
                    variant="primary"
                    disabled={selectedRules.length === 0 || !!cameraError}
                    className="flex items-center gap-2"
                  >
                    <Icon name="play" className="w-4 h-4" />
                    Start Detection
                  </Button>
                ) : (
                  <Button
                    onClick={stopDetection}
                    variant="danger"
                    className="flex items-center gap-2"
                  >
                    <Icon name="stop" className="w-4 h-4" />
                    Stop Detection
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Statistics */}
          {isDetecting && (
            <div className="card mt-6">
              <div className="card-header">
                <h2 className="text-lg font-semibold">Detection Statistics</h2>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-primary-50 rounded-lg p-4">
                    <div className="text-2xl font-bold text-primary-600">{stats.total}</div>
                    <div className="text-sm text-neutral-600 mt-1">Total Detections</div>
                  </div>
                  {Object.entries(stats.byType).map(([type, count]) => (
                    <div key={type} className="bg-neutral-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-neutral-900">{count}</div>
                      <div className="text-sm text-neutral-600 mt-1">{type}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Settings Panel */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold">Detection Rules</h2>
            </div>
            <div className="card-body">
              <p className="text-sm text-neutral-600 mb-4">
                Select the safety equipment you want to detect:
              </p>
              
              <div className="space-y-2">
                {AVAILABLE_RULES.map(rule => (
                  <label
                    key={rule.id}
                    className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedRules.includes(rule.id)
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-neutral-200 hover:border-neutral-300 bg-white'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedRules.includes(rule.id)}
                      onChange={() => toggleRule(rule.id)}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                      disabled={isDetecting}
                    />
                    <span className="text-xl">{rule.icon}</span>
                    <span className="flex-1 text-sm font-medium text-neutral-900">
                      {rule.label}
                    </span>
                  </label>
                ))}
              </div>

              <div className="mt-4 p-3 bg-warning-50 border border-warning-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <Icon name="info" className="w-4 h-4 text-warning-600 mt-0.5" />
                  <p className="text-xs text-warning-700">
                    Select at least one rule before starting detection. You cannot change rules while detection is running.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Current Detections */}
          {detections.length > 0 && (
            <div className="card mt-6">
              <div className="card-header">
                <h2 className="text-lg font-semibold">Current Detections</h2>
              </div>
              <div className="card-body">
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {detections.map((detection, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-neutral-50 rounded"
                    >
                      <span className="text-sm font-medium text-neutral-900">
                        {detection.class_name}
                      </span>
                      <span className="text-xs text-neutral-600">
                        {(detection.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
