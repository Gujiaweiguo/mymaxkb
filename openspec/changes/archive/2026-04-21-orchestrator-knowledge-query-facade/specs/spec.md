## Purpose

Define the external contract and behavior requirements for the Orchestrator-facing knowledge query facade.

## Requirements

### Requirement: Single-request knowledge QA endpoint

The system MUST expose `POST /api/knowledge/query` that completes knowledge QA in a single request without requiring upstream awareness of chat_id, anonymous tokens, or MCP protocol details.

#### Scenario: Valid query returns stable success contract

- **GIVEN** a valid `ApplicationApiKey` bearer token
- **AND** a request body with `question` (required) and optional `session_id`, `request_id`, `trace_id`, `context`, `params`
- **WHEN** `POST /api/knowledge/query` is called with `_param_preview=false` or omitted
- **THEN** the response contains `text` (string), `references` (array), `suggestions` (array), `cards` (array), `meta` (object with `chat_id`, `tokens_used`, `hit_paragraph_count`)

#### Scenario: All success contract arrays are present even when empty

- **GIVEN** a valid query that produces no retrieval hits
- **WHEN** the response is returned
- **THEN** `references` is `[]`, `suggestions` is `[]`, `cards` is `[]`, and `meta.hit_paragraph_count` is `0`

### Requirement: ApplicationApiKey authentication

The system MUST authenticate Orchestrator requests using `ApplicationApiKey.secret_key` as a Bearer token.

#### Scenario: Valid API key authenticates successfully

- **GIVEN** an active `ApplicationApiKey` for an application
- **WHEN** the request includes `Authorization: Bearer <secret_key>`
- **THEN** the request is bound to that application and proceeds

#### Scenario: Invalid or revoked API key is rejected

- **GIVEN** a disabled, revoked, or nonexistent API key
- **WHEN** the request includes `Authorization: Bearer <invalid_key>`
- **THEN** the response is a structured error with `error_code: "UNAUTHORIZED"`

### Requirement: Redis-backed session continuity with binding validation

The system MUST maintain `session_id -> chat_id` mappings in Redis with TTL, bound to application identity and caller context.

#### Scenario: Same session_id reuses same chat context

- **GIVEN** a valid session binding exists for `session_id` under the same application and caller identity
- **WHEN** a follow-up request arrives with the same `session_id`
- **THEN** the same internal `chat_id` is reused and TTL is refreshed

#### Scenario: Session mismatch is rejected

- **GIVEN** a session binding exists under one application/API key
- **WHEN** a request arrives with the same `session_id` but different API key or caller identity
- **THEN** the response is a structured error with `error_code: "SESSION_MISMATCH"`

#### Scenario: Expired session creates fresh binding

- **GIVEN** a session binding has expired (TTL elapsed)
- **WHEN** a request arrives with that `session_id`
- **THEN** a new internal chat is created and a fresh binding is stored

### Requirement: Structured references from actual retrieval evidence

References MUST be derived from the actual retrieval artifacts used by the answer path, not reconstructed from unrelated state.

#### Scenario: References map to real paragraph hits

- **GIVEN** the answer path retrieved N paragraph hits
- **WHEN** the response is assembled
- **THEN** each reference contains at least `title` and `snippet`, and `meta.hit_paragraph_count` equals N

#### Scenario: References are empty when no hits found

- **GIVEN** the answer path found zero relevant paragraphs
- **WHEN** the response is assembled
- **THEN** `references` is `[]` and `meta.hit_paragraph_count` is `0`

### Requirement: Non-template suggestions with conservative fallback

Suggestions MUST be strongly related to the current answer context. Generic templates are prohibited.

#### Scenario: High-confidence suggestions are returned

- **GIVEN** sufficient retrieval and answer context for generating follow-up questions
- **WHEN** the response is assembled
- **THEN** `suggestions` contains 2-4 contextually relevant next questions

#### Scenario: Low-confidence degrades to empty array

- **GIVEN** insufficient context for quality suggestions
- **WHEN** the response is assembled
- **THEN** `suggestions` is `[]` rather than generic filler

### Requirement: Parameter preview with zero side effects

When `params._param_preview=true`, the system MUST return only `param_schema` without creating chat state, mutating session cache, or invoking the answer pipeline.

#### Scenario: Preview returns schema only

- **GIVEN** a valid authenticated request with `_param_preview=true`
- **WHEN** the response is returned
- **THEN** it contains only `param_schema` with `kb_scope`, `top_n`, `similarity` controls
- **AND** it does NOT contain `text`, `references`, `suggestions`, `cards`, or `meta`

#### Scenario: Preview creates no side effects

- **GIVEN** a preview-mode request
- **WHEN** it completes
- **THEN** no new chat record exists, no session cache entry was created or modified, and no LLM was invoked

### Requirement: Admin integration parameter output

The admin backend MUST expose an endpoint that returns Orchestrator-ready integration parameters.

#### Scenario: Integration config is returned

- **GIVEN** an application with an active API key and mapped knowledge bases
- **WHEN** the admin integration endpoint is called
- **THEN** the response contains `endpoint_url`, `auth_token`, and `default_params` (`kb_scope`, `top_n`, `similarity`)

#### Scenario: Missing API key is auto-generated

- **GIVEN** an application with no active API key
- **WHEN** the admin integration endpoint is called
- **THEN** a new `ApplicationApiKey` is created and its secret is returned in `auth_token`

### Requirement: Structured error responses

All error cases MUST return JSON with `error_code` and `message`. Standardized error codes: `INVALID_REQUEST`, `UNAUTHORIZED`, `SESSION_MISMATCH`, `KNOWLEDGE_SCOPE_INVALID`, `INTERNAL_ERROR`.

#### Scenario: Invalid request returns structured error

- **GIVEN** a request missing required `question` field
- **WHEN** the endpoint processes it
- **THEN** the response contains `{"error_code": "INVALID_REQUEST", "message": "..."}`

#### Scenario: Invalid kb_scope returns structured error

- **GIVEN** a request with `kb_scope` containing values not mapped to the application
- **WHEN** the endpoint processes it
- **THEN** the response contains `{"error_code": "KNOWLEDGE_SCOPE_INVALID", "message": "..."}`
