import React, { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import Icon from '../components/Icon'
import Button from '../components/Button'

// Available PPE detection rules
const AVAILABLE_RULES = [
  { id: 'face', label: 'Face Recognition', icon: '👤' },
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
  const [debugMode, setDebugMode] = useState(false)
  const lastSummaryRef = useRef(0)
  
  const videoRef = useRef(null)
  const overlayCanvasRef = useRef(null) // Visible canvas that renders the annotated frame
  const offscreenCanvasRef = useRef(null) // Offscreen canvas for frame capture only
  const annotateCanvasRef = useRef(null) // Offscreen canvas for annotated frames
  const latestFrameRef = useRef({ canvas: null, width: 0, height: 0, annotated: false })
  const latestDetectionsRef = useRef([])
  const streamRef = useRef(null)
  const detectionIntervalRef = useRef(null)
  const isDetectionInProgressRef = useRef(false)
  const shouldContinueDetectionRef = useRef(false)
  const isDetectingRef = useRef(false)
  const [drawTick, setDrawTick] = useState(0)
  const hasAnnotatedFrame = !!latestFrameRef.current?.canvas

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

  const ensureOffscreenCanvas = () => {
    if (!offscreenCanvasRef.current) {
      offscreenCanvasRef.current = document.createElement('canvas')
    }
    return offscreenCanvasRef.current
  }

  const captureFrame = () => {
    const video = videoRef.current
    if (!video || video.videoWidth === 0) return null

    const offscreen = ensureOffscreenCanvas()
    offscreen.width = video.videoWidth
    offscreen.height = video.videoHeight
    const ctx = offscreen.getContext('2d')
    ctx.drawImage(video, 0, 0, offscreen.width, offscreen.height)
    return {
      dataUrl: offscreen.toDataURL('image/jpeg', 0.7),
      width: offscreen.width,
      height: offscreen.height,
      canvas: offscreen,
    }
  }

  const paintDetections = useCallback((ctx, detectionResults, baseWidth, baseHeight, scaleX = 1, scaleY = 1) => {
    if (!ctx || !detectionResults?.length || !baseWidth || !baseHeight) {
      return
    }

    detectionResults.forEach(det => {
      const { box, class_name, confidence, recognized_name, employee_id, recognition_confidence, recognition_distance, recognition_status, recognition_threshold } = det || {}
      if (!box) return
      let { x1, y1, x2, y2 } = box
      if ([x1, y1, x2, y2].some(v => typeof v !== 'number' || Number.isNaN(v))) return
      x1 = Math.max(0, Math.min(baseWidth, x1))
      x2 = Math.max(0, Math.min(baseWidth, x2))
      y1 = Math.max(0, Math.min(baseHeight, y1))
      y2 = Math.max(0, Math.min(baseHeight, y2))
      const cx1 = x1 * scaleX
      const cy1 = y1 * scaleY
      const w = (x2 - x1) * scaleX
      const h = (y2 - y1) * scaleY
      if (w <= 2 || h <= 2) return

      const colors = {
        helmet: '#22c55e',
        'safety-vest': '#eab308',
        gloves: '#3b82f6',
        glasses: '#8b5cf6',
        'face-mask': '#ec4899',
        face: '#10b981',
      }
      const normalizedClass = (class_name || '').toLowerCase()
      const color = colors[normalizedClass] || '#f59e0b'

      ctx.strokeStyle = color
      ctx.lineWidth = 3
      ctx.strokeRect(cx1, cy1, w, h)

      let label
      if (normalizedClass === 'face' && recognized_name) {
        if (recognized_name !== 'Unknown') {
          const pct = recognition_confidence != null ? Math.round(recognition_confidence * 100) : null
          const distFrag = debugMode && recognition_distance != null ? ` d=${recognition_distance.toFixed(3)}` : ''
          label = `${recognized_name}${employee_id ? ` (${employee_id})` : ''}${pct != null ? ` ${pct}%` : ''}${distFrag}`.trim()
        } else {
          if (debugMode) {
            const distFrag = recognition_distance != null ? `d=${recognition_distance.toFixed(3)}` : ''
            const thrFrag = recognition_threshold != null ? ` thr=${recognition_threshold}` : ''
            const stFrag = recognition_status ? ` ${recognition_status}` : ''
            label = `Unknown ${distFrag}${thrFrag}${stFrag}`.trim()
          } else {
            label = 'Unknown'
          }
        }
      } else if (class_name) {
        label = `${class_name} ${confidence != null ? `${Math.round(confidence * 100)}%` : ''}`.trim()
      }

      if (!label) {
        return
      }

      ctx.font = 'bold 14px sans-serif'
      const metrics = ctx.measureText(label)
      const textHeight = 18
      ctx.fillStyle = color
      const rectY = Math.max(0, cy1 - textHeight - 6)
      ctx.fillRect(cx1, rectY, metrics.width + 12, textHeight + 6)
      ctx.fillStyle = '#fff'
      ctx.fillText(label, cx1 + 6, rectY + textHeight - 4)
    })
  }, [debugMode])

  const drawOverlay = useCallback(() => {
    const canvas = overlayCanvasRef.current
    const video = videoRef.current
    const container = canvas?.parentElement
    if (!canvas || !video || !container) return

    const rect = container.getBoundingClientRect()
    const outputW = Math.max(1, Math.round(rect.width || video.clientWidth || latestFrameRef.current.width || 0))
    const outputH = Math.max(1, Math.round(rect.height || video.clientHeight || latestFrameRef.current.height || 0))
    if (!outputW || !outputH) return

    if (canvas.width !== outputW || canvas.height !== outputH) {
      canvas.width = outputW
      canvas.height = outputH
    }

    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const frame = latestFrameRef.current
    if (!frame?.canvas) {
      return
    }

    ctx.drawImage(frame.canvas, 0, 0, frame.width, frame.height, 0, 0, canvas.width, canvas.height)

    if (!frame.annotated) {
      const scaleX = canvas.width / frame.width
      const scaleY = canvas.height / frame.height
      paintDetections(ctx, latestDetectionsRef.current, frame.width, frame.height, scaleX, scaleY)
    }
  }, [paintDetections])

  useEffect(() => {
    drawOverlay()
  }, [drawTick, drawOverlay])

  const performDetection = async () => {
    // Skip if detection is already in progress
    if (isDetectionInProgressRef.current) {
      return
    }

    try {
      isDetectionInProgressRef.current = true
      
      const capturedFrame = captureFrame()
      if (!capturedFrame) {
        isDetectionInProgressRef.current = false
        return
      }

      const { dataUrl, canvas: rawCanvas, width: frameWidth, height: frameHeight } = capturedFrame
      const response = await api.post('/api/v1/live-camera/detect', {
        frame: dataUrl,
        selected_rules: selectedRules
      })

      if (response.data.success && isDetectingRef.current) {
        const detectionResults = response.data.detections || []
        latestDetectionsRef.current = detectionResults
        
        if (debugMode) {
          const now = performance.now()
            if (now - lastSummaryRef.current > 1000) {
              lastSummaryRef.current = now
              const faces = detectionResults.filter(d => d.class_name?.toLowerCase() === 'face')
              if (faces.length) {
                console.table(faces.map(f => ({
                  name: f.recognized_name,
                  status: f.recognition_status,
                  dist: f.recognition_distance?.toFixed(3),
                  thr: f.recognition_threshold,
                  confPct: f.recognition_confidence != null ? Math.round(f.recognition_confidence * 100) : null
                })))
              }
            }
        }
        
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

        if (isDetectingRef.current && rawCanvas) {
          let annotateCanvas = annotateCanvasRef.current
          if (!annotateCanvas) {
            annotateCanvas = document.createElement('canvas')
            annotateCanvasRef.current = annotateCanvas
          }
          annotateCanvas.width = frameWidth
          annotateCanvas.height = frameHeight
          const actx = annotateCanvas.getContext('2d')
          actx.drawImage(rawCanvas, 0, 0, frameWidth, frameHeight)
          paintDetections(actx, detectionResults, frameWidth, frameHeight, 1, 1)
          latestFrameRef.current = {
            canvas: annotateCanvas,
            width: frameWidth,
            height: frameHeight,
            annotated: true,
          }
          setDrawTick(t => t + 1)
        }
      } else if (!response.data.success) {
        console.error('[LiveCamera][Error] Invalid response:', response.data)
      }
    } catch (error) {
      console.error('[LiveCamera][Error] Detection failed:', error)
    } finally {
      isDetectionInProgressRef.current = false
      
      // Schedule next detection if still active
      if (shouldContinueDetectionRef.current) {
        // Use setTimeout instead of setInterval to avoid queueing
        detectionIntervalRef.current = setTimeout(() => {
          performDetection()
        }, 100) // Small delay to prevent tight loop
      }
    }
  }

  const startDetection = () => {
    if (selectedRules.length === 0) {
      alert('Please select at least one safety rule to detect.')
      return
    }

    setIsDetecting(true)
    isDetectingRef.current = true
    shouldContinueDetectionRef.current = true
    latestFrameRef.current = { canvas: null, width: 0, height: 0, annotated: false }
    latestDetectionsRef.current = []
    setDrawTick(t => t + 1)
    
    // Start the detection loop (will self-schedule after each completion)
    performDetection()
  }

  const stopDetection = () => {
    console.log('[LiveCamera] Stopping detection...')
    setIsDetecting(false)
    isDetectingRef.current = false
    shouldContinueDetectionRef.current = false
    
    if (detectionIntervalRef.current) {
      clearTimeout(detectionIntervalRef.current)
      detectionIntervalRef.current = null
    }

    // Clear canvas
    if (overlayCanvasRef.current) {
      const ctx = overlayCanvasRef.current.getContext('2d')
      ctx.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height)
    }

    latestFrameRef.current = { canvas: null, width: 0, height: 0, annotated: false }
    latestDetectionsRef.current = []
    setDrawTick(t => t + 1)
    setDetections([])
    setStats({ total: 0, byType: {} })
    console.log('[LiveCamera] Detection stopped, overlays cleared')
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
                    className="w-full h-auto block"
                    style={{ opacity: isDetecting && hasAnnotatedFrame ? 0 : 1, transition: 'opacity 120ms linear' }}
                  />
                  {/* Overlay canvas: same intrinsic size as video, scaled by CSS */}
                  <canvas
                    ref={overlayCanvasRef}
                    className="absolute inset-0 w-full h-full"
                    style={{ pointerEvents: 'none', opacity: isDetecting && hasAnnotatedFrame ? 1 : 0, transition: 'opacity 120ms linear' }}
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
                <Button
                  onClick={() => setDebugMode(d => !d)}
                  variant={debugMode ? 'secondary' : 'outline'}
                  className="flex items-center gap-1 text-xs"
                  title="Toggle verbose face recognition debug"
                >
                  {debugMode ? 'Debug ON' : 'Debug OFF'}
                </Button>
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
                      <div className="flex-1">
                        <span className="text-sm font-medium text-neutral-900">
                          {detection.class_name}
                        </span>
                        {detection.recognized_name && detection.class_name?.toLowerCase() === 'face' && (
                          <span className="text-xs text-primary-600 ml-2">
                            ({detection.recognized_name})
                          </span>
                        )}
                      </div>
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
