import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Icon from './Icon'

function NavItem({ to, icon, children, badge = null }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => 
        `nav-item ${isActive ? 'nav-item-active' : 'text-neutral-700 hover:text-neutral-900'}`
      }
    >
      <Icon name={icon} className="w-5 h-5 flex-shrink-0" />
      <span className="flex-1">{children}</span>
      {badge && (
        <span className="badge-danger text-xs">{badge}</span>
      )}
    </NavLink>
  )
}

function NavSection({ title, children }) {
  return (
    <div className="space-y-1">
      <div className="px-3 py-2 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
        {title}
      </div>
      <div className="space-y-1">
        {children}
      </div>
    </div>
  )
}

export default function Sidebar({ open }) {
  const { user } = useAuth()
  const isAdmin = user?.role?.name === 'Admin' || user?.role === 'Admin (IT)'

  return (
    <aside className={`
      bg-white border-r border-neutral-200 shadow-soft
      ${open ? 'w-64' : 'w-20'} 
      transition-all duration-300 ease-in-out
      hidden md:flex flex-col
    `}>
      {/* Header */}
      <div className="h-16 border-b border-neutral-200 flex items-center px-4">
        {open ? (
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-primary-600 rounded-lg">
              <Icon name="safety-solid" className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-neutral-900">SafeVisor</span>
          </div>
        ) : (
          <div className="p-1.5 bg-primary-600 rounded-lg mx-auto">
            <Icon name="safety-solid" className="w-5 h-5 text-white" />
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
        {open ? (
          <>
            <NavSection title="Main">
              <NavItem to="/dashboard" icon="dashboard">
                Dashboard
              </NavItem>
              <NavItem to="/employees" icon="employees">
                Employees
              </NavItem>
              <NavItem to="/cameras" icon="cameras">
                Cameras
              </NavItem>
              <NavItem to="/factory-areas" icon="building">
                Factory Areas
              </NavItem>
            </NavSection>

            <NavSection title="Safety Events">
              <NavItem to="/events/violations" icon="violations" badge="3">
                PPE Violations
              </NavItem>
              <NavItem to="/events/pose" icon="clock">
                Pose Alerts
              </NavItem>
            </NavSection>

            {isAdmin && (
              <NavSection title="Administration">
                <NavItem to="/admin/users" icon="settings">
                  User Management
                </NavItem>
              </NavSection>
            )}
          </>
        ) : (
          <div className="space-y-4">
            <NavLink
              to="/dashboard"
              className={({ isActive }) => 
                `flex items-center justify-center p-3 rounded-lg transition-colors ${
                  isActive ? 'bg-primary-50 text-primary-600' : 'text-neutral-600 hover:bg-neutral-100'
                }`
              }
              title="Dashboard"
            >
              <Icon name="dashboard" className="w-6 h-6" />
            </NavLink>
            <NavLink
              to="/employees"
              className={({ isActive }) => 
                `flex items-center justify-center p-3 rounded-lg transition-colors ${
                  isActive ? 'bg-primary-50 text-primary-600' : 'text-neutral-600 hover:bg-neutral-100'
                }`
              }
              title="Employees"
            >
              <Icon name="employees" className="w-6 h-6" />
            </NavLink>
            <NavLink
              to="/cameras"
              className={({ isActive }) => 
                `flex items-center justify-center p-3 rounded-lg transition-colors ${
                  isActive ? 'bg-primary-50 text-primary-600' : 'text-neutral-600 hover:bg-neutral-100'
                }`
              }
              title="Cameras"
            >
              <Icon name="cameras" className="w-6 h-6" />
            </NavLink>
            <NavLink
              to="/factory-areas"
              className={({ isActive }) => 
                `flex items-center justify-center p-3 rounded-lg transition-colors ${
                  isActive ? 'bg-primary-50 text-primary-600' : 'text-neutral-600 hover:bg-neutral-100'
                }`
              }
              title="Factory Areas"
            >
              <Icon name="building" className="w-6 h-6" />
            </NavLink>
            <NavLink
              to="/events/violations"
              className={({ isActive }) => 
                `relative flex items-center justify-center p-3 rounded-lg transition-colors ${
                  isActive ? 'bg-primary-50 text-primary-600' : 'text-neutral-600 hover:bg-neutral-100'
                }`
              }
              title="PPE Violations"
            >
              <Icon name="violations" className="w-6 h-6" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></span>
            </NavLink>
            {isAdmin && (
              <NavLink
                to="/admin/users"
                className={({ isActive }) => 
                  `flex items-center justify-center p-3 rounded-lg transition-colors ${
                    isActive ? 'bg-primary-50 text-primary-600' : 'text-neutral-600 hover:bg-neutral-100'
                  }`
                }
                title="Admin"
              >
                <Icon name="settings" className="w-6 h-6" />
              </NavLink>
            )}
          </div>
        )}
      </nav>

      {/* Footer */}
      {open && (
        <div className="p-4 border-t border-neutral-200">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-neutral-50">
            <div className="status-online"></div>
            <div className="text-sm">
              <div className="font-medium text-neutral-900">System Status</div>
              <div className="text-neutral-600">All systems operational</div>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
