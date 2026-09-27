# Verification Module API Contract

## 1. Playbook-Defined Requirements

The following requirements are explicitly mandated by the **TribalSetu Team Development & Integration Playbook**:

### Core Architecture & Ownership
- **Owner:** The `Verification/Eligibility` role owns rules engine, eligibility API, documents, **verification records**, and manual review APIs (Playbook Section 3 & Section 24).
- **Primary Responsibilities:** "Checks + results" (Playbook Section 13, Table 2).
- **Dependencies:** Verification depends on `Application, documents, adapters`.
- **User Flow Placement:** In the end-to-end journey, documents are attached before Verification:
  `... Create application ↓ Attach DigiLocker/mock documents ↓ Verification ↓ Mismatch → Manual Review ...` (Section 20, Rule 176).
- **Mismatch Routing:** A verification check resulting in `MISMATCH` routes the item toward `Manual Review`.
- **Adapter Boundary:** The adapter interface conceptually exposes `verifyDocument()` (Section 14, Rule 118). Real government APIs must not be invented; mock adapters are used for integration and demo.

### Playbook Endpoints
- `GET /api/v1/applications/{id}/verifications`

### Allowed Verification Status Vocabulary (Section 16, Table 3)
Only the following exact uppercase status values are permitted in the Verification domain:
```text
PENDING, VERIFIED, MISMATCH, MANUAL_REVIEW, FAILED
```
*Rule: Do not invent alternate spellings such as 'processing' vs 'IN_PROCESS'.*

---

## 2. Team-Approved Phase-1 Contract

The following decisions are **TEAM-APPROVED** for the minimal Phase-1 implementation, and must not be confused with playbook-defined requirements.

### Scope & Deferred Implementations
- **Persistent Verification Records Only:** Phase 1 establishes the persistent record foundation for tracking verification checks on attached documents.
- **Adapters Deferred:** Direct DigiLocker adapter execution, external API calls, and mock automated verification runners are deferred.
- **Status Progression Deferred:** Dynamic status transitions (`VERIFIED`, `MISMATCH`, `MANUAL_REVIEW`, `FAILED`) are deferred. All records in Phase 1 start with initial status `PENDING`.
- **Manual Review Deferred:** Manual Review exception queue creation is deferred to a subsequent phase.

### Database Table: `verification_records`

```sql
CREATE TABLE verification_records (
    id VARCHAR PRIMARY KEY,
    application_id VARCHAR NOT NULL REFERENCES applications(id),
    document_id VARCHAR NOT NULL REFERENCES documents(id),
    status VARCHAR NOT NULL,
    CONSTRAINT uq_application_document_verification UNIQUE (application_id, document_id)
);
```

#### Fields ONLY:
- **`id`**: `String`, internally generated UUID, `PRIMARY KEY`, `NOT NULL`
- **`application_id`**: `String`, `FOREIGN KEY -> applications.id`, `NOT NULL`
- **`document_id`**: `String`, `FOREIGN KEY -> documents.id`, `NOT NULL`
- **`status`**: `String`, `NOT NULL`, default `PENDING`
- **Unique Constraint**: `(application_id, document_id)` prevents duplicate verification tracking records for the same application-document pair.

*Explicitly Excluded:*
- `notes`, `details`, `reason`, `mismatch_reason`
- `source`, `provider`, `evidence`
- `verified_at`, `created_at`, `updated_at`
- `reviewer`, `review_status`
- `external_id`, raw provider payload

---

### Endpoints

#### 1. Create Verification Record: `POST /api/v1/applications/{application_id}/verifications`

*Team Decision:* Since the playbook does not define an explicit creation endpoint for verification records, this endpoint establishes a `PENDING` verification record for an attached document before future adapter execution.

##### Request Payload
```json
{
  "document_id": "<document-uuid>"
}
```

##### Validation & Business Logic Order
1. Validate that `application_id` exists in `applications`. If missing -> reject with `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
2. Validate that `document_id` exists in `documents`. If missing -> reject with `HTTP 404 Not Found` (`{"detail": "Document not found"}`).
3. **Application Document Integrity:** Validate that `(application_id, document_id)` exists in `application_documents`. A verification record can ONLY be created for a document already attached to the application. If not linked -> reject with `HTTP 409 Conflict` (`{"detail": "Document is not linked to application"}`).
4. **Duplicate Protection:** Check if a verification record already exists for `(application_id, document_id)`. If exists -> reject with `HTTP 409 Conflict` (`{"detail": "Verification record already exists"}`).
5. Persist record with internally generated UUID and status `PENDING`.

##### Success Response (`HTTP 200 OK`)
```json
{
  "id": "<verification-uuid>",
  "application_id": "<application-uuid>",
  "document_id": "<document-uuid>",
  "status": "PENDING"
}
```

---

#### 2. List Application Verifications: `GET /api/v1/applications/{application_id}/verifications`

##### Behavior
1. Validate that `application_id` exists in `applications`. If missing -> reject with `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
2. Return all verification records associated with that application.
3. If no verification records exist, return `200 OK` with an empty array `[]`.

##### Success Response (`HTTP 200 OK`)
```json
[
  {
    "id": "<verification-uuid>",
    "application_id": "<application-uuid>",
    "document_id": "<document-uuid>",
    "status": "PENDING"
  }
]
```
- Direct JSON array: `list[VerificationRecordResponse]`.
