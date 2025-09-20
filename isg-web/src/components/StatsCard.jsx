import React from 'react'
import Icon from './Icon'

export default function StatsCard({ 
  title, 
  value, 
  change, 
  changeType, 
  icon, 
  iconColor = 'text-primary-600',
  className = '' 
}) {
  const changeClasses = {
    positive: 'stat-change-positive',
    negative: 'stat-change-negative',
    neutral: 'text-neutral-600'
  }
  
  return (
    <div className={`stat-card ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="stat-label">{title}</p>
          <p className="stat-value">{value}</p>
          {change && (
            <p className={changeClasses[changeType] || changeClasses.neutral}>
              {changeType === 'positive' && '+'}
              {change}
            </p>
          )}
        </div>
        {icon && (
          <div className={`p-3 rounded-xl bg-neutral-50 ${iconColor}`}>
            <Icon name={icon} className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  )
}

export function StatsGrid({ stats = [], className = '' }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
      {stats.map((stat, index) => (
        <StatsCard key={index} {...stat} />
      ))}
    </div>
  )
}