# TribalSetu Backend - Frontend Integration Contract

**Document Version:** 1.0.0  
**Target Client:** Flutter Mobile & Web Application  
**Base URL (Local Development):** `http://localhost:8000` (or `http://10.0.2.2:8000` for Android Emulator)  
**API Documentation (Swagger UI):** `http://localhost:8000/docs`  
**OpenAPI Specification:** `http://localhost:8000/openapi.json`  

---

## 1. Authentication Status (Honest Disclosure)

> [!IMPORTANT]  
> **Current Authentication Implementation Status:**  
> - User registration (`POST /api/v1/users`) and login verification (`POST /api/v1/users/login`) are implemented using salted `bcrypt` password hashes.  
> - **Bearer tokens, JWT access/refresh tokens, and cookie-based sessions are NOT yet implemented.**  
> - The login endpoint validates credentials and returns the basic `UserResponse` object (`id`, `name`, `email`).  
> - Downstream endpoints (such as `applications`, `documents`, `students`) currently expect explicit IDs in request bodies and URL paths rather than reading user identity from an `Authorization` header.  
> - Do not attempt to pass `Authorization: Bearer <token>` expecting token introspection.

---

## 2. Health & Infrastructure Endpoints

### 2.1 API Greeting / Root
- **METHOD:** `GET`
- **PATH:** `/`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  {
    "status": "ok",
    "message": "TribalSetu API is running"
  }
  ```

### 2.2 Liveness Health Check
- **METHOD:** `GET`
- **PATH:** `/health`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  {
    "status": "ok"
  }
  ```

### 2.3 Database Connectivity Health Check
- **METHOD:** `GET`
- **PATH:** `/health/db`
- **REQUEST:** None
- **RESPONSE (`200 OK` when connected):**
  ```json
  {
    "status": "ok",
    "database": "connected"
  }
  ```
- **RESPONSE (`503 Service Unavailable` when disconnected):**
  ```json
  {
    "status": "error",
    "database": "disconnected"
  }
  ```

---

## 3. Users & Auth APIs

### 3.1 Register User
- **METHOD:** `POST`
- **PATH:** `/api/v1/users`
- **REQUEST:**
  ```json
  {
    "name": "Ravi Kumar",
    "email": "ravi.kumar@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "11111111-2222-3333-4444-555555555555",
    "name": "Ravi Kumar",
    "email": "ravi.kumar@example.com"
  }
  ```
- **COMMON ERRORS:**
  - `409 Conflict`: `{"detail": "Email already exists"}`
  - `422 Unprocessable Entity`: Invalid email format or missing fields.

### 3.2 Login User
- **METHOD:** `POST`
- **PATH:** `/api/v1/users/login`
- **REQUEST:**
  ```json
  {
    "email": "ravi.kumar@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "11111111-2222-3333-4444-555555555555",
    "name": "Ravi Kumar",
    "email": "ravi.kumar@example.com"
  }
  ```
- **COMMON ERRORS:**
  - `401 Unauthorized`: `{"detail": "Invalid email or password"}`

---

## 4. Student Profile APIs

### 4.1 Create Student Profile
- **METHOD:** `POST`
- **PATH:** `/api/v1/students`
- **REQUEST:**
  ```json
  {
    "user_id": "11111111-2222-3333-4444-555555555555",
    "name": "Ravi Kumar",
    "email": "ravi.kumar@example.com"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "22222222-3333-4444-5555-666666666666",
    "user_id": "11111111-2222-3333-4444-555555555555",
    "name": "Ravi Kumar",
    "email": "ravi.kumar@example.com"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "User not found"}`
  - `409 Conflict`: `{"detail": "Student profile already exists for this user"}`
  - `409 Conflict`: `{"detail": "Email already registered for another student"}`

### 4.2 List Students
- **METHOD:** `GET`
- **PATH:** `/api/v1/students`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "22222222-3333-4444-5555-666666666666",
      "user_id": "11111111-2222-3333-4444-555555555555",
      "name": "Ravi Kumar",
      "email": "ravi.kumar@example.com"
    }
  ]
  ```

---

## 5. Scholarships Catalogue

### 5.1 List Schemes
- **METHOD:** `GET`
- **PATH:** `/api/v1/scholarships`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "00000000-0000-0000-0000-000000000010",
      "code": "POST_MATRIC",
      "name": "Post-Matric Scholarship"
    },
    {
      "id": "00000000-0000-0000-0000-000000000011",
      "code": "PRE_MATRIC",
      "name": "Pre-Matric Scholarship"
    }
  ]
  ```
- **NOTE ON ELIGIBILITY:** Per team contract decisions (`docs/api/scholarships.md`), `eligible` is intentionally separate from static catalogue persistence and is evaluated on-demand via the Eligibility endpoint.

---

## 6. Eligibility Evaluation

