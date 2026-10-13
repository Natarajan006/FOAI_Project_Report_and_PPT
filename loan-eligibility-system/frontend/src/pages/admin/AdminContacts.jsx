import { useEffect, useState } from 'react'
import { adminService } from '../../services'
import Modal from '../../components/Modal'
import { formatDate, formatINR, getErrorMessage } from '../../utils/helpers'
import toast from 'react-hot-toast'

export default function AdminContacts() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [message, setMessage] = useState('')
  const [subject, setSubject] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    adminService
      .contacts()
      .then((res) => setRows(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const openContact = (row) => {
    setSelected(row)
    setSubject(`Regarding your ${row.loan_type} application`)
    setMessage(
      `Dear ${row.full_name},\n\nWe are contacting you about your loan application for ${formatINR(row.requested_amount)} (${row.loan_type}).\n\n`
    )
  }

  const send = async (channel) => {
    if (!selected || !message.trim()) {
      toast.error('Please enter a message')
      return
    }
    setBusy(true)
    try {
      const res = await adminService.contact(selected.id, {
        channel,
        subject,
        message,
      })
      toast.success(`Contact logged via ${channel}`)
      if (channel === 'email' && res.data.mailto_link) window.open(res.data.mailto_link, '_blank')
      if (channel === 'phone' && res.data.tel_link) window.open(res.data.tel_link, '_self')
      if (channel === 'message' && res.data.whatsapp_link) {
        /* optional — don't auto-open WhatsApp unless user wants */
      }
      setSelected(null)
      const refreshed = await adminService.contacts()
      setRows(refreshed.data)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Contact Applicants</h1>
        <p>Reach applicants by email, phone, or logged message about their loan status</p>
      </div>

      <div className="card table-wrap">
        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
          </div>
        ) : rows.length === 0 ? (
          <div className="empty-state">No applicants to contact yet.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Applicant</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Loan</th>
                <th>Status</th>
                <th>Contacts</th>
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
                  <td>{r.email || '—'}</td>
                  <td>{r.phone || '—'}</td>
                  <td>
                    {r.loan_type}
                    <div style={{ fontSize: '0.8rem' }}>{formatINR(r.requested_amount)}</div>
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{r.status?.replace('_', ' ')}</td>
                  <td>{r.contact_count || 0}</td>
                  <td>
                    <div className="contact-actions">
                      {r.email && (
                        <a className="btn btn-secondary btn-sm" href={`mailto:${r.email}`}>
                          Email
                        </a>
                      )}
                      {r.phone && (
                        <a className="btn btn-secondary btn-sm" href={`tel:${r.phone}`}>
                          Call
                        </a>
                      )}
                      <button type="button" className="btn btn-primary btn-sm" onClick={() => openContact(r)}>
                        Message
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={!!selected} title="Contact Applicant" onClose={() => setSelected(null)}>
        {selected && (
          <>
            <p>
              <strong>{selected.full_name}</strong>
            </p>
            <p>
              {selected.email || 'No email'} · {selected.phone || 'No phone'}
            </p>
            <div className="form-group">
              <label>Subject</label>
              <input value={subject} onChange={(e) => setSubject(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Message</label>
              <textarea rows={6} value={message} onChange={(e) => setMessage(e.target.value)} />
            </div>
            <div className="contact-actions">
              <button type="button" className="btn btn-primary" disabled={busy || !selected.email} onClick={() => send('email')}>
                Send Email
              </button>
              <button type="button" className="btn btn-secondary" disabled={busy || !selected.phone} onClick={() => send('phone')}>
                Call &amp; Log
              </button>
              <button type="button" className="btn btn-secondary" disabled={busy} onClick={() => send('message')}>
                Log Message
              </button>
            </div>
            <p className="form-hint" style={{ marginTop: '0.75rem' }}>
              Email opens your mail client with the message pre-filled. All contacts are saved in the audit log.
            </p>
          </>
        )}
      </Modal>
    </div>
  )
}
