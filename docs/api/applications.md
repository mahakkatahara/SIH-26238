# Application Module API Contract

## 1. Playbook-Defined Requirements

The following requirements are explicitly mandated by the **TribalSetu Team Development & Integration Playbook**:

### Module Ownership & Responsibilities
- **Owner:** Backend/Core owns FastAPI, student profile, schemes, applications, and database.
- **Primary Responsibilities:** Draft/submit/application lifecycle and application APIs.

### Endpoints
- `GET /api/v1/applications`
- `POST /api/v1/applications`
- `GET /api/v1/applications/{id}/timeline` *(Application tracker)*

### Allowed Application Status Vocabulary (Playbook Section 16, Table 3)
Only the following exact uppercase status values are permitted:
```text
DRAFT, SUBMITTED, IN_VERIFICATION, DEFICIENCY, SANCTIONED, REJECTED, WITHDRAWN, COMPLETED
```
*Rule: Do not invent alternate spellings or unapproved statuses.*

### Dependencies
- Application depends on:
  - **Student** (Profile ownership)
  - **Scheme** (Target scholarship)
  - **Documents** (Supporting assets)
- Downstream modules depending on Applications:
  - **Verification:** depends on Application, documents, adapters (`GET /api/v1/applications/{id}/verifications`)
  - **Manual Review:** exception queue depends on Verification, applications
  - **Payments:** depends on Applications, adapters (`GET /api/v1/applications/{id}/payments`)
  - **Notifications:** depends on Users, applications
  - **JAGO:** calls approved service for Application status

### Architecture & Database Rules
- **Internal IDs:** UUID strings are the project rule for internal IDs.
- **Database Ownership:** PostgreSQL is owned exclusively by Backend/Core.
- **Migrations:** All schema changes must be applied via Alembic migrations.
- **Status Separation:** Keep application status and status history separate.
- **Document Reusability:** Documents are reusable student assets; `application_documents` links them to applications.

---

## 2. Team-Approved Phase-1 Contract

The following decisions are **TEAM-APPROVED** for minimal Phase-1 implementation and must not be confused with playbook-defined requirements.

### Database Table: `applications`

```sql
CREATE TABLE applications (
    id VARCHAR PRIMARY KEY,
    student_id VARCHAR NOT NULL REFERENCES students(id),
    scholarship_id VARCHAR NOT NULL REFERENCES scholarships(id),
    status VARCHAR NOT NULL
);
```

#### Fields ONLY:
- **`id`**: `String`, internally generated UUID, `PRIMARY KEY`, `NOT NULL`
- **`student_id`**: `String`, `FOREIGN KEY -> students.id`, `NOT NULL`
- **`scholarship_id`**: `String`, `FOREIGN KEY -> scholarships.id`, `NOT NULL`
- **`status`**: `String`, `NOT NULL` (values must be from the playbook status vocabulary).

*Team Decision:* New applications created default to initial status **`DRAFT`**.

---

### POST Endpoint: `POST /api/v1/applications`

#### Request Payload
```json
{
  "student_id": "<student-uuid>",
  "scholarship_id": "<scholarship-uuid>"
}
```

#### Behavior
1. Validate that `student_id` exists in `students`. If not -> `HTTP 404 Not Found`.
2. Validate that `scholarship_id` exists in `scholarships`. If not -> `HTTP 404 Not Found`.
3. Construct the application with generated UUID and default status `DRAFT`.
4. Persist to PostgreSQL and return the created record.

#### Success Response (`HTTP 200 OK`)
```json
{
  "id": "<application-uuid>",
  "student_id": "<student-uuid>",
  "scholarship_id": "<scholarship-uuid>",
  "status": "DRAFT"
}
```

---

### GET Endpoint: `GET /api/v1/applications`

#### Success Response (`HTTP 200 OK`)
```json
[
  {
    "id": "<application-uuid>",
    "student_id": "<student-uuid>",
    "scholarship_id": "<scholarship-uuid>",
    "status": "DRAFT"
  }
]
```

---

## 3. Application Lifecycle — Team-Approved Phase-2

### State Machine & Allowed Transitions

