## Context

The repository has chat-user models, group relationships, resource-chat-user authorization tables, shared-resource UI surfaces, and application/chat pipelines that reference chat-user identity. The X-Pack parity requirement pulls several document pages into one conceptual seam: cross-workspace sharing, chat-user management, and chat-user access to applications and datasets all describe how non-admin actors or non-owning workspaces gain access to protected resources.

The authorization hardening layer (PR #9) fixed a real CE gap: `WORKSPACE_READ` was narrowed from `[ADMIN, USER]` to `[ADMIN]`. This change builds on that foundation.

## Goals / Non-Goals

**Goals:**
- Implement cross-workspace shared-resource behavior for supported resources
- Implement chat-user and chat-user-group management behavior
- Implement application and dataset access control through chat-user and chat-user-group policies
- Implement how application access restriction relates to password or authenticated chat-user access paths

**Non-Goals:**
- System-user identity or administrative RBAC (already covered)
- Workspace ownership or primary resource authority (already covered)
- External connector/channel setup details (future change)
- System branding, audit logging, or system API key behavior

## Decisions

### 1. Follow the same denied-path testing pattern as authorization hardening

**Why this decision:** The authorization hardening approach (denied-path tests first, fix only if tests expose a gap) worked well. Tests found a real CE permission gap and confirmed other endpoints were already correct.

**Alternatives considered:**
- Implement features without tests first. Rejected because the authorization hardening pattern proved its value by catching real gaps.

### 2. Start with chat-user management, then resource access, then shared resources

**Why this decision:** Chat-user management is the foundation — you can't authorize chat users if they don't exist. Resource access builds on chat-user management. Shared resources build on both.

**Alternatives considered:**
- Start with shared resources. Rejected because shared resources depend on authorization, which depends on chat users.

### 3. Use existing model structures, not new tables

**Why this decision:** The repository already has `ChatUser`, `ChatUserGroup`, `ResourceChatUserAuthorization`, `ResourceUserGroupAuthorization`, and `SharedResourceAuthorization` models. Implementation should use these, not create parallel structures.

**Alternatives considered:**
- Create new models. Rejected because it would duplicate existing functionality and create maintenance burden.

## Risks / Trade-offs

- **[Risk] Existing models may have gaps** → **Mitigation:** Test each model's behavior and fix gaps as they're discovered
- **[Risk] Application and dataset access policies may not align perfectly** → **Mitigation:** Define a shared delegated-access contract while allowing resource-specific task breakdown later
- **[Risk] Shared-resource semantics across workspaces may differ by resource type** → **Mitigation:** Keep the core sharing model generic and note any type-specific exceptions in implementation tasks

## Migration Plan

1. Implement chat-user management with denied-path tests
2. Implement resource access with denied-path tests
3. Implement shared resources with denied-path tests
4. Package as a single PR with atomic commits
5. Merge after CI passes

## Open Questions

- Which shared resource types should be included in the first community-edition rollout?
- Should auto-assignment behavior be modeled as part of authorization policy or as a separate onboarding rule?
- Do datasets and applications need different default-deny semantics, or can they share a common protected-access baseline?
