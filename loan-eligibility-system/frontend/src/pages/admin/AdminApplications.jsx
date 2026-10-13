import { useEffect, useState } from 'react'
import { adminService } from '../../services'
import DecisionPanel from '../../components/DecisionPanel'
import Modal from '../../components/Modal'
import {
  decisionBadgeClass,
  formatDate,
  formatINR,
  getErrorMessage,
  riskBadgeClass,
} from '../../utils/helpers'
import toast from 'react-hot-toast'

export default function AdminApplications() {
  const [rows, setRows] = useState([])
  const [status, setStatus] = useState('')
  const [risk, setRisk] = useState('')
  const [search, setSearch] = useState('')
  const [detail, setDetail] = useState(null)
  const [notes, setNotes] = useState('')
  const [contactMsg, setContactMsg] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)

  const load = () => {
    setLoading(true)
    adminService
      .applications({
        status: status || undefined,
        risk: risk || undefined,
        search: search || undefined,
      })
      .then((res) => setRows(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const openDetail = async (id) => {
    try {
      const res = await adminService.applicationDetail(id)
      setDetail(res.data)
      setNotes('')
      setContactMsg(
        `Hello ${res.data.applicant?.full_name || ''}, regarding your ${res.data.application?.loan_type || 'loan'} application...`
      )
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  const decide = async (action) => {
    if (!detail?.application?.id) return
    setBusy(true)
    try {
      const res = await adminService.decide(detail.application.id, { action, notes })
      setDetail(res.data)
      toast.success(
        action === 'approve'
          ? 'Application approved'
          : action === 'reject'
            ? 'Application rejected'
            : 'More information requested'
      )
      load()
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const sendContact = async (channel) => {
    if (!detail?.application?.id || !contactMsg.trim()) {
      toast.error('Enter a message before contacting')
      return
    }
    setBusy(true)
    try {
      const res = await adminService.contact(detail.application.id, {
        channel,
        message: contactMsg,
        subject: `Loan application update — ${detail.application.loan_type}`,
      })
      toast.success('Contact logged')
      if (channel === 'email' && res.data.mailto_link) {
        window.open(res.data.mailto_link, '_blank')
      } else if (channel === 'phone' && res.data.tel_link) {
        window.open(res.data.tel_link, '_self')
      }
      const refreshed = await adminService.applicationDetail(detail.application.id)
      setDetail(refreshed.data)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Loan Applications</h1>
        <p>View every application, AI reasoning, approve/reject, and contact the applicant</p>
      </div>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <div className="form-row">
          <div className="form-group">
            <label>Search</label>
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Name, loan type…" />
          </div>
          <div className="form-group">
            <label>Status</label>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All</option>
              <option value="eligible">Eligible</option>
              <option value="not_eligible">Not Eligible</option>
              <option value="manual_review">Manual Review</option>
              <option value="submitted">Submitted</option>
            </select>
          </div>
          <div className="form-group">
            <label>Risk</label>
            <select value={risk} onChange={(e) => setRisk(e.target.value)}>
              <option value="">All</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>
        </div>
        <button type="button" className="btn btn-primary btn-sm" onClick={load}>
          Apply Filters
        </button>
      </div>

      <div className="card table-wrap">
        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
          </div>
        ) : rows.length === 0 ? (
          <div className="empty-state">No applications found.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Applicant</th>
                <th>Contact</th>
                <th>Loan</th>
                <th>Amount</th>
                <th>AI Decision</th>
                <th>Admin</th>
                <th>Risk</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>
                    <strong>{r.full_name}</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--slate)' }}>{formatDate(r.created_at)}</div>
                  </td>
                  <td>
                    <div style={{ fontSize: '0.85rem' }}>{r.applicant_email || '—'}</div>
                    <div style={{ fontSize: '0.85rem' }}>{r.applicant_phone || '—'}</div>
                  </td>
                  <td>{r.loan_type}</td>
                  <td>{formatINR(r.requested_amount)}</td>
                  <td>
                    {r.latest_decision ? (
                      <span className={decisionBadgeClass(r.latest_decision)}>{r.latest_decision}</span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>
                    {r.admin_decision ? (
                      <span
                        className={
                          r.admin_decision === 'approved'
                            ? 'badge badge-eligible'
                            : r.admin_decision === 'rejected'
                              ? 'badge badge-rejected'
                              : 'badge badge-review'
                        }
                      >
                        {r.admin_decision.replace('_', ' ')}
                      </span>
                    ) : (
                      <span className="badge badge-review">Pending</span>
                    )}
                  </td>
                  <td>
                    {r.latest_risk ? (
                      <span className={riskBadgeClass(r.latest_risk)}>{r.latest_risk}</span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => openDetail(r.id)}>
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={!!detail} title="Application Review & Contact" onClose={() => setDetail(null)}>
        {detail && (
          <>
            <div className="card" style={{ marginBottom: '1rem', background: '#fffdf8' }}>
              <h4>Applicant Contact</h4>
              <p>
                <strong>{detail.applicant?.full_name || detail.application.full_name}</strong>
              </p>
              <p>Email: {detail.applicant?.email || '—'}</p>
              <p>Phone: {detail.applicant?.phone || '—'}</p>
              <div className="contact-actions" style={{ marginTop: '0.75rem' }}>
                {detail.applicant?.email && (
                  <a className="btn btn-secondary btn-sm" href={`mailto:${detail.applicant.email}`}>
                    Open Email
                  </a>
                )}
                {detail.applicant?.phone && (
                  <a className="btn btn-secondary btn-sm" href={`tel:${detail.applicant.phone}`}>
                    Call
                  </a>
                )}
                {detail.applicant?.phone && (
                  <a
                    className="btn btn-secondary btn-sm"
                    href={`https://wa.me/${String(detail.applicant.phone).replace(/\D/g, '')}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    WhatsApp
                  </a>
                )}
              </div>
            </div>

            <h4>Loan Summary</h4>
            <p>
              {detail.application.loan_type} · {formatINR(detail.application.requested_amount)} ·{' '}
              Tenure {detail.application.tenure_months} months
            </p>
            <p>
              Income {formatINR(detail.application.monthly_income)} · Demo Credit{' '}
              {detail.application.credit_score} · Age {detail.application.age}
            </p>
            {detail.application.admin_decision && (
              <p>
                Admin decision:{' '}
                <strong style={{ textTransform: 'capitalize' }}>
                  {detail.application.admin_decision.replace('_', ' ')}
                </strong>
                {detail.application.admin_notes ? ` — ${detail.application.admin_notes}` : ''}
              </p>
            )}

            {detail.assessments?.[0] && (
              <div style={{ marginTop: '1rem' }}>
                <DecisionPanel assessment={detail.assessments[0]} />
              </div>
            )}

            <div style={{ marginTop: '1.25rem' }}>
              <h4>Admin Decision</h4>
              <div className="form-group">
                <label>Notes</label>
                <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional approval / rejection notes" />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => decide('approve')}>
                  Approve Loan
                </button>
                <button type="button" className="btn btn-danger btn-sm" disabled={busy} onClick={() => decide('reject')}>
                  Reject Loan
                </button>
                <button type="button" className="btn btn-secondary btn-sm" disabled={busy} onClick={() => decide('request_info')}>
                  Request More Info
                </button>
              </div>
            </div>

            <div style={{ marginTop: '1.25rem' }}>
              <h4>Contact Applicant</h4>
              <div className="form-group">
                <label>Message</label>
                <textarea rows={3} value={contactMsg} onChange={(e) => setContactMsg(e.target.value)} />
              </div>
              <div className="contact-actions">
                <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => sendContact('email')}>
                  Log &amp; Email
                </button>
                <button type="button" className="btn btn-secondary btn-sm" disabled={busy} onClick={() => sendContact('phone')}>
                  Log &amp; Call
                </button>
                <button type="button" className="btn btn-secondary btn-sm" disabled={busy} onClick={() => sendContact('message')}>
                  Log Message Only
                </button>
              </div>
            </div>

            {(detail.contact_history || []).length > 0 && (
              <div style={{ marginTop: '1.25rem' }}>
                <h4>Contact History</h4>
                <ul className="reasons-list">
                  {detail.contact_history.map((c) => (
                    <li key={c.id}>
                      <strong>{c.channel}</strong> · {formatDate(c.timestamp)} — {c.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </Modal>
    </div>
  )
}
