import React, { useEffect, useState, useMemo } from 'react'
import { EmployeeLogsAPI } from '../services/api'
import Icon from '../components/Icon'
import Table from '../components/Table'
import Button from '../components/Button'

export default function EmployeeLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')
  const [actionFilter, setActionFilter] = useState('')

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        setLoading(true)
        setError(null)
        const resp = await EmployeeLogsAPI.list(0, 250) // fetch first 250
        if (mounted) setLogs(Array.isArray(resp) ? resp : [])
      } catch (e) {
        console.error('Failed to load employee logs', e)
        if (mounted) setError('Failed to load employee activity logs.')
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => { mounted = false }
  }, [])

  const filtered = useMemo(() => {
    const term = q.toLowerCase()
    return logs.filter(l => {
      if (actionFilter && l.action !== actionFilter) return false
      if (!term) return true
      const actor = l.actor_name || ''
      const employee = l.employee_name || ''
      const details = JSON.stringify(l.details || {})
      return (
        l.action.toLowerCase().includes(term) ||
        actor.toLowerCase().includes(term) ||
        employee.toLowerCase().includes(term) ||
        details.toLowerCase().includes(term)
      )
    })
  }, [logs, q, actionFilter])

  const columns = [
    {
      header: 'Action',
      accessor: 'action',
      cell: (row) => {
        const label = row.action === 'created' ? 'Create' : row.action === 'updated' ? 'Update' : row.action === 'deleted' ? 'Delete' : row.action
        const color = row.action === 'created' ? 'bg-success-100 text-success-700' : row.action === 'updated' ? 'bg-warning-100 text-warning-800' : row.action === 'deleted' ? 'bg-danger-100 text-danger-700' : 'bg-neutral-100 text-neutral-700'
        return <span className={`px-2 py-1 rounded text-xs font-medium ${color}`}>{label}</span>
      }
    },
    {
      header: 'Employee',
      accessor: 'employee_name',
      cell: (row) => row.employee_name || 'Unknown'
    },
    {
      header: 'Actor',
      accessor: 'actor_name',
      cell: (row) => row.actor_name || 'System'
    },
    {
      header: 'Timestamp',
      accessor: 'timestamp',
      cell: (row) => {
        try {
          return new Date(row.timestamp).toLocaleString()
        } catch {
            return row.timestamp
        }
      }
    },
    {
      header: 'Details',
      accessor: 'details',
      cell: (row) => {
        if (!row.details) return <span className='text-neutral-400'>No details</span>
        if (row.details.changed_fields) {
          const fields = Array.isArray(row.details.changed_fields) ? row.details.changed_fields : []
          if (fields.length) {
            return <span className='text-xs text-neutral-700'>Changed: {fields.join(', ')}</span>
          }
        }
        const concise = JSON.stringify(row.details).slice(0, 80)
        return <span title={JSON.stringify(row.details)} className='text-xs text-neutral-600'>{concise}{JSON.stringify(row.details).length > 80 ? '…' : ''}</span>
      }
    }
  ]

  return (
    <div className='space-y-5'>
      <div className='flex flex-col md:flex-row md:items-center md:justify-between gap-4'>
        <div className='flex items-center gap-2'>
          <Icon name='document' className='w-6 h-6 text-primary-600' />
          <h2 className='text-xl font-semibold'>Employee Activity Logs</h2>
        </div>
        <div className='flex gap-2'>
          <div className='relative'>
            <input
              className='input pr-8'
              placeholder='Search logs...'
              value={q}
              onChange={e => setQ(e.target.value)}
            />
            {q && (
              <button className='absolute top-1/2 -translate-y-1/2 right-2 text-neutral-400 hover:text-neutral-600'
                onClick={() => setQ('')}>
                <Icon name='close' className='w-4 h-4' />
              </button>
            )}
          </div>
          <select className='input' value={actionFilter} onChange={e => setActionFilter(e.target.value)}>
            <option value=''>All Actions</option>
            <option value='created'>Create</option>
            <option value='updated'>Update</option>
            <option value='deleted'>Delete</option>
          </select>
        </div>
      </div>

      {error && (
        <div className='card p-4 border border-danger-200 bg-danger-50 text-danger-700 flex items-center gap-2'>
          <Icon name='info' className='w-5 h-5' />
          <span>{error}</span>
        </div>
      )}

      <div className='card p-4'>
        {loading ? (
          <div className='py-10 text-center text-neutral-500 text-sm'>Loading logs...</div>
        ) : filtered.length === 0 ? (
          <div className='py-10 text-center text-neutral-500 text-sm'>No employee activity found.</div>
        ) : (
          <Table
            columns={columns}
            data={filtered}
            empty='No employee activity found.'
          />
        )}
      </div>
    </div>
  )
}
