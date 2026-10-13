import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { authService } from '../services'
import { getErrorMessage } from '../utils/helpers'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
  })
  const [busy, setBusy] = useState(false)

  const save = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      await authService.updateProfile(form)
      await refreshUser()
      toast.success('Profile updated')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Profile</h1>
        <p>Manage your account details</p>
      </div>
      <form className="card" onSubmit={save} style={{ maxWidth: 480 }}>
        <div className="form-group">
          <label>Email</label>
          <input value={user?.email || ''} disabled />
          <p className="form-hint">Email cannot be changed</p>
        </div>
        <div className="form-group">
          <label>Role</label>
          <input value={user?.role || ''} disabled style={{ textTransform: 'capitalize' }} />
        </div>
        <div className="form-group">
          <label>Full Name</label>
          <input
            required
            value={form.full_name}
            onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
          />
        </div>
        <div className="form-group">
          <label>Phone</label>
          <input
            required
            value={form.phone}
            onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