### 6.1 Check Scheme Eligibility
- **METHOD:** `POST`
- **PATH:** `/api/v1/eligibility/check`
- **REQUEST:**
  ```json
  {
    "student_id": "22222222-3333-4444-5555-666666666666",
    "scholarship_id": "00000000-0000-0000-0000-000000000010"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "student_id": "22222222-3333-4444-5555-666666666666",
    "scholarship_id": "00000000-0000-0000-0000-000000000010",
    "eligible": true,
    "reasons": [
      "Mock eligibility evaluation only; official scheme rules are not configured"
    ],
    "evaluation_mode": "MOCK"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Student not found"}`
  - `404 Not Found`: `{"detail": "Scholarship not found"}`
- **NOTE:** Current evaluation runs the mock evaluator; official government policy rules have not been configured yet.

---

## 7. Applications & Document Linking

### 7.1 Create Application
- **METHOD:** `POST`
- **PATH:** `/api/v1/applications`
- **REQUEST:**
  ```json
  {
    "student_id": "22222222-3333-4444-5555-666666666666",
    "scholarship_id": "00000000-0000-0000-0000-000000000010"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "33333333-4444-5555-6666-777777777777",
    "student_id": "22222222-3333-4444-5555-666666666666",
    "scholarship_id": "00000000-0000-0000-0000-000000000010",
    "status": "DRAFT"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Student not found"}`
  - `404 Not Found`: `{"detail": "Scholarship not found"}`

### 7.2 List Applications
- **METHOD:** `GET`
- **PATH:** `/api/v1/applications`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "33333333-4444-5555-6666-777777777777",
      "student_id": "22222222-3333-4444-5555-666666666666",
      "scholarship_id": "00000000-0000-0000-0000-000000000010",
      "status": "DRAFT"
    }
  ]
  ```

### 7.3 Link Document to Application
- **METHOD:** `POST`
- **PATH:** `/api/v1/applications/{application_id}/documents`
- **REQUEST:**
  ```json
  {
    "document_id": "44444444-5555-6666-7777-888888888888"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "application_id": "33333333-4444-5555-6666-777777777777",
    "document_id": "44444444-5555-6666-7777-888888888888"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Application not found"}`
  - `404 Not Found`: `{"detail": "Document not found"}`
  - `409 Conflict`: `{"detail": "Document does not belong to application student"}`
  - `409 Conflict`: `{"detail": "Document already linked to application"}`

### 7.4 List Documents Attached to Application
- **METHOD:** `GET`
- **PATH:** `/api/v1/applications/{application_id}/documents`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "44444444-5555-6666-7777-888888888888",
      "student_id": "22222222-3333-4444-5555-666666666666",
      "document_type": "MOCK_ST_CERTIFICATE",
      "document_name": "ST Certificate",
      "status": "PENDING"
    }
  ]
  ```

---

## 8. Documents Repository

### 8.1 Register Document Metadata
- **METHOD:** `POST`
- **PATH:** `/api/v1/documents`
- **REQUEST:**
  ```json
  {
    "student_id": "22222222-3333-4444-5555-666666666666",
    "document_type": "MOCK_ST_CERTIFICATE",
    "document_name": "ST Certificate"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "44444444-5555-6666-7777-888888888888",
    "student_id": "22222222-3333-4444-5555-666666666666",
    "document_type": "MOCK_ST_CERTIFICATE",
    "document_name": "ST Certificate",
    "status": "PENDING"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Student not found"}`

### 8.2 List Registered Documents
- **METHOD:** `GET`
- **PATH:** `/api/v1/documents`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "44444444-5555-6666-7777-888888888888",
      "student_id": "22222222-3333-4444-5555-666666666666",
      "document_type": "MOCK_ST_CERTIFICATE",
      "document_name": "ST Certificate",
      "status": "PENDING"
    }
  ]
  ```

---

## 9. DigiLocker (Simulated Adapter)

### 9.1 Browse Mock DigiLocker Certificates
- **METHOD:** `GET`
- **PATH:** `/api/v1/students/{student_id}/digilocker/documents`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
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

### 9.2 Import Mock Certificate to Student Documents
- **METHOD:** `POST`
- **PATH:** `/api/v1/students/{student_id}/digilocker/documents/import`
- **REQUEST:**
  ```json
  {
    "document_type": "MOCK_ST_CERTIFICATE"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "44444444-5555-6666-7777-888888888888",
    "student_id": "22222222-3333-4444-5555-666666666666",
    "document_type": "MOCK_ST_CERTIFICATE",
    "document_name": "ST Certificate",
    "status": "PENDING"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Student not found"}`
  - `404 Not Found`: `{"detail": "Mock DigiLocker document not found"}`
  - `409 Conflict`: `{"detail": "Mock DigiLocker document already imported"}`

---

## 10. Verification & Manual Review Pipeline

### 10.1 Create Verification Record
- **METHOD:** `POST`
- **PATH:** `/api/v1/applications/{application_id}/verifications`
- **REQUEST:**
  ```json
  {
    "document_id": "44444444-5555-6666-7777-888888888888"
  }
  ```
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "55555555-6666-7777-8888-999999999999",
    "application_id": "33333333-4444-5555-6666-777777777777",
    "document_id": "44444444-5555-6666-7777-888888888888",
    "status": "PENDING"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Application not found"}` / `{"detail": "Document not found"}`
  - `409 Conflict`: `{"detail": "Document is not linked to application"}`
  - `409 Conflict`: `{"detail": "Verification record already exists"}`

### 10.2 List Application Verifications
- **METHOD:** `GET`
- **PATH:** `/api/v1/applications/{application_id}/verifications`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "55555555-6666-7777-8888-999999999999",
      "application_id": "33333333-4444-5555-6666-777777777777",
      "document_id": "44444444-5555-6666-7777-888888888888",
      "status": "PENDING"
    }
  ]
  ```

### 10.3 Execute Verification (Mock Adapter)
- **METHOD:** `POST`
- **PATH:** `/api/v1/verifications/{verification_id}/execute`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "55555555-6666-7777-8888-999999999999",
    "application_id": "33333333-4444-5555-6666-777777777777",
    "document_id": "44444444-5555-6666-7777-888888888888",
    "status": "VERIFIED",
    "message": "Mock document successfully verified against simulated issuer registry",
    "evaluation_mode": "MOCK"
  }
  ```
