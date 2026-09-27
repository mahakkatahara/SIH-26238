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

---

## 3. Team-Approved Phase-2 Contract — Mock Verification Execution

### Playbook Alignment & Boundaries
- The Playbook defines the conceptual adapter method **`verifyDocument()`** (Section 14).
- The Playbook permits and recommends **mock adapters for SIH** ("For SIH, use mock adapters that behave like the real systems").
- Production government endpoint details must come from authorized documentation and credentials; real government APIs are **not** invented.
- This implementation is **strictly a mock integration** for demonstration purposes and is **NOT** a live DigiLocker or official government verification service.

---

### Adapter Boundary: `MockVerificationAdapter`

- Located under `backend/app/integrations/verification/mock_adapter.py`.
- Exposes `verify_document(document: Document) -> dict`.
- Returns an internal execution outcome dictionary:
  ```python
  {
      "status": "VERIFIED" | "MISMATCH" | "FAILED",
      "message": "<mock explanation>",
      "evaluation_mode": "MOCK"
  }
  ```
- **Evaluation Mode:** `evaluation_mode` is always `"MOCK"`.
- **Stateless Metadata:** `message` and `evaluation_mode` are returned in the execution response only and are **not** persisted to PostgreSQL. The database table `verification_records` remains strictly: `id`, `application_id`, `document_id`, `status`.

---

### Deterministic Mock Behavior

The mock adapter executes purely deterministic demo rules without random generation, external network requests, or fake government heuristics. It inspects only explicit test markers on `document.document_type`:

| Marker / `document_type` | Resulting `status` | Message / Description |
| :--- | :--- | :--- |
| `TEST_VERIFIED` | `VERIFIED` | `"Mock document successfully verified against simulated issuer registry"` |
| `TEST_MISMATCH` | `MISMATCH` | `"Mock document attributes do not match student records (mismatch simulated)"` |
| `TEST_FAILED` | `FAILED` | `"Mock document verification failed (simulated issuer failure)"` |
| *Any other `document_type`* | `FAILED` | `"Mock adapter has no configured verification rule for this document type"` |

---

### Execution Endpoint: `POST /api/v1/verifications/{verification_id}/execute`

#### Request Payload
- None (HTTP `POST` with empty body).

#### Business Logic & State Transitions
1. Lookup `verification_id` in `verification_records`. If not found -> reject with `HTTP 404 Not Found` (`{"detail": "Verification record not found"}`).
2. **Pending State Check:** Verify `verification.status == "PENDING"`. If status is already `VERIFIED`, `MISMATCH`, or `FAILED` -> reject with `HTTP 409 Conflict` (`{"detail": "Verification record is not pending"}`).
3. Load the associated `document_id` from `documents`. If missing -> reject with `HTTP 404 Not Found` (`{"detail": "Document not found"}`).
4. Invoke `MockVerificationAdapter.verify_document(document)`.
5. Update `verification_records.status` to the adapter's resulting status (`VERIFIED`, `MISMATCH`, or `FAILED`).
6. Return `VerificationExecutionResponse`.

#### Allowed Transitions
- `PENDING -> VERIFIED`
- `PENDING -> MISMATCH`
- `PENDING -> FAILED`

*Forbidden:*
- `VERIFIED -> *`
- `MISMATCH -> *`
- `FAILED -> *`
- `PENDING -> MANUAL_REVIEW` (Manual Review queue belongs to the next module)

#### Success Response (`HTTP 200 OK`)
```json
{
  "id": "<verification-id>",
  "application_id": "<application-id>",
  "document_id": "<document-id>",
  "status": "VERIFIED|MISMATCH|FAILED",
  "message": "<mock explanation>",
  "evaluation_mode": "MOCK"
}
```

#### Error Responses
- **Verification record missing:** `HTTP 404 Not Found` (`{"detail": "Verification record not found"}`)
- **Verification record not pending:** `HTTP 409 Conflict` (`{"detail": "Verification record is not pending"}`)
- **Associated document missing:** `HTTP 404 Not Found` (`{"detail": "Document not found"}`)

---

## 4. Real Digitally Signed PDF Verification Contract (`evaluation_mode = SIGNED_PDF`)

### Architecture & Boundaries
For documents acquired via PDF upload (`source = "PDF_UPLOAD"`), verification is executed locally using **pyHanko** (cryptographic digital signature verification) and **pdfplumber** (text & metadata extraction), eliminating fake APIs or third-party network vulnerabilities.

### Upload Endpoint: `POST /api/v1/students/{student_id}/documents/upload`
- **Request:** `multipart/form-data` with:
  - `file`: PDF file (`max 5 MB`)
  - `document_type`: `ST_CERTIFICATE | INCOME_CERTIFICATE | CLASS_12_MARKSHEET | DOMICILE_CERTIFICATE`
- **Storage:** Persisted locally to `backend/uploads/` (gitignored).
- **Database:** Creates `Document` row with:
  - `file_path`: Absolute path on disk
  - `source`: `"PDF_UPLOAD"`
  - `status`: `"PENDING"`

### Verification Flow & Evaluation Rules
1. **Digital Signature & Trust Root Verification (`pyHanko`):**
   - Embedded digital signature is extracted. If missing -> `FAILED` (`"Digital signature missing from PDF"`).
   - Byte-range integrity is validated (`val_status.intact`). If tampered or modified after signing -> `FAILED` (`"Digital signature is invalid or document has been modified after signing"`).
   - Certificate chain is cryptographically validated against official Indian CCA root certificates (`backend/app/data/trust_roots/`) using pyHanko `ValidationContext`. If self-signed or not issued by an authorized Indian Root CA -> `FAILED` (`"Certificate not issued by a trusted Indian CA"`).
   - Only after certificate chain trust is established, signer name is checked against `TRUSTED_SIGNERS` in `.env`.
2. **Text Extraction & Student Profile Matching (`pdfplumber` + `rapidfuzz`):**
   - Candidate Name, Date of Birth, and Income (for `INCOME_CERTIFICATE`) are extracted from certificate text.
   - Name is compared with the student's registered profile using fuzzy token sort matching (`rapidfuzz`). If similarity is below threshold -> `MISMATCH` (`"Name on certificate '<extracted>' does not match profile '<profile>'"`).
   - Date of Birth and Income (for income certificates) are validated against profile attributes. If different -> `MISMATCH`.
3. **Execution Outcomes & State Transitions:**
   - **`FAILED`:** Signature missing, signature invalid, PDF modified after signing, untrusted CA root, or signer not in trusted list.
   - **`MISMATCH`:** Cryptographic signature valid and trusted, but extracted certificate data does not match the student's profile. Automatically enqueued to `manual_reviews` exception queue for officer review.
   - **`VERIFIED`:** Signature intact, certificate chain valid to Indian CCA root, signer trusted, and certificate metadata matches student profile.
   - **Evaluation Mode:** Always returns `evaluation_mode = "SIGNED_PDF"`.

### Adapter Routing Rules
- Only documents with `source = "PDF_UPLOAD"` route to `SignedPdfVerificationAdapter`.
- All other documents (`source = "MOCK"`, `source = "DIGILOCKER_MOCK"`, or `source = None`) route to `MockVerificationAdapter` (`evaluation_mode = "MOCK"`).
- `documents.source` defaults to `NULL`, with mock imports setting `source = "DIGILOCKER_MOCK"`. Existing legacy documents are backfilled to `source = "MOCK"` where `file_path` is null.

