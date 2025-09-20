import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'

export default function DashboardLayout() {
  const [open, setOpen] = useState(true)
  return (
    <div className="min-h-screen flex bg-neutral-50">
      <Sidebar open={open} onToggle={() => setOpen(!open)} />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar onToggleSidebar={() => setOpen(!open)} />
        <main className="flex-1 p-4 md:p-6 lg:p-8 animate-fade-in-custom">
          <div className="container-app">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
