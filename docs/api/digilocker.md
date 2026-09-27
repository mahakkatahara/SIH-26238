# DigiLocker Module API Contract

## 1. Playbook-Defined Requirements

The following architectural principles and requirements are established by the **TribalSetu Team Development & Integration Playbook**:

### Core Architecture & Ownership
- **Owner:** The `Integration Engineer` owns `NSP/SFMP/NOS/DigiLocker/APAAR/UDISE/AISHE adapter interfaces and mocks` (Section 3 & Section 24).
- **User Journey Placement:** Document acquisition precedes verification:
  `... Create application ↓ Attach DigiLocker/mock documents ↓ Verification ↓ Mismatch → Manual Review ...` (Section 20, Rule 176).
- **Adapter Boundary:** External systems must sit behind common adapter interfaces exposing conceptual methods (Section 14).
- **No Invented Government APIs:** Production endpoint details must come from authorized documentation and credentials; developers must not invent government APIs (Section 14).
- **SIH Mock Guidance:** For SIH, the Playbook explicitly permits and recommends mock adapters that simulate the behavior of external registries without claiming a live connection (Section 14).

---

## 2. Team-Approved Mock Phase-1 Contract

The following definitions and rules represent **TEAM-APPROVED** choices for the minimal mock DigiLocker acquisition slice:

### Core Principles
1. **Stateless Mock Document Catalogue:** Provides a deterministic list of simulated certificates commonly required for tribal scholarship applications.
2. **Student Existence Validation:** Any request to view or import documents must reference a valid registered `Student` in TribalSetu.
3. **Seamless Storage as Ordinary Documents:** When a mock document is imported, it is persisted directly into the existing `documents` table as a standard, reusable student asset with initial `status="PENDING"`.
4. **No Schema Expansion:** The `documents` table remains strictly unchanged (`id`, `student_id`, `document_type`, `document_name`, `status`). No provider, URI, issuer, or token columns are added.
5. **Service-Level Duplicate Protection:** A student cannot import the same mock `document_type` more than once. If an existing document with the same `(student_id, document_type)` exists, import is rejected with `HTTP 409 Conflict`.
6. **Strict Separation from Verification:** Acquisition produces documents in `PENDING` status. No automatic verification or status mutation occurs during acquisition.

### Deterministic Mock Catalogue
The mock adapter provides exactly four demo items in deterministic order:
1. `{"document_type": "MOCK_ST_CERTIFICATE", "document_name": "ST Certificate"}`
2. `{"document_type": "MOCK_INCOME_CERTIFICATE", "document_name": "Income Certificate"}`
3. `{"document_type": "MOCK_CLASS_12_MARKSHEET", "document_name": "Class 12 Marksheet"}`
4. `{"document_type": "MOCK_DOMICILE_CERTIFICATE", "document_name": "Domicile Certificate"}`

*Note: These are synthetic demo identifiers approved for SIH demonstration and are not official DigiLocker DocType codes.*

---

## 3. Endpoints

### 1. View Mock DigiLocker Documents: `GET /api/v1/students/{student_id}/digilocker/documents`

- **Request Body:** None.
- **Validation:**
  1. Check if `student_id` exists. If not -> `HTTP 404 Not Found` (`{"detail": "Student not found"}`).
- **Success Response (`HTTP 200 OK`):**
  Direct JSON array of available mock certificates:
  ```json
  [
    {
      "document_type": "MOCK_ST_CERTIFICATE",
      "document_name": "ST Certificate"
    },
    {
      "document_type": "MOCK_INCOME_CERTIFICATE",
      "document_name": "Income Certificate"
    },
    {
      "document_type": "MOCK_CLASS_12_MARKSHEET",
      "document_name": "Class 12 Marksheet"
    },
    {
      "document_type": "MOCK_DOMICILE_CERTIFICATE",
      "document_name": "Domicile Certificate"
    }
  ]
  ```

---

### 2. Import Mock DigiLocker Document: `POST /api/v1/students/{student_id}/digilocker/documents/import`

- **Request Body:**
  ```json
  {
    "document_type": "MOCK_ST_CERTIFICATE"
  }
  ```
- **Validation Order & Business Logic:**
  1. Check if `student_id` exists in `students`. If missing -> reject with `HTTP 404 Not Found` (`{"detail": "Student not found"}`).
  2. Validate that `document_type` exists in the mock catalogue. If not found -> reject with `HTTP 404 Not Found` (`{"detail": "Mock DigiLocker document not found"}`).
  3. Check if the student already has an imported document with the same `document_type`. If duplicate -> reject with `HTTP 409 Conflict` (`{"detail": "Mock DigiLocker document already imported"}`).
  4. Create and persist an ordinary `Document` row:
     - `id`: generated UUID
     - `student_id`: target student
     - `document_type`: requested mock document type
     - `document_name`: canonical mock document name
     - `status`: `"PENDING"`
- **Success Response (`HTTP 200 OK`):**
  Standard `DocumentResponse`:
  ```json
  {
    "id": "<document-uuid>",
    "student_id": "<student-uuid>",
    "document_type": "MOCK_ST_CERTIFICATE",
    "document_name": "ST Certificate",
    "status": "PENDING"
  }
  ```

---

## 4. Deferred Live Integration Requirements

The following components are strictly deferred to future live integration phases and are not part of Phase-1:
- Requester onboarding and organization whitelisting with API Setu / NeGD.
- OAuth 2.0 authorization code flow (`/authorize`, `/token`, `/callback`).
- Student consent receipts and lifecycle tracking.
- Access token and refresh token handling, storage, and encryption.
- DigiLocker user account linking (`digilocker_id`).
- Official document URIs, XML parsing, and issuer digital signature validation.
- Live file downloads (PDF/XML binaries) and cloud storage integration.
