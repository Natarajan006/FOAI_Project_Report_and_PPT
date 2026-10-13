import { Link } from 'react-router-dom'
import './Landing.css'

export default function Landing() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="container nav-inner">
          <Link to="/" className="brand">
            LoanAI
          </Link>
          <nav>
            <a href="#how">How It Works</a>
            <a href="#features">Features</a>
            <Link to="/login">Login</Link>
            <Link to="/register" className="btn btn-primary btn-sm">
              Register
            </Link>
          </nav>
        </div>
      </header>

      <section className="hero">
        <div className="hero-bg" aria-hidden="true" />
        <div className="container hero-content">
          <p className="hero-brand">LoanAI</p>
          <h1>AI-Based Loan Eligibility Assessment System</h1>
          <p className="hero-sub">
            Smart, explainable and rule-based loan eligibility assessment using Forward
            Chaining and Agentic AI.
          </p>
          <div className="hero-cta">
            <Link to="/register" className="btn btn-primary">
              Check Eligibility
            </Link>
            <Link to="/login" className="btn btn-ghost">
              Login
            </Link>
            <Link to="/register" className="btn btn-ghost">
              Register
            </Link>
          </div>
        </div>
      </section>

      <section id="how" className="section">
        <div className="container">
          <h2>How It Works</h2>
          <p className="section-lead">
            A clear pipeline from application to explainable decision.
          </p>
          <div className="steps">
            <div>
              <span>01</span>
              <h3>Apply</h3>
              <p>Submit personal, financial, and loan details in a guided multi-step form.</p>
            </div>
            <div>
              <span>02</span>
              <h3>Agent Validates</h3>
              <p>The Agentic AI checks completeness, asks for missing info, and calculates EMI &amp; DTI.</p>
            </div>
            <div>
              <span>03</span>
              <h3>Forward Chaining</h3>
              <p>Rules fire against your facts until a deterministic eligibility decision is reached.</p>
            </div>
            <div>
              <span>04</span>
              <h3>Explain</h3>
              <p>See every rule that fired, risk factors, and human-readable reasons.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="section alt">
        <div className="container">
          <h2>AI Features</h2>
          <p className="section-lead">
            Agentic workflow orchestration with a rule-based expert system at the core.
          </p>
          <div className="feature-grid">
            <article>
              <h3>Agentic AI Workflow</h3>
              <p>
                Collects, validates, and calculates — then invokes Forward Chaining. The agent
                never overrides the eligibility decision.
              </p>
            </article>
            <article>
              <h3>What-If Simulator</h3>
              <p>
                Change income, tenure, or loan amount and see exactly which rules flip the result.
              </p>
            </article>
            <article>
              <h3>AI Loan Advisor</h3>
              <p>Ask about DTI, EMI, credit score, and the assessment process in plain language.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container two-col">
          <div>
            <h2>Explainable AI</h2>
            <p className="section-lead">Never just “Eligible” — always show why.</p>
            <ul className="check-list">
              <li>Human-readable reasons for every decision</li>
              <li>Complete list of fired rules (R001, R003…)</li>
              <li>Risk factors and improvement suggestions</li>
              <li>Downloadable PDF assessment reports</li>
            </ul>
          </div>
          <div className="explain-card">
            <p className="label">LOAN DECISION</p>
            <p className="result">🟢 ELIGIBLE</p>
            <p>✓ Age requirement satisfied</p>
            <p>✓ Income requirement satisfied</p>
            <p>✓ Credit requirement satisfied</p>
            <p>✓ Debt ratio acceptable</p>
            <div className="mini-rules">
              <span>R001 ✓</span>
              <span>R003 ✓</span>
              <span>R004 ✓</span>
              <span>R008 ✓</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt">
        <div className="container">
          <h2>Forward Chaining</h2>
          <p className="section-lead">
            Classic data-driven inference: facts in, rules fire, derived facts accumulate,
            decision emerges. No machine learning for eligibility.
          </p>
          <div className="fc-flow">
            <span>Facts</span>
            <span>→</span>
            <span>Rules</span>
            <span>→</span>
            <span>Derived Facts</span>
            <span>→</span>
            <span>Decision</span>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container feature-grid">
          <article>
            <h3>Security</h3>
            <p>
              JWT authentication, bcrypt password hashing, role-based access control, and
              backend-enforced admin authorization (403 Forbidden).
            </p>
          </article>
          <article>
            <h3>Benefits</h3>
            <p>
              Transparent demo underwriting logic, EMI &amp; DTI tools, history tracking, and
              admin rule management — built for viva-ready demonstration.
            </p>
          </article>
          <article>
            <h3>Demo Credit Score</h3>
            <p>
              Enter a demo credit score (300–900). Architecture allows future authorized
              bureau API integration — no scraping.
            </p>
          </article>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="container">
          <p>
            <strong>LoanAI</strong> — College Foundation of AI project. Sample rules only —
            not real bank underwriting.
          </p>
        </div>
      </footer>
    </div>
  )
}
