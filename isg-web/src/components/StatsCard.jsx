import React from 'react'

export default function StatsCard({ title, value, subtitle, icon, trend, trendDirection = 'up', color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
  }

  const getTrendIcon = () => {
    if (trendDirection === 'up') return '↗'
    if (trendDirection === 'down') return '↘'
    return '→'
  }

  const getTrendColor = () => {
    if (trendDirection === 'up' && color === 'green') return 'text-green-600'
    if (trendDirection === 'up' && color === 'red') return 'text-red-600'
    if (trendDirection === 'down' && color === 'green') return 'text-red-600'
    if (trendDirection === 'down' && color === 'red') return 'text-green-600'
    return 'text-gray-600'
  }

  return (
    <div className={`card p-6 border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={`flex items-center text-sm mt-2 ${getTrendColor()}`}>
              <span className="mr-1">{getTrendIcon()}</span>
              <span>{trend}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className={`text-3xl opacity-75 ${colorClasses[color].split(' ')[1]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}