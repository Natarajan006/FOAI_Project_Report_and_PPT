import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { adminService } from '../../services'
import DecisionPanel from '../../components/DecisionPanel'
import {
  decisionBadgeClass,
  formatDate,
  formatINR,
  getErrorMessage,
  riskBadgeClass,
} from '../../utils/helpers'
import toast from 'react-hot-toast'

export default function AdminApprovals() {
  const [rows, setRows] = useState([])
  const [selected, setSelected] = useState(null)
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [params] = useSearchParams()

  const load = async () => {
    setLoading(true)
    try {
      const res = await adminService.applications({})
      const pending = res.data.filter(
        (r) => !r.admin_decision || r.admin_decision === 'request_info' || r.status === 'manual_review'
      )
      setRows(pending.length ? pending : res.data.filter((r) => r.admin_decision !== 'approved' && r.admin_decision !== 'rejected'))
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    const id = params.get('id')
    if (id) selectApp(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params, rows])

  const selectApp = async (id) => {
    try {
      const res = await adminService.applicationDetail(id)
      setSelected(res.data)
      setNotes('')
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  const decide = async (action) => {
    if (!selected?.application?.id) return
    setBusy(true)
    try {
      await adminService.decide(selected.application.id, { action, notes })
      toast.success(action === 'approve' ? 'Loan approved' : action === 'reject' ? 'Loan rejected' : 'Info requested')
      setSelected(null)
      await load()
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Approve / Reject Loans</h1>
        <p>Final admin decision desk — separate from the applicant self-service tools</p>
      </div>

      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '1.25rem' }}
        className="approval-grid"
      >
        <div className="card table-wrap">
          <h3 style={{ marginBottom: '0.75rem' }}>Pending Decisions</h3>
          {loading ? (
            <div className="loading-state">
              <div className="spinner" />
            </div>
          ) : rows.length === 0 ? (
            <div className="empty-state">All caught up — no pending approvals.</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Applicant</th>
                  <th>Amount</th>
                  <th>AI</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr
                    key={r.id}
                    style={{
                      background:
                        selected?.application?.id === r.id ? 'var(--blue-soft)' : undefined,
                    }}
                  >
                    <td>
                      <strong>{r.full_name}</strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--slate)' }}>{r.loan_type}</div>
                    </td>
                    <td>{formatINR(r.requested_amount)}</td>
                    <td>
                      {r.latest_decision ? (
                        <span className={decisionBadgeClass(r.latest_decision)}>{r.latest_decision}</span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td>
                      <button type="button" className="btn btn-secondary btn-sm" onClick={() => selectApp(r.id)}>
                        Open
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          {!selected ? (
            <div className="empty-state">Select an application to approve or reject.</div>
          ) : (
            <>
              <h3>{selected.application.full_name}</h3>
              <p style={{ color: 'var(--slate)', marginBottom: '0.75rem' }}>
                {selected.application.loan_type} · {formatINR(selected.application.requested_amount)} ·{' '}
                {formatDate(selected.application.created_at)}
              </p>

              <div className="card" style={{ background: '#fffdf8', marginBottom: '1rem' }}>
                <strong>Contact</strong>
                <p>{selected.applicant?.email || 'No email'}</p>
                <p>{selected.applicant?.phone || 'No phone'}</p>
                <div className="contact-actions" style={{ marginTop: 8 }}>
                  {selected.applicant?.email && (
                    <a className="btn btn-secondary btn-sm" href={`mailto:${selected.applicant.email}`}>
                      Email
                    </a>
                  )}
                  {selected.applicant?.phone && (
                    <a className="btn btn-secondary btn-sm" href={`tel:${selected.applicant.phone}`}>
                      Call
                    </a>
                  )}
                </div>
              </div>

              {selected.assessments?.[0] && (
                <>
                  <p style={{ marginBottom: '0.5rem' }}>
                    Risk:{' '}
                    <span className={riskBadgeClass(selected.assessments[0].risk_level)}>
                      {selected.assessments[0].risk_level}
                    </span>
                  </p>
                  <DecisionPanel assessment={selected.assessments[0]} />
                </>
              )}

              <div className="form-group" style={{ marginTop: '1rem' }}>
                <label>Decision notes</label>
                <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button type="button" className="btn btn-primary" disabled={busy} onClick={() => decide('approve')}>
                  Approve
                </button>
                <button type="button" className="btn btn-danger" disabled={busy} onClick={() => decide('reject')}>
                  Reject
                </button>
                <button type="button" className="btn btn-secondary" disabled={busy} onClick={() => decide('request_info')}>
                  Request Info
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      <style>{`@media (max-width:900px){ .approval-grid{ grid-template-columns:1fr !important; } }`}</style>
    </div>
  )
}
