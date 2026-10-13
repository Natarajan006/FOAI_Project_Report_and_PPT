import { useEffect, useState } from 'react'
import { loanService, aiService } from '../services'
import DecisionPanel from '../components/DecisionPanel'
import { formatINR, getErrorMessage, decisionEmoji } from '../utils/helpers'
import toast from 'react-hot-toast'

export default function WhatIf() {
  const [apps, setApps] = useState([])
  const [appId, setAppId] = useState('')
  const [overrides, setOverrides] = useState({
    requested_amount: '',
    tenure_months: '',
    interest_rate: '',
    monthly_income: '',
    existing_emi: '',
    credit_score: '',
  })
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

  const set = (k) => (e) => setOverrides((o) => ({ ...o, [k]: e.target.value }))

  const run = async (e) => {
    e.preventDefault()
    if (!appId) {
      toast.error('Select an application')
      return
    }
    setBusy(true)
    try {
      const payload = { application_id: appId }
      Object.entries(overrides).forEach(([k, v]) => {
        if (v !== '') payload[k] = Number(v)
      })
      const res = await aiService.whatIf(payload)
      setResult(res.data)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>What-If Simulator</h1>
        <p>Modify parameters and re-run Forward Chaining — see which rules change</p>
      </div>

      <form className="card" onSubmit={run} style={{ marginBottom: '1.25rem' }}>
        <div className="form-group">
          <label>Base Application</label>
          <select value={appId} onChange={(e) => setAppId(e.target.value)} required>
            <option value="">Select…</option>
            {apps.map((a) => (
              <option key={a.id} value={a.id}>
                {a.loan_type} — {formatINR(a.requested_amount)} ({a.status})
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Loan Amount</label>
            <input type="number" min={1} value={overrides.requested_amount} onChange={set('requested_amount')} placeholder="Leave blank to keep" />
          </div>
          <div className="form-group">
            <label>Tenure (months)</label>
            <input type="number" min={6} value={overrides.tenure_months} onChange={set('tenure_months')} />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Interest Rate %</label>
            <input type="number" step={0.1} value={overrides.interest_rate} onChange={set('interest_rate')} />
          </div>
          <div className="form-group">
            <label>Monthly Income</label>
            <input type="number" min={1} value={overrides.monthly_income} onChange={set('monthly_income')} />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Existing EMI</label>
            <input type="number" min={0} value={overrides.existing_emi} onChange={set('existing_emi')} />
          </div>
          <div className="form-group">
            <label>Demo Credit Score</label>
            <input type="number" min={300} max={900} value={overrides.credit_score} onChange={set('credit_score')} />
          </div>
        </div>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? 'Simulating…' : 'Run Simulation'}
        </button>
      </form>

      {result?.status === 'completed' && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }} className="whatif-grid">
            <div className="card">
              <h3>CURRENT RESULT</h3>
              <p style={{ fontSize: '1.25rem', marginTop: '0.5rem' }}>
                {decisionEmoji(result.current_result.decision)}
              </p>
              <p>Risk: {result.current_result.risk_level}</p>
            </div>
            <div className="card">
              <h3>AFTER CHANGE</h3>
              <p style={{ fontSize: '1.25rem', marginTop: '0.5rem' }}>
                {decisionEmoji(result.after_change.decision)}
              </p>
              <p>Risk: {result.after_change.risk_level}</p>
            </div>
          </div>

          {result.comparison && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h3>What Changed</h3>
              {(result.comparison.parameter_changes || []).map((c, i) => (
                <p key={i}>{c}</p>
              ))}
              <p style={{ marginTop: '0.75rem' }}>
                <strong>Reason:</strong> {result.comparison.reason}
              </p>
              {result.comparison.newly_fired_rules?.length > 0 && (
                <p>
                  Newly fired: {result.comparison.newly_fired_rules.join(', ')}
                </p>
              )}
              {result.comparison.no_longer_fired_rules?.length > 0 && (
                <p>
                  No longer fired: {result.comparison.no_longer_fired_rules.join(', ')}
                </p>
              )}
            </div>
          )}

          <DecisionPanel assessment={result.after_change} />
        </>
      )}
      <style>{`@media (max-width:800px){ .whatif-grid{ grid-template-columns:1fr !important; } }`}</style>
    </div>
  )
}
