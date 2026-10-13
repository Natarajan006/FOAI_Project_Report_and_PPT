import { useEffect, useState } from 'react'
import { adminService } from '../../services'
import Modal, { ConfirmModal } from '../../components/Modal'
import { getErrorMessage } from '../../utils/helpers'
import toast from 'react-hot-toast'

const emptyRule = {
  rule_id: '',
  name: '',
  conditions: [{ field: '', operator: '>=', value: '' }],
  conclusion: '',
  priority: 1,
  explanation: '',
  enabled: true,
  category: 'general',
}

export default function AdminRules() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyRule)
  const [isNew, setIsNew] = useState(false)
  const [deleteId, setDeleteId] = useState(null)

  const load = () => {
    setLoading(true)
    adminService
      .rules()
      .then((res) => setRules(res.data))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const openNew = () => {
    setIsNew(true)
    setForm({ ...emptyRule, conditions: [{ field: '', operator: '>=', value: '' }] })
    setEditing({})
  }

  const openEdit = (rule) => {
    setIsNew(false)
    setForm({
      rule_id: rule.rule_id,
      name: rule.name,
      conditions: rule.conditions.map((c) => ({
        ...c,
        value: Array.isArray(c.value) ? c.value.join(',') : String(c.value),
      })),
      conclusion: rule.conclusion,
      priority: rule.priority,
      explanation: rule.explanation,
      enabled: rule.enabled,
      category: rule.category || 'general',
    })
    setEditing(rule)
  }

  const parseConditions = () =>
    form.conditions.map((c) => {
      let value = c.value
      if (c.operator === 'in' || c.operator === 'not_in') {
        value = String(c.value)
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean)
      } else if (value === 'true') value = true
      else if (value === 'false') value = false
      else if (!Number.isNaN(Number(value)) && value !== '' && !String(value).startsWith('__')) {
        value = Number(value)
      }
      return { field: c.field, operator: c.operator, value }
    })

  const save = async () => {
    try {
      const payload = {
        ...form,
        priority: Number(form.priority),
        conditions: parseConditions(),
      }
      if (isNew) {
        await adminService.createRule(payload)
        toast.success('Rule created')
      } else {
        const { rule_id, ...updates } = payload
        await adminService.updateRule(editing.id, updates)
        toast.success('Rule updated')
      }
      setEditing(null)
      load()
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  const toggle = async (rule) => {
    try {
      await adminService.updateRule(rule.id, { enabled: !rule.enabled })
      toast.success(rule.enabled ? 'Rule disabled' : 'Rule enabled')
      load()
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  const confirmDelete = async () => {
    try {
      await adminService.deleteRule(deleteId)
      toast.success('Rule deleted')
      setDeleteId(null)
      load()
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>Rule Management</h1>
          <p>Knowledge base for Forward Chaining — demo thresholds only</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={openNew}>
          Add Rule
        </button>
      </div>

      <div className="card table-wrap">
        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Conclusion</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((r) => (
                <tr key={r.id}>
                  <td>
                    <strong>{r.rule_id}</strong>
                  </td>
                  <td>{r.name}</td>
                  <td>
                    <code style={{ fontSize: '0.8rem' }}>{r.conclusion}</code>
                  </td>
                  <td>{r.priority}</td>
                  <td>
                    <span className={r.enabled ? 'badge badge-eligible' : 'badge badge-rejected'}>
                      {r.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => openEdit(r)}>
                      Edit
                    </button>{' '}
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => toggle(r)}>
                      {r.enabled ? 'Disable' : 'Enable'}
                    </button>{' '}
                    <button type="button" className="btn btn-danger btn-sm" onClick={() => setDeleteId(r.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal
        open={!!editing}
        title={isNew ? 'Add Rule' : `Edit ${form.rule_id}`}
        onClose={() => setEditing(null)}
      >
        <div className="form-group">
          <label>Rule ID</label>
          <input
            value={form.rule_id}
            disabled={!isNew}
            onChange={(e) => setForm((f) => ({ ...f, rule_id: e.target.value }))}
            placeholder="R033"
          />
        </div>
        <div className="form-group">
          <label>Name</label>
          <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Conclusion</label>
            <input value={form.conclusion} onChange={(e) => setForm((f) => ({ ...f, conclusion: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>Priority</label>
            <input
              type="number"
              min={1}
              value={form.priority}
              onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
            />
          </div>
        </div>
        <div className="form-group">
          <label>Explanation</label>
          <textarea
            rows={2}
            value={form.explanation}
            onChange={(e) => setForm((f) => ({ ...f, explanation: e.target.value }))}
          />
        </div>
        <h4 style={{ marginBottom: '0.5rem' }}>Conditions</h4>
        {form.conditions.map((c, i) => (
          <div key={i} className="form-row" style={{ marginBottom: '0.5rem' }}>
            <input
              placeholder="field"
              value={c.field}
              onChange={(e) => {
                const conditions = [...form.conditions]
                conditions[i] = { ...c, field: e.target.value }
                setForm((f) => ({ ...f, conditions }))
              }}
            />
            <select
              value={c.operator}
              onChange={(e) => {
                const conditions = [...form.conditions]
                conditions[i] = { ...c, operator: e.target.value }
                setForm((f) => ({ ...f, conditions }))
              }}
            >
              {['>=', '<=', '>', '<', '==', '!=', 'in', 'not_in'].map((op) => (
                <option key={op}>{op}</option>
              ))}
            </select>
            <input
              placeholder="value"
              value={c.value}
              onChange={(e) => {
                const conditions = [...form.conditions]
                conditions[i] = { ...c, value: e.target.value }
                setForm((f) => ({ ...f, conditions }))
              }}
            />
          </div>
        ))}
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() =>
            setForm((f) => ({
              ...f,
              conditions: [...f.conditions, { field: '', operator: '>=', value: '' }],
            }))
          }
        >
          Add Condition
        </button>
        <div style={{ marginTop: '1.25rem' }}>
          <button type="button" className="btn btn-primary" onClick={save}>
            Save Rule
          </button>
        </div>
      </Modal>

      <ConfirmModal
        open={!!deleteId}
        title="Delete Rule"
        message="Are you sure you want to delete this rule? This cannot be undone."
        onClose={() => setDeleteId(null)}
        onConfirm={confirmDelete}
      />
    </div>
  )
}
