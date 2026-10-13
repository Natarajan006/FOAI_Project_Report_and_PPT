import { useEffect, useState } from 'react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { aiService } from '../services'
import { formatINR, getErrorMessage } from '../utils/helpers'
import toast from 'react-hot-toast'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function EMICalculator() {
  const [form, setForm] = useState({
    loan_amount: 500000,
    interest_rate: 10,
    tenure_months: 60,
  })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const calculate = async (e) => {
    e?.preventDefault()
    setBusy(true)
    try {
      const res = await aiService.emi({
        loan_amount: Number(form.loan_amount),
        interest_rate: Number(form.interest_rate),
        tenure_months: Number(form.tenure_months),
      })
      setResult(res.data)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    calculate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const chartData = result
    ? {
        labels: ['Principal', 'Total Interest'],
        datasets: [
          {
            data: [result.loan_amount, result.total_interest],
            backgroundColor: ['#1a56db', '#94a3b8'],
            borderWidth: 0,
          },
        ],
      }
    : null

  return (
    <div>
      <div className="page-header">
        <h1>EMI Calculator</h1>
        <p>Estimate monthly installments — demo rates only</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }} className="emi-grid">
        <form className="card" onSubmit={calculate}>
          <div className="form-group">
            <label>Loan Amount (₹)</label>
            <input type="number" min={1} value={form.loan_amount} onChange={set('loan_amount')} required />
          </div>
          <div className="form-group">
            <label>Interest Rate (% p.a.)</label>
            <input type="number" min={0.1} max={50} step={0.1} value={form.interest_rate} onChange={set('interest_rate')} required />
          </div>
          <div className="form-group">
            <label>Tenure (months)</label>
            <input type="number" min={1} max={480} value={form.tenure_months} onChange={set('tenure_months')} required />
          </div>
          <button type="submit" className="btn btn-primary" disabled={busy}>
            {busy ? 'Calculating…' : 'Calculate EMI'}
          </button>
        </form>

        <div className="card">
          {result ? (
            <>
              <div className="stats-grid" style={{ gridTemplateColumns: '1fr', marginBottom: '1rem' }}>
                <div>
                  <div className="stat-label">Monthly EMI</div>
                  <div className="stat-value">{formatINR(result.emi)}</div>
                </div>
                <div>
                  <div className="stat-label">Total Interest</div>
                  <div className="stat-value" style={{ fontSize: '1.35rem' }}>
                    {formatINR(result.total_interest)}
                  </div>
                </div>
                <div>
                  <div className="stat-label">Total Repayment</div>
                  <div className="stat-value" style={{ fontSize: '1.35rem' }}>
                    {formatINR(result.total_repayment)}
                  </div>
                </div>
              </div>
              {chartData && (
                <div style={{ maxWidth: 260, margin: '0 auto' }}>
                  <Doughnut data={chartData} options={{ plugins: { legend: { position: 'bottom' } } }} />
                </div>
              )}
            </>
          ) : (
            <div className="loading-state">
              <div className="spinner" />
            </div>
          )}
        </div>
      </div>
      <style>{`
        @media (max-width: 800px) {
          .emi-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
