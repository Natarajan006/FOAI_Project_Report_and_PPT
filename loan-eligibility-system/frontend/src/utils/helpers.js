/** Format currency in Indian Rupees */
export function formatINR(value) {
  if (value == null || Number.isNaN(Number(value))) return '₹0'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(Number(value))
}

export function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export function decisionBadgeClass(decision) {
  if (decision === 'ELIGIBLE' || decision === 'eligible') return 'badge badge-eligible'
  if (decision === 'MANUAL_REVIEW' || decision === 'manual_review') return 'badge badge-review'
  if (decision === 'NOT_ELIGIBLE' || decision === 'not_eligible') return 'badge badge-rejected'
  return 'badge'
}

export function riskBadgeClass(risk) {
  if (risk === 'LOW') return 'badge badge-low'
  if (risk === 'MEDIUM') return 'badge badge-medium'
  if (risk === 'HIGH') return 'badge badge-high'
  return 'badge'
}

export function decisionPanelClass(decision) {
  if (decision === 'ELIGIBLE') return 'decision-panel eligible'
  if (decision === 'MANUAL_REVIEW') return 'decision-panel review'
  return 'decision-panel rejected'
}

export function decisionEmoji(decision) {
  if (decision === 'ELIGIBLE') return '🟢 ELIGIBLE'
  if (decision === 'MANUAL_REVIEW') return '🟡 MANUAL REVIEW REQUIRED'
  if (decision === 'NOT_ELIGIBLE') return '🔴 NOT ELIGIBLE'
  return decision || '—'
}

export function getErrorMessage(err) {
  const detail = err?.response?.data?.detail
  if (Array.isArray(detail)) return detail.join('; ')
  if (typeof detail === 'string') return detail
  return err?.message || 'Something went wrong'
}