```text
DRAFT ───────────────> SUBMITTED ───────────────> IN_VERIFICATION
  │                        │                            │   │
  │ (withdraw)             │ (withdraw)                 │   │
  ▼                        ▼                            │   │
WITHDRAWN               WITHDRAWN                       │   │
                                                        │   │
                                                        ▼   ▼
                           SANCTIONED <───────── DEFICIENCY (re-verify)
                                │                      │
                                │                      │ (withdraw)
                                ▼                      ▼
                            COMPLETED              WITHDRAWN

IN_VERIFICATION ──────> REJECTED
```

#### Allowed Transition Map:
- **`DRAFT`** -> `SUBMITTED`, `WITHDRAWN`
- **`SUBMITTED`** -> `IN_VERIFICATION`, `WITHDRAWN`
- **`IN_VERIFICATION`** -> `DEFICIENCY`, `SANCTIONED`, `REJECTED`
- **`DEFICIENCY`** -> `IN_VERIFICATION`, `WITHDRAWN`
- **`SANCTIONED`** -> `COMPLETED`
- **Terminal States:** `REJECTED`, `WITHDRAWN`, `COMPLETED` (No transitions permitted from these states).
- **Same-state transitions:** Prohibited (e.g. `SUBMITTED` -> `SUBMITTED` is rejected with `HTTP 409`).

---

### Automation Boundary
- Application lifecycle transitions in Phase-2 are controlled through the status transition API.
- Cross-module automatic status transitions (e.g. verification outcomes automatically causing `DEFICIENCY` or `SANCTIONED`, or payment triggers) are **NOT** coupled in this phase.

---

### Database Table: `application_status_history`

```sql
CREATE TABLE application_status_history (
    id VARCHAR PRIMARY KEY,
    application_id VARCHAR NOT NULL REFERENCES applications(id),
    from_status VARCHAR NOT NULL,
    to_status VARCHAR NOT NULL
);
```

#### Fields ONLY:
- **`id`**: `String`, generated UUID, `PRIMARY KEY`, `NOT NULL`
- **`application_id`**: `String`, `FOREIGN KEY -> applications.id`, `NOT NULL`
- **`from_status`**: `String`, `NOT NULL`
- **`to_status`**: `String`, `NOT NULL`

#### History Rule:
- No history row is created for the initial `DRAFT` creation.
- History begins on the first actual transition (e.g. `DRAFT -> SUBMITTED`).
- Failed transition attempts do NOT create history rows.
- Atomic transaction: `Application.status` update and `application_status_history` insertion commit together.

---

### Endpoints

#### 1. Transition Application Status: `POST /api/v1/applications/{application_id}/status`

##### Request Payload
```json
{
  "status": "SUBMITTED"
}
```

##### Validation Order:
1. **Application Existence:** Check if `application_id` exists in `applications`. If missing -> `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
2. **Vocabulary Check:** Check if requested `status` belongs to the official Playbook vocabulary (`DRAFT`, `SUBMITTED`, `IN_VERIFICATION`, `DEFICIENCY`, `SANCTIONED`, `REJECTED`, `WITHDRAWN`, `COMPLETED`). If not -> `HTTP 400 Bad Request` (`{"detail": "Invalid application status"}`).
3. **Transition Validation:** Check if transition from `application.status` to `status` is permitted by the state machine. If not -> `HTTP 409 Conflict` (`{"detail": "Invalid application status transition"}`).
4. **Atomic Update:**
   - Update `application.status = status`.
   - Insert row into `application_status_history` (`from_status=old_status`, `to_status=new_status`).
   - Single commit.

##### Success Response (`HTTP 200 OK`):
```json
{
  "id": "<application-uuid>",
  "student_id": "<student-uuid>",
  "scholarship_id": "<scholarship-uuid>",
  "status": "SUBMITTED"
}
```

---

#### 2. Get Application Timeline: `GET /api/v1/applications/{application_id}/timeline`

##### Behavior:
1. Check if `application_id` exists. If missing -> `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
2. Query `application_status_history` for `application_id`.
3. If no transitions have occurred, return `HTTP 200 OK` with `[]`.

##### Success Response (`HTTP 200 OK`):
```json
[
  {
    "id": "<history-uuid>",
    "application_id": "<application-uuid>",
    "from_status": "DRAFT",
    "to_status": "SUBMITTED"
  }
]
```
