# Application Documents Linking API Contract

## 1. Playbook-Defined Requirements

The following requirements are explicitly mandated by the **TribalSetu Team Development & Integration Playbook**:

### Core Reusability Rule
> *"Documents are reusable student assets; application_documents links them to applications."* (Playbook Section 15, Rule 127)

### Mandated Architectural Principles
- **Asset Reusability:** Documents belong to the student profile and must NOT contain `application_id` directly in their database schema.
- **Junction Mechanism:** A reusable student document is associated with a specific scholarship application exclusively through the `application_documents` junction layer.
- **Many-to-Many Potential:** A student may attach the same verified document across multiple distinct scholarship applications over time.
- **Internal IDs:** UUID strings are the project-wide standard for internal identifiers.

---

## 2. Team-Approved Phase-1 Contract

The following decisions are **TEAM-APPROVED** for the minimal Phase-1 linking implementation, and must not be confused with playbook-defined requirements.

### Scope & Deferred Features
- **Minimal Association Only:** Phase 1 implements only the association link between an application and a document.
- **No Extra Junction Metadata:** Status, timestamps, verification metadata, and document types are NOT stored on the junction table in Phase 1.
- **Unlinking Deferred:** Delete/unlink endpoints are deferred.
- **Submission Trigger Deferred:** Linking documents is an independent metadata step before formal application submission.

### Database Table: `application_documents`

```sql
CREATE TABLE application_documents (
    application_id VARCHAR NOT NULL REFERENCES applications(id),
    document_id VARCHAR NOT NULL REFERENCES documents(id),
    PRIMARY KEY (application_id, document_id)
);
```

#### Columns ONLY:
- **`application_id`**: `String`, `FOREIGN KEY -> applications.id`, `NOT NULL`
- **`document_id`**: `String`, `FOREIGN KEY -> documents.id`, `NOT NULL`
- **Primary Key**: Composite primary key `(application_id, document_id)`

*Explicitly Excluded:*
- Extra surrogate `id` column
- `status`
- `created_at` / timestamps
- Verification check fields
- `student_id` (enforced via foreign relations)

---

### Endpoints

#### 1. Link Document to Application: `POST /api/v1/applications/{application_id}/documents`

##### Request Payload
```json
{
  "document_id": "<document-uuid>"
}
```

##### Validation & Business Logic
1. Validate that `application_id` exists in `applications`. If missing -> `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
2. Validate that `document_id` exists in `documents`. If missing -> `HTTP 404 Not Found` (`{"detail": "Document not found"}`).
3. **Student Ownership Validation:** Verify that `document.student_id == application.student_id`. A student cannot attach another student's document to their application. If mismatched -> `HTTP 409 Conflict` (`{"detail": "Document does not belong to application student"}`).
4. **Duplicate Validation:** Verify that `(application_id, document_id)` link does not already exist. If duplicate -> `HTTP 409 Conflict` (`{"detail": "Document already linked to application"}`).
5. Persist link to `application_documents`.

##### Success Response (`HTTP 200 OK`)
```json
{
  "application_id": "<application-uuid>",
  "document_id": "<document-uuid>"
}
```

---

#### 2. List Linked Documents: `GET /api/v1/applications/{application_id}/documents`

##### Validation & Business Logic
1. Validate that `application_id` exists in `applications`. If missing -> `HTTP 404 Not Found` (`{"detail": "Application not found"}`).
2. Query and return all `documents` linked via `application_documents`.

##### Success Response (`HTTP 200 OK`)
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
- Direct JSON array of `DocumentResponse` objects.
- Empty array `[]` if application has no documents linked yet.
