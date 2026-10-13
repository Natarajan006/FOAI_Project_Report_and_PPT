# AI-Based Loan Eligibility Assessment System using Forward Chaining Algorithm

College-level **Foundation of AI** project combining:

- **Agentic AI workflow** (orchestration, validation, explanation)
- **Rule-based expert system** (knowledge base of modular rules)
- **Forward Chaining** (deterministic eligibility decisions)
- **Explainable AI** (fired rules, reasons, risk factors)

> **Important:** Eligibility is decided **only** by the Forward Chaining engine. The agent does **not** override decisions. Demo thresholds are **not** real bank underwriting criteria.

---

## 1. Project Overview

Users register, apply for loans, and receive an explainable eligibility result (`ELIGIBLE` / `NOT_ELIGIBLE` / `MANUAL_REVIEW`). Admins manage applications, review flagged cases, and edit knowledge-base rules.

---

## 2. Features

- JWT auth with **USER** and **ADMIN** roles (backend-enforced RBAC)
- Multi-step loan application form
- Demo Credit Score (300–900) — no bureau scraping
- Forward Chaining inference with 30+ sample rules
- Agentic assessment workflow + missing-info handling
- EMI calculator with chart
- What-If simulator (before/after + rule diffs)
- Loan amount recommendation (demo)
- Explainable AI panel + PDF reports
- Rule-based risk analysis (LOW / MEDIUM / HIGH)
- Assessment history
- Admin analytics, application review, rule CRUD

---

## 3. Architecture

```
Frontend (React)  --JWT-->  FastAPI Backend  -->  MongoDB
                                |
                    Agentic Workflow Agent
                                |
                    Fact Generator (EMI, DTI)
                                |
                    Knowledge Base (rules)
                                |
                    Forward Chaining Engine  ← authoritative decision
                                |
                    Explanation + Risk Analysis
```

---

## 4. Technology Stack

| Layer | Tech |
|-------|------|
| Frontend | React.js, React Router, Axios, Chart.js |
| Backend | Python, FastAPI, Pydantic, JWT, bcrypt |
| Database | MongoDB (Motor) |
| AI | Custom Forward Chaining + Agentic pipeline |

---

## 5. Folder Structure

```
loan-eligibility-system/
├── frontend/          # React SPA
├── backend/           # FastAPI + AI engine
├── docker-compose.yml
└── README.md
```

---

## 6. Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB 6+ (local or Docker)

---

## 7. MongoDB Setup

**Option A — Docker**

```bash
docker run -d --name loanai-mongo -p 27017:27017 mongo:7
```

**Option B — Local MongoDB**

Install MongoDB Community and ensure it listens on `mongodb://localhost:27017`.

---

## 8. Environment Variables

Copy examples and edit:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Key variables:

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `JWT_SECRET` | Long random secret for JWT signing |
| `FRONTEND_URL` | CORS allowed origin |
| `VITE_API_URL` | Frontend API base URL |

**Never commit real secrets.**

---

## 9. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Seed demo data:

```bash
python scripts/seed.py
```

Run API:

```bash
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

---

## 10. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## 11. Running the Application

1. Start MongoDB  
2. Seed backend (`python scripts/seed.py`)  
3. Start backend (`uvicorn app.main:app --reload --port 8000`)  
4. Start frontend (`npm run dev`)  

**Docker Compose (full stack):**

```bash
docker-compose up --build
```

After first start with Docker, seed via:

```bash
docker exec -it loanai-backend python scripts/seed.py
```

---

## 12. Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@loanai.demo` | `Admin@12345` |
| User | `user1@loanai.demo` | `User@12345` |
| User | `user2@loanai.demo` | `User@12345` |
| User | `user3@loanai.demo` | `User@12345` |

**Change these before any real deployment.**

---

## 13. Forward Chaining Explanation

1. Load applicant **facts** into working memory (including EMI & DTI).  
2. Load **rules** from the knowledge base (sorted by priority).  
3. Evaluate each rule’s conditions against facts.  
4. **Fire** satisfied rules → assert conclusions as derived facts.  
5. Repeat until no new facts (quiescence).  
6. Map decision facts (`final_eligible`, `final_not_eligible`, `final_manual_review`) to the outcome.  
7. Record every fired rule for explainability.

Rules are modular JSON-like objects — not one giant `if/else`.

---

## 14. Agentic AI Explanation

The agent:

1. Checks required information  
2. Asks for missing fields (does not assess if incomplete)  
3. Validates inputs  
4. Calculates EMI / DTI / affordability  
5. Invokes Forward Chaining  
6. Builds explanation, risk factors, and suggestions  
7. Stores the assessment  

The agent **never** overrides the FC decision.

---

## 15. Database Schema

| Collection | Purpose |
|------------|---------|
| `users` | Accounts (hashed passwords, roles) |
| `loan_applications` | Submitted applications |
| `assessments` | FC results, rules, explanations |
| `rules` | Knowledge base |
| `audit_logs` | Security/audit trail |

Relationships: User → Loan Applications → Assessments → Triggered Rules.

---

## 16. API Documentation

Interactive OpenAPI docs: `/docs`

Key endpoints:

**Auth:** `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`  
**Loans:** `POST /api/loans`, `GET /api/loans`, `GET /api/loans/{id}`  
**Assessment:** `POST /api/assessment/evaluate`, `GET /api/assessment/{id}`, `GET /api/assessment/{id}/report`  
**AI:** `POST /api/ai/advisor`, `POST /api/ai/what-if`, `POST /api/ai/emi/public`  
**Admin:** `/api/admin/users`, `/api/admin/applications`, `/api/admin/rules` (CRUD)

Non-admin calls to admin APIs return **403 Forbidden**.

---

## 17. Testing Instructions

```bash
cd backend
pytest tests/ -v
```

Covers:

- Password hashing & JWT  
- Forward Chaining (eligible / not eligible / manual review / missing facts)  
- EMI & DTI calculations  
- API validation & unauthorized access  

---

## 18. Known Limitations

- Demo rules/thresholds — not real underwriting  
- Demo credit score is user-entered  
- Advisor uses rule/FAQ responses (no external LLM required)  
- JWT logout is client-side token discard (stateless JWT)  
- Sample data for viva demos only  

---

## 19. Future Enhancements

- Authorized credit-bureau API integration  
- Optional LangGraph / LLM-powered advisor (still calling FC for decisions)  
- Email notifications for manual review  
- Refresh-token rotation & token blacklist  
- Production hardening (rate limits, HTTPS, secrets manager)

---

## Viva Demo Flow

1. Landing page → Register/Login  
2. Apply for loan with good profile → **ELIGIBLE** + rules fired  
3. Apply with poor credit / high DTI → **NOT ELIGIBLE**  
4. Borderline credit (650) → **MANUAL REVIEW**  
5. What-If: reduce loan amount → decision flips  
6. Admin: charts, review application, toggle a rule  

---

## License

Educational / academic use for Foundation of AI coursework.
