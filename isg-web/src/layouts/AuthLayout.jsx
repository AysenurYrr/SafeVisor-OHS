import React from 'react'
import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-neutral-50 px-4">
      <div className="w-full max-w-md">
        <div className="card p-8 shadow-large">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
