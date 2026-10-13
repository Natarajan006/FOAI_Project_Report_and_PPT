import './layouts.css'
import { Link, NavLink, Outlet, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useState } from 'react'

const userLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/apply', label: 'Apply for Loan' },
  { to: '/advisor', label: 'AI Loan Advisor' },
  { to: '/assessment', label: 'Eligibility Assessment' },
  { to: '/emi', label: 'EMI Calculator' },
  { to: '/what-if', label: 'What-If Simulator' },
  { to: '/history', label: 'Assessment History' },
  { to: '/reports', label: 'Reports' },
  { to: '/profile', label: 'Profile' },
]

const adminLinks = [
  { to: '/admin', label: 'Operations Dashboard' },
  { to: '/admin/applications', label: 'Loan Applications' },
  { to: '/admin/approvals', label: 'Approve / Reject' },
  { to: '/admin/contacts', label: 'Contact Applicants' },
  { to: '/admin/rules', label: 'Rule Management' },
  { to: '/admin/users', label: 'Registered Users' },
]

export default function DashboardLayout({ admin = false }) {
  const { user, logout, isAdmin } = useAuth()
  const [open, setOpen] = useState(false)

  // Keep roles on separate experiences
  if (admin && !isAdmin) {
    return <Navigate to="/dashboard" replace />
  }
  if (!admin && isAdmin) {
    return <Navigate to="/admin" replace />
  }

  const links = admin ? adminLinks : userLinks

  return (
    <div className={`dash-shell ${admin ? 'admin-shell' : 'user-shell'}`}>
      <aside className={`dash-sidebar ${admin ? 'admin-sidebar' : ''} ${open ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <Link to={admin ? '/admin' : '/dashboard'} onClick={() => setOpen(false)}>
            LoanAI
          </Link>
          <span>{admin ? 'Admin Console' : 'Applicant Portal'}</span>
        </div>
        <nav className="sidebar-nav">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/dashboard' || l.to === '/admin'}
              onClick={() => setOpen(false)}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <button type="button" className="sidebar-logout" onClick={logout}>
          Logout
        </button>
      </aside>

      <div className="dash-main">
        <header className={`dash-topbar ${admin ? 'admin-topbar' : ''}`}>
          <button
            type="button"
            className="menu-toggle"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <div className="topbar-role">
            {admin ? 'Loan Review & Approvals' : 'My Loan Workspace'}
          </div>
          <div className="topbar-user">
            <strong>{user?.full_name}</strong>
            <span>
              {user?.email} · {admin ? 'Administrator' : 'Applicant'}
            </span>
          </div>
        </header>
        <main className="dash-content">
          <Outlet />
        </main>
      </div>
      {open && <div className="sidebar-backdrop" onClick={() => setOpen(false)} />}
    </div>
  )
}
