# Document Module API Contract

## 1. Playbook-Defined Requirements

The following requirements are explicitly mandated by the **TribalSetu Team Development & Integration Playbook**:

### Module Ownership & Responsibilities
- **Owner:** Verification/Eligibility role owns rules engine, eligibility API, documents, verification records, manual review APIs.
- **Backend/Core:** Owns PostgreSQL, migrations, auth, student profile, schemes, applications, and database.
- **Integrations:** Owns adapter interfaces and mocks (NSP, SFMP, NOS, DigiLocker, APAAR, UDISE, AISHE).

### Endpoints
- `GET /api/v1/documents`
- `POST /api/v1/documents`

### Allowed Document Status Vocabulary
Only the following uppercase status values are permitted:
```text
PENDING, VERIFIED, EXPIRED, REJECTED
```
*Rule: Do not invent alternate spellings or unapproved statuses.*

### Architecture & Database Rules
- **Internal IDs:** UUID strings are the project rule for internal IDs.
- **Document Reusability:** Documents are reusable student assets; `application_documents` links them to applications.
- **Verification Dependency:** Verification checks depend on `Application, documents, adapters`.
- **Integration Boundary:** DigiLocker integration belongs behind adapter interfaces; production credentials/endpoints must not be invented.

---

## 2. Team-Approved Phase-1 Contract

The following decisions are **TEAM-APPROVED** for a minimal Phase-1 implementation focusing on **document metadata only**, and must not be confused with playbook-defined requirements.

### Scope & Deferred Implementations
- **Metadata Only:** Phase 1 implements document metadata persistence.
- **Binary Upload/Storage Deferred:** Actual file storage (local storage, S3, MinIO) and multipart file upload (`UploadFile`) are deferred.
- **DigiLocker Integration Deferred:** Direct DigiLocker API integration is deferred behind future adapter contracts.
- **Application Linking Deferred:** The `application_documents` junction table and document attachment endpoints are deferred.
- **Verification Deferred:** Verification workflows and status transitions are deferred.

### Database Table: `documents`

```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    student_id VARCHAR NOT NULL REFERENCES students(id),
    document_type VARCHAR NOT NULL,
    document_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL
);
```

#### Fields ONLY:
- **`id`**: `String`, internally generated UUID, `PRIMARY KEY`, `NOT NULL`
- **`student_id`**: `String`, `FOREIGN KEY -> students.id`, `NOT NULL`
- **`document_type`**: `String`, `NOT NULL` (*Team Decision: Free-form string in Phase 1; no strict enum yet*)
- **`document_name`**: `String`, `NOT NULL`
- **`status`**: `String`, `NOT NULL` (*Team Decision: New document metadata records default to initial status `PENDING`*)

*Explicitly Excluded in Phase 1:*
- `file_url`, `file_path`, MIME type, storage bucket keys
- DigiLocker document identifiers / URIs
- Timestamps (`created_at`, `updated_at`, `issued_at`, `expires_at`)
- Verification metadata / audit logs
- `application_id` column (preserves reusable student asset design)

---

### POST Endpoint: `POST /api/v1/documents`

#### Request Payload
```json
{
  "student_id": "<student-uuid>",
  "document_type": "<string>",
  "document_name": "<string>"
}
```

#### Behavior
1. Validate that the referenced `student_id` exists in `students`. If not, reject with HTTP 404.
2. Construct the document record with an internally generated UUID and initial status `PENDING`.
3. Persist to PostgreSQL and return the created document record.

#### Success Response (`HTTP 200 OK`)
```json
{
  "id": "<document-uuid>",
  "student_id": "<student-uuid>",
  "document_type": "<string>",
  "document_name": "<string>",
  "status": "PENDING"
}
```

#### Error Response
- **Student not found:** `HTTP 404 Not Found` (`{"detail": "Student not found"}`)

---

### GET Endpoint: `GET /api/v1/documents`

#### Purpose
Returns a list of all document metadata records currently registered in the system.

#### Success Response (`HTTP 200 OK`)
```json
[
  {
    "id": "<document-uuid>",
    "student_id": "<student-uuid>",
    "document_type": "<string>",
    "document_name": "<string>",
    "status": "PENDING"
  }
]
```
- Direct JSON array of document objects (`list[DocumentResponse]`).
- No response envelope wrapper (consistent with Student, Scholarship, and Application endpoints).
- *Team Decision:* Authenticated student-scoped filtering is deferred; Phase 1 returns all documents.

---

## 3. Phase-1 Deferred Features (Out of Scope for Current Step)

The following features require subsequent team contracts and must **NOT** be implemented in Phase 1:
- `application_documents` junction table and document-to-application attachment API
- Binary file upload handling (`UploadFile` / multipart form data)
- File storage engines (local disk, AWS S3, MinIO)
- DigiLocker adapter integration and identifiers
- Document verification pipeline and manual review workflows
- Document status transitions (`VERIFIED`, `EXPIRED`, `REJECTED`)
- Strict document type catalog/enum
- Authenticated student-scoped document filtering