- **DETERMINISTIC SIMULATION BEHAVIOR:**
  - `document_type == "TEST_VERIFIED"` -> `status: "VERIFIED"`
  - `document_type == "TEST_MISMATCH"` -> `status: "MISMATCH"`
  - `document_type == "TEST_FAILED"` -> `status: "FAILED"`
  - Other document types -> `status: "FAILED"`
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Verification record not found"}`
  - `409 Conflict`: `{"detail": "Verification record is not pending"}`

### 10.4 Enqueue Mismatch for Manual Review
- **METHOD:** `POST`
- **PATH:** `/api/v1/verifications/{verification_id}/manual-review`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  {
    "id": "66666666-7777-8888-9999-000000000000",
    "application_id": "33333333-4444-5555-6666-777777777777",
    "verification_id": "55555555-6666-7777-8888-999999999999",
    "status": "OPEN"
  }
  ```
- **COMMON ERRORS:**
  - `404 Not Found`: `{"detail": "Verification record not found"}`
  - `409 Conflict`: `{"detail": "Verification record is not eligible for manual review"}` (verification status must be `MISMATCH`)
  - `409 Conflict`: `{"detail": "Manual review already exists"}`

### 10.5 List Manual Reviews Queue
- **METHOD:** `GET`
- **PATH:** `/api/v1/manual-reviews`
- **REQUEST:** None
- **RESPONSE (`200 OK`):**
  ```json
  [
    {
      "id": "66666666-7777-8888-9999-000000000000",
      "application_id": "33333333-4444-5555-6666-777777777777",
      "verification_id": "55555555-6666-7777-8888-999999999999",
      "status": "OPEN"
    }
  ]
  ```

---

## 11. Pre-Seeded Development Demo Data
When the database is seeded (`python -m app.seed`), the following test records are deterministically available:

| Entity | ID / Value | Purpose |
| :--- | :--- | :--- |
| **Demo User** | `00000000-0000-0000-0000-000000000001`<br>`demo.student@example.com` / `DemoPassword123!` | Test login & user lookup |
| **Demo Student** | `00000000-0000-0000-0000-000000000002`<br>`Demo Student User` | Attached to Demo User |
| **Scholarships** | `00000000-0000-0000-0000-000000000010` (`POST_MATRIC`)<br>`00000000-0000-0000-0000-000000000011` (`PRE_MATRIC`)<br>`00000000-0000-0000-0000-000000000012` (`NATIONAL_OVERSEAS`)<br>`00000000-0000-0000-0000-000000000013` (`TOP_CLASS_EDUCATION`) | Catalogue browsing & application targets |
| **Application** | `00000000-0000-0000-0000-000000000020`<br>Status: `DRAFT` | Target for document linking and verifications |
| **Documents** | `00000000-0000-0000-0000-000000000030` (`MOCK_ST_CERTIFICATE`)<br>`00000000-0000-0000-0000-000000000031` (`TEST_VERIFIED`)<br>`00000000-0000-0000-0000-000000000032` (`TEST_MISMATCH`) | Document linking & deterministic verification demos |
| **Verification Record** | `00000000-0000-0000-0000-000000000040`<br>Status: `PENDING` | Ready for execution |
