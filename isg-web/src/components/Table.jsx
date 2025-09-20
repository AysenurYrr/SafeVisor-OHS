import React from 'react'

export default function Table({ columns, data, rowKey = 'id', empty = 'No data' }) {
  return (
    <div className="table-container card">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map(col => (
              <th key={col.key || col.accessor} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data?.length ? (
            data.map((row) => (
              <tr key={row[rowKey] || Math.random()} className="hover:bg-gray-50">
                {columns.map((col) => (
                  <td key={col.key || col.accessor} className="px-4 py-3 text-sm text-gray-700">
                    {col.cell ? col.cell(row) : row[col.accessor]}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td className="px-4 py-6 text-center text-sm text-gray-500" colSpan={columns.length}>{empty}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
