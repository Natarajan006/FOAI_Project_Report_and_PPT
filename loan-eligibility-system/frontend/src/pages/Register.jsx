import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../utils/helpers'
import toast from 'react-hot-toast'
import './Auth.css'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
  })
  const [busy, setBusy] = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const onSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    setBusy(true)
    try {
      await register(form)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-brand">
          LoanAI
        </Link>
        <h1>Register</h1>
        <p className="auth-sub">Create your account to check loan eligibility</p>
        <form onSubmit={onSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input required minLength={2} value={form.full_name} onChange={set('full_name')} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" required value={form.email} onChange={set('email')} />
          </div>
          <div className="form-group">
            <label>Phone Number</label>
            <input required minLength={10} value={form.phone} onChange={set('phone')} placeholder="10–15 digits" />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input type="password" required minLength={8} value={form.password} onChange={set('password')} />
              <p className="form-hint">8+ chars, upper, lower, digit</p>
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" required value={form.confirm_password} onChange={set('confirm_password')} />
            </div>
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={busy}>
            {busy ? 'Creating account…' : 'Register'}
          </button>
        </form>
        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
