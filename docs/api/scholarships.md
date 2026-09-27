# Scholarship Catalogue

## Endpoint

GET /api/v1/scholarships

## Purpose

Returns the scholarship/scheme catalogue.

## Minimal Scholarship Entity

For the catalogue itself, define only:

- **id**: `string`
  - Internal identifier
  - Backend should use UUIDs for internal IDs
- **code**: `string`
  - Stable scheme code
  - Example from playbook: `POST_MATRIC`
- **name**: `string`
  - Human-readable scheme name
  - Example from playbook: `Post-Matric Scholarship`

Do NOT add any other persistent Scholarship fields.

## Eligibility Separation

- The playbook example/frontend model references an `eligible` boolean.
- However, Eligibility is a separate backend module responsible for rule evaluation and explainable results.
- The playbook does not define `eligible` as a persistent Scholarship database field.
- Therefore `eligible` must NOT be defined as a Scholarship database column in this contract.
- Its final API behavior remains separated until the Eligibility contract is defined.

## Response Shape

### PLAYBOOK EXAMPLE

The playbook Section 11 illustrates an enveloped response format:

```json
{
  "success": true,
  "data": [
    {
      "id": "scheme-1",
      "code": "POST_MATRIC",
      "name": "Post-Matric Scholarship",
      "eligible": true
    }
  ],
  "message": "Request successful",
  "request_id": "req-123"
}
```

### TEAM-APPROVED IMPLEMENTATION CONTRACT

`GET /api/v1/scholarships` returns a direct JSON array of `list[ScholarshipResponse]`:

```json
[
  {
    "id": "<uuid>",
    "code": "POST_MATRIC",
    "name": "Post-Matric Scholarship"
  }
]
```

- This intentionally follows the current backend convention used by `GET /api/v1/students/`.
- The envelope shown in the playbook is an example and is not being adopted for this endpoint at this stage.
- A project-wide response-envelope standard may be introduced later only through an explicit contract change.

## Explicitly Out of Scope / Undefined

The current playbook does NOT define catalogue fields for:
- description
- scheme type
- income limit
- category criteria
- education level
- amount/benefits
- application deadline
- required documents
- portal/source
- active/inactive status

These must not be added without an approved contract change.

Not currently defined by the playbook:
- `GET /api/v1/scholarships/{id}`
- `POST scholarship`
- `PUT/PATCH scholarship`
- `DELETE scholarship`

## Dependencies

- **Eligibility:**
  - Depends on Student + schemes + rules
  - Exact rule structure is not yet defined
- **Applications:**
  - Depend on Student + scheme + documents
  - Applications will eventually need to reference a scheme
  - Exact Application schema is not part of this contract
- **JAGO:**
  - Should use approved internal services such as Eligibility/Application
  - Should not directly depend on Scholarship database internals

## Implementation Status

**Contract status: APPROVED / IMPLEMENTATION-READY**

**Reason:**
The three required contract decisions (Response Shape, `eligible` Behavior, and Persistent Scheme Entity) have been explicitly reviewed and approved by the team.

## Contract Decisions

### Decision 1 — GET /api/v1/scholarships response wrapper

**Status: APPROVED**

**PLAYBOOK EXAMPLE:**
```json
{
  "success": true,
  "data": [
    {
      "id": "scheme-1",
      "code": "POST_MATRIC",
      "name": "Post-Matric Scholarship",
      "eligible": true
    }
  ],
  "message": "Request successful",
  "request_id": "req-123"
}
```

**TEAM-APPROVED IMPLEMENTATION CONTRACT:**
- `GET /api/v1/scholarships` will return a direct JSON array: `list[ScholarshipResponse]`.
- Example:
  ```json
  [
    {
      "id": "<uuid>",
      "code": "POST_MATRIC",
      "name": "Post-Matric Scholarship"
    }
  ]
  ```
- This intentionally follows the current backend convention used by `GET /api/v1/students/`.
- The envelope shown in the playbook is an example and is not being adopted for this endpoint at this stage.
- A project-wide response-envelope standard may be introduced later only through an explicit contract change.

### Decision 2 — `eligible` behavior

**Status: APPROVED**

- `eligible` will NOT be:
  - stored in the `scholarships` database table
  - returned by `GET /api/v1/scholarships` at this stage
  - hardcoded or mocked by the catalogue service
- The catalogue endpoint will currently return only:
  - `id`
  - `code`
  - `name`
- Notes:
  - The playbook examples include `eligible`.
  - This implementation intentionally defers `eligible` until the Eligibility module contract is defined.
  - Student-specific eligibility will be handled by the Eligibility module rather than persisted as static Scholarship catalogue data.
  - Adding `eligible` to catalogue responses later requires an explicit contract update.

### Decision 3 — Persistent Scheme Entity

**Status: APPROVED**

**TEAM-APPROVED IMPLEMENTATION CONTRACT:**
- Minimal PostgreSQL table: `scholarships`
- Approved columns:
  - `id`: `String`, UUID generated internally, `PRIMARY KEY`, `NOT NULL`
  - `code`: `String`, `UNIQUE`, `NOT NULL`
  - `name`: `String`, `NOT NULL`
- No additional Scholarship fields are approved.

### Implementation Gate

The three required contract decisions (Decision 1, Decision 2, and Decision 3) have now been approved, and backend implementation may begin against this documented contract.
