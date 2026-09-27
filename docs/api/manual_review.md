# Manual Review Module API Contract

## 1. Playbook-Defined Requirements

The following concepts and constraints are explicitly established by the **TribalSetu Team Development & Integration Playbook**:

### Core Architecture & Ownership
- **Owner:** The `Verification/Eligibility` role owns rules engine, eligibility API, documents, verification records, and **manual review APIs** (Playbook Section 3 & Section 24).
- **Primary Responsibility:** Serves as an **Exception queue** for mismatches and anomalies (Playbook Section 13, Table 2).
- **Dependencies:** Manual Review depends directly on **Verification** and **Applications** (`Verification, Applications`).
- **User Journey Placement:** In the end-to-end applicant journey:
  `... Create application ↓ Attach DigiLocker/mock documents ↓ Verification ↓ Mismatch → Manual Review ...` (Section 20, Rule 176).
- **Review Status Vocabulary (Section 16, Table 3):**
  Only the following exact uppercase status values are defined for the review lifecycle:
  ```text
  OPEN, ASSIGNED, RESOLVED, ESCALATED
  ```
- **Verification Status Vocabulary Linkage:**
  The verification lifecycle includes the explicit status value:
  ```text
  MANUAL_REVIEW
  ```

### Playbook Gaps & Undefined Semantics
The Playbook intentionally leaves implementation specifics open for team definition:
- The Playbook does **NOT** define specific Manual Review HTTP endpoints or path contracts.
- The Playbook does **NOT** define the Manual Review database schema or table structure.
- **Reviewer assignment** semantics and mechanisms (who assigns, roles, capacity) are undefined.
- **Resolution** semantics (approval, rejection, document re-submission) are undefined.
- **Escalation** semantics and hierarchy are undefined.
- **Deficiency integration** (triggers, applicant notification, remediation) is undefined.

---

## 2. Team-Approved Phase-1 Contract

The following definitions and rules represent **TEAM-APPROVED** design choices for the minimal Phase-1 implementation and must not be cited as direct playbook mandates.

### Core Policies
1. **One-to-One Verification Mapping:** Exactly one Manual Review record corresponds to a single Verification record (`verification_id` is unique).
2. **Strict Ingestion Precondition:** Only a verification record currently in the `MISMATCH` state may be queued for Manual Review.
3. **Atomic Queueing & Transition:** Enqueuing an item creates a `manual_reviews` record with status `OPEN` and atomically transitions the associated `verification_records.status` from `MISMATCH` to `MANUAL_REVIEW`.
4. **Normalized Persistence (No Redundant document_id):** The `manual_reviews` table does **NOT** store `document_id`. The document is always reachable via `manual_reviews.verification_id -> verification_records.document_id`.

---

## 3. Database Table: `manual_reviews`

```sql
CREATE TABLE manual_reviews (
    id VARCHAR PRIMARY KEY,
    application_id VARCHAR NOT NULL REFERENCES applications(id),
    verification_id VARCHAR NOT NULL UNIQUE REFERENCES verification_records(id),
    status VARCHAR NOT NULL
);
```

### Table Fields ONLY:
- **`id`**: `String`, internally generated UUID, `PRIMARY KEY`, `NOT NULL`.
- **`application_id`**: `String`, `FOREIGN KEY -> applications.id`, `NOT NULL`.
- **`verification_id`**: `String`, `FOREIGN KEY -> verification_records.id`, `NOT NULL`, `UNIQUE`.
- **`status`**: `String`, `NOT NULL`, initial default value `"OPEN"`.

### Explicitly Excluded Fields (Phase-1):
- `document_id` (reachable via `verification_records`)
- `assigned_to`, `reviewer_id`
- `reason`, `resolution`, `notes`, `evidence`
- `created_at`, `updated_at`, `resolved_at`, `escalated_at`

---

## 4. Endpoints

### 1. Enqueue Verification for Manual Review: `POST /api/v1/verifications/{verification_id}/manual-review`

- **Request Body:** None (empty `POST`).
- **Authorization / RBAC:** None for Phase-1 minimal slice.

#### Business Logic & Validation Order:
1. **Verification Existence:** Check if `verification_id` exists in `verification_records`.
   - If not found -> reject with `HTTP 404 Not Found` (`{"detail": "Verification record not found"}`).
2. **Status Eligibility:** Check `verification.status == "MISMATCH"`.
   - If status is not `MISMATCH` -> reject with `HTTP 409 Conflict` (`{"detail": "Verification record is not eligible for manual review"}`).
3. **Duplicate Review Check:** Check if a `manual_reviews` row already exists for `verification_id`.
   - If exists -> reject with `HTTP 409 Conflict` (`{"detail": "Manual review already exists"}`).
4. **Data Derivation:** Retrieve `application_id` directly from `VerificationRecord` (never accepted from client input).
5. **Atomic State Transition:** In a single atomic database transaction:
   - Insert new `ManualReview` row (`id=UUID`, `application_id`, `verification_id`, `status="OPEN"`).
   - Update `verification_records.status` to `"MANUAL_REVIEW"`.
   - Commit once.

#### Deterministic Error Ordering Note:
Once a verification record has been successfully queued, its status becomes `"MANUAL_REVIEW"`.
If the same `POST` endpoint is invoked again for that verification record, condition #2 (`status == "MISMATCH"`) fails first before duplicate check #3. Therefore, repeated requests deterministically return:
`HTTP 409 Conflict` with `{"detail": "Verification record is not eligible for manual review"}`.

#### Success Response (`HTTP 200 OK`):
```json
{
  "id": "<manual-review-uuid>",
  "application_id": "<application-uuid>",
  "verification_id": "<verification-uuid>",
  "status": "OPEN"
}
```

---

### 2. List Exception Queue: `GET /api/v1/manual-reviews`

- **Request Body / Parameters:** None.
- **Behavior:** Queries and returns all `manual_reviews` records.
- **Empty State:** If queue is empty, returns `HTTP 200 OK` with `[]`.

#### Success Response (`HTTP 200 OK`):
```json
[
  {
    "id": "<manual-review-uuid>",
    "application_id": "<application-uuid>",
    "verification_id": "<verification-uuid>",
    "status": "OPEN"
  }
]
```
- Direct JSON array: `list[ManualReviewResponse]`.

---

## 5. Scope Boundary (Deferred Behaviors)

Phase-1 strictly excludes the following:
- Reviewer assignment / claim actions (`ASSIGNED` status).
- Review resolution / overrides (`RESOLVED` status).
- Escalation workflows (`ESCALATED` status).
- Deficiency creation or application state progression to `DEFICIENCY`.
- Application or Document status modifications.
- DigiLocker / external government API integration.
- Authentication / RBAC role restrictions on the review queue.
- Background worker tasks or notification dispatches.
