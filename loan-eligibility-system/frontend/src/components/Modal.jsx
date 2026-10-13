import { useState } from 'react'

export default function Modal({ open, title, onClose, children }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog">
        <div className="modal-header">
          <h3>{title}</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function ConfirmModal({ open, title, message, onConfirm, onClose }) {
  const [busy, setBusy] = useState(false)
  if (!open) return null
  return (
    <Modal open={open} title={title} onClose={onClose}>
      <p>{message}</p>
      <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.25rem' }}>
        <button
          type="button"
          className="btn btn-danger"
          disabled={busy}
          onClick={async () => {
            setBusy(true)
            await onConfirm()
            setBusy(false)
          }}
        >
          Confirm
        </button>
        <button type="button" className="btn btn-secondary" onClick={onClose}>
          Cancel
        </button>
      </div>
    </Modal>
  )
}
