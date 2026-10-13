import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { loanService, assessmentService } from '../services'
import DecisionPanel from '../components/DecisionPanel'
import { formatINR, getErrorMessage, decisionBadgeClass } from '../utils/helpers'
import toast from 'react-hot-toast'

export default function AssessmentPage() {
  const [apps, setApps] = useState([])
  const [appId, setAppId] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    loanService
      .list()
      .then((res) => {
        setApps(res.data)
        if (res.data[0]) setAppId(res.data[0].id)
      })
      .catch((err) => toast.error(getErrorMessage(err)))
  }, [])

  const run = async (e) => {
    e.preventDefault()
    if (!appId) {
      toast.error('Select an application or apply for a loan first')
      return
    }
    setBusy(true)
    try {
      const res = await assessmentService.evaluate(appId)
      setResult(res.data)
      toast.success('Assessment complete')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Eligibility Assessment</h1>
        <p>Re-run Forward Chaining on an existing application</p>
      </div>

      <form className="card" onSubmit={run} style={{ marginBottom: '1.25rem' }}>
        {apps.length === 0 ? (
          <div className="empty-state">
            <p>No applications found.</p>
            <Link to="/apply" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Apply for Loan
            </Link>
          </div>
        ) : (
          <>
            <div className="form-group">
              <label>Select Application</label>
              <select value={appId} onChange={(e) => setAppId(e.target.value)}>
                {apps.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.loan_type} — {formatINR(a.requested_amount)} —{' '}
                    <span className={decisionBadgeClass(a.status)}>{a.status}</span>
                  </option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? 'Running Forward Chaining…' : 'Evaluate Eligibility'}
            </button>
          </>
        )}
      </form>

      {result && <DecisionPanel assessment={result} />}
    </div>
  )
}
