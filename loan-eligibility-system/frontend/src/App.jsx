import { Navigate, Route, Routes } from 'react-router-dom'
import { GuestRoute, ProtectedRoute } from './components/ProtectedRoute'
import DashboardLayout from './layouts/DashboardLayout'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ApplyLoan from './pages/ApplyLoan'
import Advisor from './pages/Advisor'
import AssessmentPage from './pages/AssessmentPage'
import EMICalculator from './pages/EMICalculator'
import WhatIf from './pages/WhatIf'
import History from './pages/History'
import Reports from './pages/Reports'
import Profile from './pages/Profile'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminApplications from './pages/admin/AdminApplications'
import AdminApprovals from './pages/admin/AdminApprovals'
import AdminContacts from './pages/admin/AdminContacts'
import AdminRules from './pages/admin/AdminRules'
import AdminUsers from './pages/admin/AdminUsers'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />

      <Route element={<GuestRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Applicant portal — admins are redirected to /admin by layout */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/apply" element={<ApplyLoan />} />
          <Route path="/advisor" element={<Advisor />} />
          <Route path="/assessment" element={<AssessmentPage />} />
          <Route path="/emi" element={<EMICalculator />} />
          <Route path="/what-if" element={<WhatIf />} />
          <Route path="/history" element={<History />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Route>

      {/* Admin console — approve, contact, manage */}
      <Route element={<ProtectedRoute adminOnly />}>
        <Route element={<DashboardLayout admin />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/applications" element={<AdminApplications />} />
          <Route path="/admin/approvals" element={<AdminApprovals />} />
          <Route path="/admin/contacts" element={<AdminContacts />} />
          <Route path="/admin/rules" element={<AdminRules />} />
          <Route path="/admin/users" element={<AdminUsers />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
