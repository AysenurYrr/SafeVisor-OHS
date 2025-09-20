import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'

export default function DashboardLayout() {
  const [open, setOpen] = useState(true)
  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar open={open} onToggle={() => setOpen(!open)} />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar onToggleSidebar={() => setOpen(!open)} />
        <main className="p-4 md:p-6 lg:p-8 flex-1">
          <div className="container-app">
            <Outlet />
          </div>
        </main>
      </div>
      
      {/* Mobile overlay when sidebar is open */}
      {open && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setOpen(false)}
        />
      )}
    </div>
  )
}
