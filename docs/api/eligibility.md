# Eligibility Module API Contract

## 1. Playbook-Defined Requirements

The following requirements are explicitly mandated by the **TribalSetu Team Development & Integration Playbook**:

### Core Architecture & Ownership
- **Owner:** The `Verification/Eligibility` role owns the rules engine, eligibility API, and explainable results.
- **Responsibilities:** "Rule evaluation + explainable result" (Playbook Section 13, Table 2).
- **Dependencies:** Evaluates criteria based on `Student, schemes, rules`.
- **User Journey Placement:** In the end-to-end user journey, Eligibility evaluation precedes Application creation:
  `Find scholarships ↓ Eligibility ↓ Create application` (Section 20, Rule 176).
- **Core Concept:** Boolean qualification flag `eligible` (Section 10 & 11).
- **Downstream Consumers:** JAGO chatbot invokes the Eligibility service to explain eligibility status and reasons to students (Section 21, Rule 179).

### Explicit Playbook Limitation
> **"The playbook does not define executable scholarship eligibility rules."**
> 
> No income limits, age limits, caste/ST requirements, percentage cutoffs, or scheme-specific criteria are defined in the project playbook.

---

## 2. Team-Approved Phase-1 Contract

The following decisions are **TEAM-APPROVED** for the minimal Phase-1 implementation, and must not be confused with playbook-defined requirements.

### Stateless Architecture
- **Stateless Evaluation:** Phase 1 implements a stateless evaluation service.
- **No Database Persistence:** No `eligibility` or `rules` tables, and no Alembic migrations are created. Results are computed dynamically on request.
- **No Invented Rules:** In the absence of official Government/MoTA scheme criteria, the system strictly avoids fabricating pseudo-rules (such as fake income or caste thresholds).
- **Isolated Mock Evaluator:** Phase 1 utilizes an isolated mock evaluator explicitly marked with `evaluation_mode: "MOCK"`.

---

### Endpoint: `POST /api/v1/eligibility/check`

#### Request Payload
```json
{
  "student_id": "<student-uuid>",
  "scholarship_id": "<scholarship-uuid>"
}
```

#### Fields:
- **`student_id`**: `String`, UUID of the student to evaluate.
- **`scholarship_id`**: `String`, UUID of the target scholarship scheme.

#### Validation & Behavior
1. Look up `student_id` in `students`. If not found -> reject with `HTTP 404 Not Found` (`{"detail": "Student not found"}`).
2. Look up `scholarship_id` in `scholarships`. If not found -> reject with `HTTP 404 Not Found` (`{"detail": "Scholarship not found"}`).
3. Delegate to the isolated mock evaluator (`evaluate_mock_eligibility`).
4. Return the evaluation result with explicit mock disclosure.

#### Success Response (`HTTP 200 OK`)
```json
{
  "student_id": "<student-uuid>",
  "scholarship_id": "<scholarship-uuid>",
  "eligible": true,
  "reasons": [
    "Mock eligibility evaluation only; official scheme rules are not configured"
  ],
  "evaluation_mode": "MOCK"
}
```

#### Error Responses
- **Missing Student:** `HTTP 404 Not Found`
  ```json
  {"detail": "Student not found"}
  ```
- **Missing Scholarship:** `HTTP 404 Not Found`
  ```json
  {"detail": "Scholarship not found"}
  ```

---

## 3. Phase-1 Deferred Features (Out of Scope for Current Step)

The following features require subsequent team contracts and official government criteria, and must **NOT** be implemented in Phase 1:
- Persistent eligibility history or evaluation logs database tables
- Configurable rules engine / decision table schema
- Real MoTA / State scholarship eligibility criteria evaluation
- Automatic document verification checks during eligibility
- Auto-application creation triggered by eligibility checks
