import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loanService } from '../services'
import DecisionPanel from '../components/DecisionPanel'
import { getErrorMessage, formatINR } from '../utils/helpers'
import toast from 'react-hot-toast'

const STEPS = ['Personal', 'Financial', 'Loan', 'Review']

const initial = {
  full_name: '',
  age: '',
  gender: '',
  employment_type: 'Salaried',
  monthly_income: '',
  monthly_expenses: '',
  existing_emi: '',
  credit_score: '',
  employment_duration: '',
  repayment_history: 'Good',
  loan_type: 'Personal Loan',
  requested_amount: '',
  tenure_months: '',
  purpose: '',
  interest_rate: '',
}

export default function ApplyLoan() {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(initial)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const validateStep = () => {
    if (step === 0) {
      if (!form.full_name || !form.age || !form.employment_type) {
        toast.error('Please fill all required personal fields')
        return false
      }
      const age = Number(form.age)
      if (age < 18 || age > 80) {
        toast.error('Age must be between 18 and 80')
        return false
      }
    }
    if (step === 1) {
      const nums = ['monthly_income', 'monthly_expenses', 'existing_emi', 'credit_score', 'employment_duration']
      for (const k of nums) {
        if (form[k] === '' || Number(form[k]) < 0) {
          toast.error('Please enter valid non-negative financial values')
          return false
        }
      }
      if (Number(form.monthly_income) <= 0) {
        toast.error('Monthly income must be positive')
        return false
      }
      const cs = Number(form.credit_score)
      if (cs < 300 || cs > 900) {
        toast.error('Demo Credit Score must be between 300 and 900')
        return false
      }
    }
    if (step === 2) {
      if (!form.loan_type || !form.requested_amount || !form.tenure_months || !form.purpose) {
        toast.error('Please complete loan information')
        return false
      }
      if (Number(form.requested_amount) <= 0) {
        toast.error('Loan amount must be positive')
        return false
      }
      const tenure = Number(form.tenure_months)
      if (tenure < 6 || tenure > 360) {
        toast.error('Tenure must be between 6 and 360 months')
        return false
      }
    }
    return true
  }

  const next = () => {
    if (!validateStep()) return
    setStep((s) => Math.min(s + 1, STEPS.length - 1))
  }
  const back = () => setStep((s) => Math.max(s - 1, 0))

  const submit = async () => {
    if (!validateStep()) return
    setBusy(true)
    try {
      const payload = {
        ...form,
        age: Number(form.age),
        monthly_income: Number(form.monthly_income),
        monthly_expenses: Number(form.monthly_expenses),
        existing_emi: Number(form.existing_emi),
        credit_score: Number(form.credit_score),
        employment_duration: Number(form.employment_duration),
        requested_amount: Number(form.requested_amount),
        tenure_months: Number(form.tenure_months),
        interest_rate: form.interest_rate ? Number(form.interest_rate) : null,
        gender: form.gender || null,
      }
      const res = await loanService.create(payload)
      setResult(res.data.assessment)
      toast.success('Application submitted and assessed')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  if (result) {
    return (
      <div>
        <div className="page-header">
          <h1>Assessment Result</h1>
          <p>Forward Chaining decision with explainable AI</p>
        </div>
        <DecisionPanel assessment={result} />
        <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/history')}>
            View History
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setResult(null)
              setForm(initial)
              setStep(0)
            }}
          >
            New Application
          </button>
          {result.id && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate(`/reports?id=${result.id}`)}
            >
              Download Report
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Apply for Loan</h1>
        <p>Multi-step application — assessed by Agentic AI + Forward Chaining</p>
      </div>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {STEPS.map((s, i) => (
            <span
              key={s}
              className="badge"
              style={{
                background: i === step ? 'var(--blue-soft)' : 'var(--off-white)',
                color: i === step ? 'var(--blue)' : 'var(--slate)',
              }}
            >
              {i + 1}. {s}
            </span>
          ))}
        </div>
      </div>

      <div className="card">
        {step === 0 && (
          <>
            <h3 style={{ marginBottom: '1rem' }}>Personal Information</h3>
            <div className="form-group">
              <label>Full Name *</label>
              <input required value={form.full_name} onChange={set('full_name')} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Age *</label>
                <input type="number" min={18} max={80} value={form.age} onChange={set('age')} />
              </div>
              <div className="form-group">
                <label>Gender (optional)</label>
                <select value={form.gender} onChange={set('gender')}>
                  <option value="">Prefer not to say</option>
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Employment Type *</label>
              <select value={form.employment_type} onChange={set('employment_type')}>
                <option>Salaried</option>
                <option>Self-Employed</option>
                <option>Business</option>
                <option>Unemployed</option>
              </select>
            </div>
          </>
        )}

        {step === 1 && (
          <>
            <h3 style={{ marginBottom: '1rem' }}>Financial Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Monthly Income (₹) *</label>
                <input type="number" min={0} value={form.monthly_income} onChange={set('monthly_income')} />
              </div>
              <div className="form-group">
                <label>Monthly Expenses (₹) *</label>
                <input type="number" min={0} value={form.monthly_expenses} onChange={set('monthly_expenses')} />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Existing EMI (₹) *</label>
                <input type="number" min={0} value={form.existing_emi} onChange={set('existing_emi')} />
              </div>
              <div className="form-group">
                <label>Demo Credit Score * (300–900)</label>
                <input type="number" min={300} max={900} value={form.credit_score} onChange={set('credit_score')} />
                <p className="form-hint">
                  Demo Credit Score — manually entered for this college demo. Not from a credit bureau.
                </p>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Employment Duration (months) *</label>
                <input type="number" min={0} value={form.employment_duration} onChange={set('employment_duration')} />
              </div>
              <div className="form-group">
                <label>Previous Loan Repayment History *</label>
                <select value={form.repayment_history} onChange={set('repayment_history')}>
                  <option>Good</option>
                  <option>Average</option>
                  <option>Poor</option>
                  <option>None</option>
                </select>
              </div>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h3 style={{ marginBottom: '1rem' }}>Loan Information</h3>
            <div className="form-group">
              <label>Loan Type *</label>
              <select value={form.loan_type} onChange={set('loan_type')}>
                <option>Personal Loan</option>
                <option>Education Loan</option>
                <option>Home Loan</option>
                <option>Vehicle Loan</option>
                <option>Business Loan</option>
              </select>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Requested Loan Amount (₹) *</label>
                <input type="number" min={1} value={form.requested_amount} onChange={set('requested_amount')} />
              </div>
              <div className="form-group">
                <label>Loan Tenure (months) *</label>
                <input type="number" min={6} max={360} value={form.tenure_months} onChange={set('tenure_months')} />
              </div>
            </div>
            <div className="form-group">
              <label>Interest Rate % (optional — demo default by loan type if blank)</label>
              <input type="number" min={1} max={30} step={0.1} value={form.interest_rate} onChange={set('interest_rate')} />
            </div>
            <div className="form-group">
              <label>Purpose of Loan *</label>
              <textarea rows={3} value={form.purpose} onChange={set('purpose')} />
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h3 style={{ marginBottom: '1rem' }}>Review &amp; Submit</h3>
            <p className="form-hint" style={{ marginBottom: '1rem' }}>
              On submit, the AI agent validates your data, calculates EMI &amp; DTI, and runs
              Forward Chaining. Sample demo rules — not real bank underwriting.
            </p>
            <div className="table-wrap">
              <table className="data-table">
                <tbody>
                  {[
                    ['Name', form.full_name],
                    ['Age', form.age],
                    ['Employment', form.employment_type],
                    ['Income', formatINR(form.monthly_income)],
                    ['Existing EMI', formatINR(form.existing_emi)],
                    ['Demo Credit Score', form.credit_score],
                    ['Loan Type', form.loan_type],
                    ['Amount', formatINR(form.requested_amount)],
                    ['Tenure', `${form.tenure_months} months`],
                    ['Purpose', form.purpose],
                  ].map(([k, v]) => (
                    <tr key={k}>
                      <td>
                        <strong>{k}</strong>
                      </td>
                      <td>{v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
          {step > 0 && (
            <button type="button" className="btn btn-secondary" onClick={back}>
              Back
            </button>
          )}
          {step < STEPS.length - 1 ? (
            <button type="button" className="btn btn-primary" onClick={next}>
              Next
            </button>
          ) : (
            <button type="button" className="btn btn-primary" onClick={submit} disabled={busy}>
              {busy ? 'Assessing…' : 'Submit & Assess'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
