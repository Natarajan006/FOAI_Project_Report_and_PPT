import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { loanService } from '../services'
import {
  decisionBadgeClass,
  formatINR,
  formatDate,
  getErrorMessage,
  riskBadgeClass,
} from '../utils/helpers'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loanService
      .dashboardStats()
      .then((res) => setStats(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner" />
        <p>Loading dashboard…</p>
      </div>
    )
  }

  const latest = stats?.latest_assessment

  return (
    <div>
      <div className="page-header">
        <h1>Welcome, {user?.full_name}</h1>
        <p>Your loan eligibility overview</p>
      </div>

      <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-card">
          <div className="stat-label">Eligibility Status</div>
          <div className="stat-value" style={{ fontSize: '1.25rem' }}>
            {stats?.eligibility_status && stats.eligibility_status !== 'N/A' ? (
              <span className={decisionBadgeClass(stats.eligibility_status)}>
                {stats.eligibility_status}
              </span>
            ) : (
              'No assessment yet'
            )}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Loan Amount</div>
          <div className="stat-value">{formatINR(stats?.loan_amount)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Credit Score</div>
          <div className="stat-value">{stats?.credit_score ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Risk Level</div>
          <div className="stat-value" style={{ fontSize: '1.25rem' }}>
            {stats?.risk_level ? (
              <span className={riskBadgeClass(stats.risk_level)}>{stats.risk_level}</span>
            ) : (
              '—'
            )}
          </div>
        </div>
      </div>

      <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-card">
          <div className="stat-label">Total Applications</div>
          <div className="stat-value">{stats?.total_applications ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Eligible Applications</div>
          <div className="stat-value">{stats?.eligible_applications ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Reviews</div>
          <div className="stat-value">{stats?.pending_reviews ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Application Status</div>
          <div className="stat-value" style={{ fontSize: '1.1rem', textTransform: 'capitalize' }}>
            {stats?.application_status || 'N/A'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Admin Decision</div>
          <div className="stat-value" style={{ fontSize: '1.1rem', textTransform: 'capitalize' }}>
            {stats?.admin_decision ? stats.admin_decision.replace('_', ' ') : 'Awaiting admin'}
          </div>
        </div>
      </div>

      {stats?.admin_notes && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Message from Admin</h3>
          <p>{stats.admin_notes}</p>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: '0.75rem' }}>Latest Assessment</h3>
        {latest ? (
          <>
            <p>
              <span className={decisionBadgeClass(latest.decision)}>{latest.decision}</span>{' '}
              <span className={riskBadgeClass(latest.risk_level)}>{latest.risk_level}</span>
            </p>
            <p style={{ marginTop: '0.5rem', color: 'var(--slate)', fontSize: '0.9rem' }}>
              {formatDate(latest.timestamp)}
            </p>
            <p style={{ marginTop: '0.75rem' }}>{latest.explanation?.slice(0, 220)}…</p>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <Link to="/history" className="btn btn-primary btn-sm">
                View History
              </Link>
              <Link to="/apply" className="btn btn-secondary btn-sm">
                Apply for Loan
              </Link>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <p>No assessments yet. Start by applying for a loan.</p>
            <Link to="/apply" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Apply for Loan
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
