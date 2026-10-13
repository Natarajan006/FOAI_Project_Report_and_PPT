import { useEffect, useState } from 'react'
import { assessmentService } from '../services'
import DecisionPanel from '../components/DecisionPanel'
import Modal from '../components/Modal'
import {
  decisionBadgeClass,
  formatDate,
  formatINR,
  getErrorMessage,
  riskBadgeClass,
} from '../utils/helpers'
import toast from 'react-hot-toast'

export default function History() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    assessmentService
      .history()
      .then((res) => setRows(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const download = async (id) => {
    try {
      const res = await assessmentService.downloadReport(id)
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `assessment_${id}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Report downloaded')
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner" />
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Assessment History</h1>
        <p>Previous Forward Chaining assessments</p>
      </div>

      <div className="card table-wrap">
        {rows.length === 0 ? (
          <div className="empty-state">No assessments yet.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Decision</th>
                <th>Risk</th>
                <th>Credit</th>
                <th>DTI</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{formatDate(r.timestamp)}</td>
                  <td>
                    <span className={decisionBadgeClass(r.decision)}>{r.decision}</span>
                  </td>
                  <td>
                    <span className={riskBadgeClass(r.risk_level)}>{r.risk_level}</span>
                  </td>
                  <td>{r.financial_summary?.credit_score ?? '—'}</td>
                  <td>{r.financial_summary?.debt_to_income_ratio ?? '—'}%</td>
                  <td>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => setSelected(r)}>
                      View Details
                    </button>{' '}
                    <button type="button" className="btn btn-primary btn-sm" onClick={() => download(r.id)}>
                      Download Report
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={!!selected} title="Assessment Details" onClose={() => setSelected(null)}>
        {selected && (
          <>
            <p style={{ marginBottom: '0.75rem' }}>
              Requested: {formatINR(selected.financial_summary?.requested_amount)} · EMI:{' '}
              {formatINR(selected.financial_summary?.estimated_new_emi)}
            </p>
            <DecisionPanel assessment={selected} />
            {selected.derived_facts?.length > 0 && (
              <>
                <h4 style={{ marginTop: '1rem' }}>Derived Facts</h4>
                <div className="rules-fired">
                  {selected.derived_facts.map((f) => (
                    <span className="rule-chip" key={f}>
                      {f}
                    </span>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </Modal>
    </div>
  )
}
