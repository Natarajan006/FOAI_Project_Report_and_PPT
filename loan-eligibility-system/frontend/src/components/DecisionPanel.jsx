import { decisionEmoji, decisionPanelClass, formatINR } from '../utils/helpers'

export default function DecisionPanel({ assessment }) {
  if (!assessment || !assessment.decision) {
    if (assessment?.status === 'missing_information') {
      return (
        <div className="decision-panel review">
          <h3 className="decision-title">Additional information required</h3>
          <ul className="reasons-list">
            {(assessment.missing_fields || []).map((f) => (
              <li key={f}>• {f}</li>
            ))}
          </ul>
          <p>{assessment.message}</p>
        </div>
      )
    }
    return null
  }

  const fs = assessment.financial_summary || {}
  const rec = assessment.loan_recommendation || fs.loan_recommendation

  return (
    <div className={decisionPanelClass(assessment.decision)}>
      <p style={{ fontSize: '0.8rem', fontWeight: 700, letterSpacing: '0.06em' }}>
        LOAN DECISION
      </p>
      <h3 className="decision-title">{decisionEmoji(assessment.decision)}</h3>

      {assessment.risk_level && (
        <p>
          <strong>Risk Level:</strong> {assessment.risk_level}
        </p>
      )}

      {fs.debt_to_income_ratio != null && (
        <p>
          <strong>DTI:</strong> {fs.debt_to_income_ratio}% &nbsp;|&nbsp;
          <strong>Est. EMI:</strong> {formatINR(fs.estimated_new_emi)} &nbsp;|&nbsp;
          <strong>Demo Credit Score:</strong> {fs.credit_score}
        </p>
      )}

      {assessment.reasons?.length > 0 && (
        <>
          <h4 style={{ marginTop: '1rem' }}>Reasons</h4>
          <ul className="reasons-list">
            {assessment.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </>
      )}

      {assessment.triggered_rules?.length > 0 && (
        <>
          <h4>Rules Fired</h4>
          <div className="rules-fired">
            {assessment.triggered_rules.map((r) => (
              <span className="rule-chip" key={r.rule_id + r.conclusion} title={r.explanation}>
                {r.rule_id} ✓
              </span>
            ))}
          </div>
        </>
      )}

      {assessment.explanation && (
        <>
          <h4 style={{ marginTop: '1rem' }}>AI Explanation</h4>
          <p style={{ fontSize: '0.95rem' }}>{assessment.explanation}</p>
        </>
      )}

      {assessment.risk_factors?.length > 0 && (
        <>
          <h4 style={{ marginTop: '1rem' }}>Risk Factors</h4>
          <ul className="reasons-list">
            {assessment.risk_factors.map((f, i) => (
              <li key={i}>• {f}</li>
            ))}
          </ul>
        </>
      )}

      {assessment.suggestions?.length > 0 && (
        <>
          <h4 style={{ marginTop: '1rem' }}>Suggestions</h4>
          <ul className="reasons-list">
            {assessment.suggestions.map((s, i) => (
              <li key={i}>• {s}</li>
            ))}
          </ul>
        </>
      )}

      {rec && (
        <>
          <h4 style={{ marginTop: '1rem' }}>Loan Amount Recommendation (Demo)</h4>
          <p>
            Recommended Range: {formatINR(rec.recommended_min)} – {formatINR(rec.recommended_max)}
          </p>
          <p>Estimated Maximum Affordable: {formatINR(rec.estimated_maximum_affordable)}</p>
          <p className="form-hint">{rec.disclaimer}</p>
        </>
      )}
    </div>
  )
}
