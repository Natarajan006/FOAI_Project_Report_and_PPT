import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Pie, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import { adminService } from '../../services'
import { formatDate, formatINR, getErrorMessage } from '../../utils/helpers'
import toast from 'react-hot-toast'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminService
      .dashboard()
      .then((res) => setStats(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading || !stats) {
    return (
      <div className="loading-state">
        <div className="spinner" />
        <p>Loading operations dashboard…</p>
      </div>
    )
  }

  const eligibilityData = {
    labels: Object.keys(stats.eligibility_distribution || {}),
    datasets: [
      {
        data: Object.values(stats.eligibility_distribution || {}),
        backgroundColor: ['#15803d', '#b91c1c', '#c2410c'],
      },
    ],
  }

  const monthlyData = {
    labels: Object.keys(stats.monthly_applications || {}),
    datasets: [
      {
        label: 'Applications',
        data: Object.values(stats.monthly_applications || {}),
        backgroundColor: '#92400e',
      },
    ],
  }

  return (
    <div>
      <div className="page-header">
        <h1>Admin Operations Dashboard</h1>
        <p>
          Review loan applications, approve or reject decisions, and contact applicants.
          This console is separate from the applicant portal.
        </p>
      </div>

      <div className="stats-grid" style={{ marginBottom: '1.25rem' }}>
        <div className="stat-card" style={{ borderColor: '#f59e0b' }}>
          <div className="stat-label">Pending Your Action</div>
          <div className="stat-value">{stats.pending_approval ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Manual Review Queue</div>
          <div className="stat-value">{stats.manual_review}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Admin Approved</div>
          <div className="stat-value" style={{ color: 'var(--eligible)' }}>
            {stats.admin_approved ?? 0}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Admin Rejected</div>
          <div className="stat-value" style={{ color: 'var(--rejected)' }}>
            {stats.admin_rejected ?? 0}
          </div>
        </div>
      </div>

      <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-card">
          <div className="stat-label">Total Applicants</div>
          <div className="stat-value">{stats.total_users}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Applications</div>
          <div className="stat-value">{stats.total_applications}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">AI Eligible</div>
          <div className="stat-value">{stats.eligible}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">AI Not Eligible</div>
          <div className="stat-value">{stats.not_eligible}</div>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1rem',
          marginBottom: '1.5rem',
        }}
        className="admin-actions"
      >
        <Link to="/admin/approvals" className="card" style={{ textDecoration: 'none' }}>
          <h3 style={{ color: 'var(--navy)' }}>Approve / Reject</h3>
          <p style={{ color: 'var(--slate)', marginTop: 6 }}>
            Take final decisions on pending loan applications.
          </p>
        </Link>
        <Link to="/admin/applications" className="card" style={{ textDecoration: 'none' }}>
          <h3 style={{ color: 'var(--navy)' }}>View Applications</h3>
          <p style={{ color: 'var(--slate)', marginTop: 6 }}>
            Search and open full AI reasoning for every application.
          </p>
        </Link>
        <Link to="/admin/contacts" className="card" style={{ textDecoration: 'none' }}>
          <h3 style={{ color: 'var(--navy)' }}>Contact Applicants</h3>
          <p style={{ color: 'var(--slate)', marginTop: 6 }}>
            Email, call, or message applicants about their loan status.
          </p>
        </Link>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3>Action Queue — Needs Review / Approval</h3>
          <Link to="/admin/approvals" className="btn btn-primary btn-sm">
            Open Approvals
          </Link>
        </div>
        {(stats.pending_queue || []).length === 0 ? (
          <div className="empty-state">No applications waiting for admin action.</div>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Applicant</th>
                  <th>Loan</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Contact</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {stats.pending_queue.map((r) => (
                  <tr key={r.id}>
                    <td>{r.full_name}</td>
                    <td>{r.loan_type}</td>
                    <td>{formatINR(r.requested_amount)}</td>
                    <td style={{ textTransform: 'capitalize' }}>{r.status?.replace('_', ' ')}</td>
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
                      </div>
                    </td>
                    <td>{formatDate(r.created_at)}</td>
                    <td>
                      <Link to={`/admin/approvals?id=${r.id}`} className="btn btn-primary btn-sm">
                        Decide
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: '1.25rem' }}
        className="admin-charts"
      >
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>AI Eligibility Distribution</h3>
          <div style={{ maxWidth: 280, margin: '0 auto' }}>
            <Pie data={eligibilityData} />
          </div>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Monthly Applications</h3>
          <Bar data={monthlyData} options={{ plugins: { legend: { display: false } } }} />
        </div>
      </div>
      <style>{`
        @media (max-width:900px){
          .admin-charts, .admin-actions { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
