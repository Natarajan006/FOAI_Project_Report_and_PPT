import { useState } from 'react'
import { aiService } from '../services'
import { getErrorMessage } from '../utils/helpers'
import toast from 'react-hot-toast'

export default function Advisor() {
  const [message, setMessage] = useState('')
  const [chat, setChat] = useState([
    {
      role: 'assistant',
      text: 'Hi! I am the AI Loan Advisor. I can explain eligibility, DTI, EMI, Forward Chaining, and more. I do not decide eligibility — the Forward Chaining engine does.',
    },
  ])
  const [busy, setBusy] = useState(false)

  const send = async (e) => {
    e.preventDefault()
    if (!message.trim()) return
    const userMsg = message.trim()
    setChat((c) => [...c, { role: 'user', text: userMsg }])
    setMessage('')
    setBusy(true)
    try {
      const res = await aiService.advisor(userMsg)
      setChat((c) => [...c, { role: 'assistant', text: res.data.reply }])
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const quick = (q) => {
    setMessage(q)
  }

  return (
    <div>
      <div className="page-header">
        <h1>AI Loan Advisor</h1>
        <p>Ask about the process — decisions stay with Forward Chaining</p>
      </div>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {['How does eligibility work?', 'What is DTI?', 'Explain Forward Chaining', 'How to improve chances?'].map(
            (q) => (
              <button key={q} type="button" className="btn btn-secondary btn-sm" onClick={() => quick(q)}>
                {q}
              </button>
            )
          )}
        </div>
      </div>

      <div className="card" style={{ minHeight: 360, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', maxHeight: 420 }}>
          {chat.map((m, i) => (
            <div
              key={i}
              style={{
                marginBottom: '0.85rem',
                padding: '0.75rem 1rem',
                borderRadius: 8,
                background: m.role === 'user' ? 'var(--blue-soft)' : 'var(--off-white)',
                marginLeft: m.role === 'user' ? '2rem' : 0,
                marginRight: m.role === 'assistant' ? '2rem' : 0,
                whiteSpace: 'pre-wrap',
              }}
            >
              <strong style={{ fontSize: '0.75rem', color: 'var(--slate)' }}>
                {m.role === 'user' ? 'You' : 'Advisor'}
              </strong>
              <p style={{ marginTop: 4 }}>{m.text}</p>
            </div>
          ))}
        </div>
        <form onSubmit={send} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            style={{ flex: 1, padding: '0.7rem', borderRadius: 8, border: '1.5px solid var(--border)' }}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question…"
            disabled={busy}
          />
          <button type="submit" className="btn btn-primary" disabled={busy}>
            {busy ? '…' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  )
}
