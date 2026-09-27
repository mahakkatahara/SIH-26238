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

### Allowed Application Status Vocabulary
Only the following uppercase status values are permitted:
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

*Team Decision:* New applications created during Phase 1 will default to initial status **`DRAFT`**.

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
1. Validate that the referenced `student_id` exists in `students`. If not, reject with HTTP 404.
2. Validate that the referenced `scholarship_id` exists in `scholarships`. If not, reject with HTTP 404.
3. Construct the application with an internally generated UUID and default status `DRAFT`.
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

#### Error Responses
- **Student not found:** `HTTP 404 Not Found` (`{"detail": "Student not found"}`)
- **Scholarship not found:** `HTTP 404 Not Found` (`{"detail": "Scholarship not found"}`)

---

### GET Endpoint: `GET /api/v1/applications`

#### Purpose
Returns a list of all application records currently in the system.

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
- Direct JSON array of application objects (`list[ApplicationResponse]`).
- No response envelope wrapper (consistent with Student and Scholarship endpoints).
- *Team Decision:* Authenticated student-scoped filtering is deferred; Phase 1 returns the catalogue-style list.

---

## 3. Phase-1 Deferred Features (Out of Scope for Current Step)

The following features require subsequent team contracts and must **NOT** be implemented in Phase 1:
- Separate timeline / status history table and endpoint (`GET /api/v1/applications/{id}/timeline`)
- `application_documents` junction table and document upload/linking
- Verification checks and adapter interfaces
- Manual review workflows
- Payment tracking
- Notifications
- Status transition endpoints (e.g. submit, sanction, reject, withdraw)
- `application_number`
- Timestamps (`created_at`, `updated_at`, `submitted_at`)
