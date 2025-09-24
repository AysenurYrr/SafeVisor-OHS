import React, { useMemo, useState } from 'react'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Cameras() {
  const { token, user } = useAuth()
  const [selected, setSelected] = useState(1)
  const cameras = useMemo(() => ([
    { id: 1, name: 'Camera-1', desc: 'Demo stream 1 (demo.mp4)' },
    { id: 2, name: 'Camera-2', desc: 'Demo stream 2 (demo2.mp4)' },
    { id: 3, name: 'Camera-3', desc: 'Demo stream 3 (demo3.mp4)' },
  ]), [])

  const src = `${api.defaults.baseURL}/api/v1/cameras/${selected}/stream?token=${encodeURIComponent(token || '')}`

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Cameras</h1>
      </div>
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
          <p className="mb-3 text-sm text-gray-600">Logged in as: {user?.full_name || user?.email}</p>
          <video
            key={selected}
            controls
            style={{ width: '100%', maxHeight: 540, background: '#000' }}
            preload="metadata"
          >
            <source src={src} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <p className="mt-2 text-xs text-gray-500">If the video doesn't start, ensure: backend is running and videos demo.mp4, demo2.mp4, demo3.mp4 exist under app/static/videos/.</p>
        </div>
      </div>
    </div>
  )
}
