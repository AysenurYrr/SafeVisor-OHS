import React from 'react'

export default function Loading({ type = 'spinner', size = 'md', className = '' }) {
  if (type === 'spinner') {
    const sizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
      xl: 'w-12 h-12'
    }
    
    return (
      <div className={`inline-flex items-center justify-center ${className}`}>
        <div className={`animate-spin rounded-full border-2 border-neutral-300 border-t-primary-600 ${sizeClasses[size]}`} />
      </div>
    )
  }
  
  if (type === 'skeleton-text') {
    return <div className={`skeleton-text ${className}`} />
  }
  
  if (type === 'skeleton-title') {
    return <div className={`skeleton-title ${className}`} />
  }
  
  if (type === 'skeleton-avatar') {
    return <div className={`skeleton-avatar ${className}`} />
  }
  
  return null
}

export function SkeletonCard({ lines = 3, className = '' }) {
  return (
    <div className={`card p-6 space-y-4 ${className}`}>
      <div className="skeleton-title w-1/3" />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`skeleton-text ${i === lines - 1 ? 'w-2/3' : 'w-full'}`} />
      ))}
    </div>
  )
}

export function SkeletonTable({ rows = 5, cols = 4, className = '' }) {
  return (
    <div className={`table-container ${className}`}>
      <table className="table">
        <thead className="table-header">
          <tr>
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i} className="table-header-cell">
                <div className="skeleton-text w-20" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="table-body">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: cols }).map((_, colIndex) => (
                <td key={colIndex} className="table-cell">
                  <div className={`skeleton-text ${colIndex === 0 ? 'w-32' : 'w-16'}`} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function SkeletonStats({ count = 4, className = '' }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="stat-card">
          <div className="skeleton-text w-16 mb-2" />
          <div className="skeleton-title w-20 mb-3" />
          <div className="skeleton-text w-12" />
        </div>
      ))}
    </div>
  )
}