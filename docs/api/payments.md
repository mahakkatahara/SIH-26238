# Payments / DBT Module API Contract

## 1. Playbook-Defined Requirements

The following requirements and constraints are explicitly established by the **TribalSetu Team Development & Integration Playbook**:

### Core Architecture & Ownership
- **Owner:** The `Payments` module handles `DBT/payment status aggregation` (Section 13, Table 2).
- **Dependencies:** Payments depends directly on `Applications, adapters`.
- **User Journey Placement:** Payment occurs after application sanction:
  `... Create application ↓ Attach DigiLocker/mock documents ↓ Verification ↓ Mismatch → Manual Review ↓ Sanction ↓ DBT status ↓ JAGO explains status` (Section 20, Rule 176).
- **Playbook Endpoint:**
  - `GET /api/v1/applications/{id}/payments` (Section 7, Table 1).
- **Integration Boundary:**
  - Conceptual adapter method: `getPaymentStatus()` (Section 14).
  - External payment systems are abstracted via adapters (e.g. SFMP Adapter) rather than direct integration (Section 14).
- **JAGO Platform Integration:**
  - JAGO reads `Payment status` from approved internal services (Section 21).

### Exact Playbook Payment Status Vocabulary (Section 16, Table 3)
The Playbook strictly dictates the uppercase status vocabulary for the Payment domain:
```text
SANCTIONED, DBT_INITIATED, PROCESSING, CREDITED, FAILED
```
*Rule: Do not invent alternate spellings or unapproved statuses (e.g., 'PENDING', 'SUCCESS', or 'PAID' are strictly forbidden).*

---

## 2. Team-Approved Mock Phase-1 Contract

The following specifications represent **TEAM-APPROVED** choices for the simulated DBT payment tracking slice:

### Core Principles
1. **One Payment per Application:** Exactly one payment record corresponds to an application (`application_id` is unique).
2. **Sanction Precondition:** A payment record can **only** be created when the referenced application currently has `status == "SANCTIONED"`.
3. **Decoupled Creation:** Payment records are **not** created automatically when an application is transitioned to `SANCTIONED`. They must be explicitly created via the payment creation endpoint.
4. **Initial Payment Status:** Upon creation, `payments.status` defaults to `"SANCTIONED"` (matching the Playbook initial payment state).
5. **Decoupled Lifecycle Boundary:** Moving a payment to `"CREDITED"` does **not** automatically mutate the application status to `"COMPLETED"`. Application lifecycle and payment lifecycle remain independent in Phase-1.
6. **Stateless Mock Flow:** Purely simulates DBT status progression without real banking calls, financial account storage, or fabricated UTR numbers.

---

### Database Table: `payments`

```sql
CREATE TABLE payments (
    id VARCHAR PRIMARY KEY,
    application_id VARCHAR NOT NULL UNIQUE REFERENCES applications(id),
    status VARCHAR NOT NULL
);
```

#### Fields ONLY:
- **`id`**: `String`, generated UUID, `PRIMARY KEY`, `NOT NULL`
- **`application_id`**: `String`, `FOREIGN KEY -> applications.id`, `NOT NULL`, `UNIQUE`
- **`status`**: `String`, `NOT NULL`, default `"SANCTIONED"`

#### Explicitly Excluded Fields:
- `amount`, `currency`
- `bank_account`, `ifsc_code`, `beneficiary_name`
- `transaction_id`, `utr`, `sanction_number`
- `provider`, `external_reference`, `failure_reason`
- `created_at`, `updated_at`, `payment_date`, timestamps

---

### Exact Payment State Machine

```text
SANCTIONED ───────> DBT_INITIATED ───────> PROCESSING ───────┬───────> CREDITED (Terminal)
                                                             │
                                                             └───────> FAILED (Terminal)
```

#### Allowed Transitions:
- `SANCTIONED` -> `DBT_INITIATED`
- `DBT_INITIATED` -> `PROCESSING`
- `PROCESSING` -> `CREDITED`, `FAILED`
- **Terminal States:** `CREDITED`, `FAILED` (no further transitions permitted).
- **Invalid / Prohibited Transitions:** Any skipping of steps (e.g. `SANCTIONED -> PROCESSING`, `SANCTIONED -> CREDITED`), same-state transitions, or transitions from terminal states.

---

### Endpoints

#### 1. Create Payment Record: `POST /api/v1/applications/{application_id}/payments`

- **Request Body:** None (empty `POST`).
- **Validation Order & Business Logic:**
  1. Check if `application_id` exists in `applications`. If missing -> `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
  2. Check `application.status == "SANCTIONED"`. If not -> `HTTP 409 Conflict` (`{"detail": "Application is not sanctioned"}`).
  3. Check if a payment already exists for `application_id`. If exists -> `HTTP 409 Conflict` (`{"detail": "Payment already exists"}`).
  4. Create and persist `Payment(id=UUID, application_id=application_id, status="SANCTIONED")`.
- **Success Response (`HTTP 200 OK`):**
  ```json
  {
    "id": "<payment-uuid>",
    "application_id": "<application-uuid>",
    "status": "SANCTIONED"
  }
  ```

---

#### 2. Get Application Payments: `GET /api/v1/applications/{application_id}/payments`

- **Validation:**
  1. Check if `application_id` exists. If missing -> `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
- **Behavior:**
  - Queries `payments` table for `application_id`.
  - If no payment exists -> returns `HTTP 200 OK` with `[]`.
  - If payment exists -> returns `HTTP 200 OK` with `[PaymentResponse]`.
- **Success Response (`HTTP 200 OK`):**
  ```json
  [
    {
      "id": "<payment-uuid>",
      "application_id": "<application-uuid>",
      "status": "SANCTIONED"
    }
  ]
  ```

---

#### 3. Transition Payment Status: `POST /api/v1/payments/{payment_id}/status`

- **Request Body:**
  ```json
  {
    "status": "DBT_INITIATED"
  }
  ```
- **Validation Order:**
  1. Check if `payment_id` exists in `payments`. If missing -> `HTTP 404 Not Found` (`{"detail": "Payment not found"}`).
  2. Validate that `status` belongs to the exact Playbook vocabulary (`SANCTIONED`, `DBT_INITIATED`, `PROCESSING`, `CREDITED`, `FAILED`). If not -> `HTTP 400 Bad Request` (`{"detail": "Invalid payment status"}`).
  3. Validate transition from current `payment.status` to `status`. If not allowed -> `HTTP 409 Conflict` (`{"detail": "Invalid payment status transition"}`).
  4. Persist updated status and return.
- **Success Response (`HTTP 200 OK`):**
  ```json
  {
    "id": "<payment-uuid>",
    "application_id": "<application-uuid>",
    "status": "DBT_INITIATED"
  }
  ```

---

## 3. Deferred Live Integration Requirements

The following requirements are strictly out of scope for Phase-1 and are deferred to production government integration:
- Live SFMP / PFMS / NPCI gateway integration and authentication.
- Real money disbursements, bank account number validation, and Aadhaar-seeded account verification.
- Real bank UTR / transaction IDs and reconciliation feeds.
- Payment webhooks, retry queues, and automated dispute resolution.
- Automatic application completion triggers upon DBT credit.
