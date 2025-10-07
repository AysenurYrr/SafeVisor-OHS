import React, { useState } from 'react'
import Icon from '../components/Icon'
import Employees from './Employees'
import Departments from './Departments'
import Positions from './Positions'
import EmployeeLogs from './EmployeeLogs'

export default function EmployeeManagement() {
  const [activeTab, setActiveTab] = useState('employees')

  const tabs = [
    { id: 'employees', label: 'Employees', icon: 'employees' },
    { id: 'departments', label: 'Departments', icon: 'building' },
    { id: 'positions', label: 'Positions', icon: 'tag' },
    { id: 'logs', label: 'Logs', icon: 'document' }
  ]

  return (
    <div className="space-y-6 animate-fade-in-custom">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
            <Icon name="employees" className="w-8 h-8 text-primary-600" />
            Employee Management
          </h1>
          <p className="text-neutral-600 mt-1">
            Manage employees, departments, and positions
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="card p-0 overflow-hidden">
        <div className="flex border-b border-neutral-200">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex-1 flex items-center justify-center gap-2 px-6 py-4 font-medium transition-colors
                ${activeTab === tab.id 
                  ? 'bg-primary-50 text-primary-600 border-b-2 border-primary-600' 
                  : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
                }
              `}
            >
              <Icon name={tab.icon} className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'employees' && <Employees embedded />}
          {activeTab === 'departments' && <Departments />}
          {activeTab === 'positions' && <Positions />}
          {activeTab === 'logs' && <EmployeeLogs />}
        </div>
      </div>
    </div>
  )
}
