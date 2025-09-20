import React from 'react'
import Icon from './Icon'

export default function Table({ 
  columns, 
  data, 
  rowKey = 'id', 
  empty = 'No data available',
  className = '',
  actions = null
}) {
  const hasActions = actions && actions.length > 0
  
  return (
    <div className={`table-container ${className}`}>
      <table className="table">
        <thead className="table-header">
          <tr>
            {columns.map(col => (
              <th key={col.key || col.accessor} className="table-header-cell">
                <div className="flex items-center gap-2">
                  {col.icon && <Icon name={col.icon} className="w-4 h-4" />}
                  {col.header}
                </div>
              </th>
            ))}
            {hasActions && (
              <th className="table-header-cell">Actions</th>
            )}
          </tr>
        </thead>
        <tbody className="table-body">
          {data?.length ? (
            data.map((row) => (
              <tr key={row[rowKey] || Math.random()} className="table-row">
                {columns.map((col) => (
                  <td key={col.key || col.accessor} className="table-cell">
                    {col.cell ? col.cell(row) : row[col.accessor]}
                  </td>
                ))}
                {hasActions && (
                  <td className="table-cell">
                    <div className="flex items-center gap-2">
                      {actions.map((action, index) => (
                        <button
                          key={index}
                          onClick={() => action.onClick(row)}
                          className={`btn-ghost btn-sm ${action.className || ''}`}
                          title={action.title}
                        >
                          <Icon name={action.icon} className="w-4 h-4" />
                        </button>
                      ))}
                    </div>
                  </td>
                )}
              </tr>
            ))
          ) : (
            <tr>
              <td 
                className="table-cell text-center text-neutral-500 py-12" 
                colSpan={columns.length + (hasActions ? 1 : 0)}
              >
                <div className="flex flex-col items-center gap-3">
                  <Icon name="document" className="w-12 h-12 text-neutral-400" />
                  {empty}
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

export function StatusBadge({ status, className = '' }) {
  const statusConfig = {
    active: { variant: 'badge-success', text: 'Active' },
    inactive: { variant: 'badge-neutral', text: 'Inactive' },
    online: { variant: 'badge-success', text: 'Online' },
    offline: { variant: 'badge-neutral', text: 'Offline' },
    warning: { variant: 'badge-warning', text: 'Warning' },
    error: { variant: 'badge-danger', text: 'Error' },
    pending: { variant: 'badge-warning', text: 'Pending' },
    completed: { variant: 'badge-success', text: 'Completed' },
  }
  
  const config = statusConfig[status] || statusConfig.inactive
  
  return (
    <span className={`${config.variant} ${className}`}>
      {config.text}
    </span>
  )
}
