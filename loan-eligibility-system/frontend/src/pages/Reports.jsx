import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { assessmentService } from '../services'
import { formatDate, decisionBadgeClass, getErrorMessage } from '../utils/helpers'
import toast from 'react-hot-toast'

export default function Reports() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [params] = useSearchParams()

  useEffect(() => {
    assessmentService
      .history()
      .then((res) => setRows(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const id = params.get('id')
    if (id && rows.length) {
      download(id)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params, rows])

  const download = async (id) => {
    try {
      const res = await assessmentService.downloadReport(id)
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `assessment_${id}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('PDF downloaded')
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Reports</h1>
        <p>Download PDF assessment reports (no passwords included)</p>
      </div>
      <div className="card table-wrap">
        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
          </div>
        ) : rows.length === 0 ? (
          <div className="empty-state">No reports available. Complete an assessment first.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Decision</th>
                <th>Risk</th>
                <th>Report</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{formatDate(r.timestamp)}</td>
                  <td>
                    <span className={decisionBadgeClass(r.decision)}>{r.decision}</span>
                  </td>
                  <td>{r.risk_level}</td>
                  <td>
                    <button type="button" className="btn btn-primary btn-sm" onClick={() => download(r.id)}>
                      Download PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
