## Context

The repository already has chat-user models, group relationships, resource-chat-user authorization tables, shared-resource UI surfaces, and application/chat pipelines that reference chat-user identity. The X-Pack parity requirement pulls several document pages into one conceptual seam: cross-workspace sharing, chat-user management, and chat-user access to applications and datasets all describe how non-admin actors or non-owning workspaces gain access to protected resources.

This change therefore sits on top of the identity foundation and the workspace/ownership model. It does not define primary administrative authority; it defines delegated or external-facing access once ownership is already known.

## Goals / Non-Goals

**Goals:**
- Define cross-workspace shared-resource behavior for supported resources.
- Define chat-user and chat-user-group management behavior.
- Define application and dataset access control through chat-user and chat-user-group policies.
- Define how application access restriction relates to password or authenticated chat-user access paths.

**Non-Goals:**
- Defining system-user identity or administrative RBAC.
- Defining workspace ownership or primary resource authority.
- Defining external connector/channel setup details.
- Defining system branding, audit logging, or system API key behavior.

## Decisions

### 1. Shared resources and chat-user access are planned together as delegated access

This change treats shared workspaces, chat users, and chat-user groups as delegated or downstream access paths layered on top of primary ownership.

**Why this decision:** these features all answer the same planning question: who may access a resource when they are not simply the owning admin actor inside the owning workspace?

**Alternatives considered:**
- Split shared resources and chat-user access into separate changes. Rejected because both rely on the same delegated-access vocabulary and would create duplicated planning.

### 2. Application access restriction belongs here instead of the identity foundation

Password-protected or authenticated application access is defined here because it governs resource entry for chat-facing actors rather than administrative sign-in.

**Why this decision:** it depends on chat-user and resource-access rules, not on admin login semantics.

**Alternatives considered:**
- Put application access restriction into the identity foundation. Rejected because that would mix admin authentication with chat-facing access control.

### 3. Group-based authorization is a first-class planning concept

This change assumes that user groups are not just a UI convenience; they are a primary way to express chat-user authorization at scale.

**Why this decision:** the existing models and UI surfaces already distinguish chat users and chat-user groups, and the X-Pack docs rely on group-based management.

**Alternatives considered:**
- Treat group authorization as an implementation detail. Rejected because the product behavior changes materially when policies can target groups.

## Risks / Trade-offs

- **[Risk] Application and dataset access policies may not align perfectly** → **Mitigation:** define a shared delegated-access contract while allowing resource-specific task breakdown later.
- **[Risk] Shared-resource semantics across workspaces may differ by resource type** → **Mitigation:** keep the core sharing model generic and note any type-specific exceptions in implementation tasks rather than redefining the contract.
- **[Risk] Password-based access and authenticated access could become overlapping policy systems** → **Mitigation:** define them as alternative entry-control modes under one access-restriction capability.

## Migration Plan

1. Define chat-user and user-group lifecycle requirements.
2. Define delegated access rules for applications, datasets, and shared workspaces.
3. Align application access restriction with the delegated-access model.
4. Reuse the ownership model from the prior change instead of redefining resource authority.

## Handoff to `external-integrations`

The follow-on integration change should reuse the delegated-access foundation from this change instead of redefining provider-facing identity or resource authorization semantics.

### Provider and access prerequisites to reuse

1. **Chat-user identity surfaces**
   - `apps/system_manage/models/chat_user.py`
   - `apps/application/models/application_chat.py`

   `ChatUser.source` remains the canonical origin marker for external identities, while `ChatUserType` and `ChatSourceChoices` remain the canonical actor/channel classification surfaces for downstream integrations.

2. **Authentication token contract**
   - `apps/common/constants/authentication_type.py`
   - `apps/common/auth/common.py`
   - `apps/common/auth/handle/impl/chat_anonymous_user_token.py`
   - `apps/common/auth/handle/impl/application_key.py`
   - `apps/application/models/application_access_token.py`

   `ChatAuthentication`, `ChatUserToken`, and `ApplicationAccessToken.authentication_value` define the existing auth payload and token contract that external channel integrations should extend or configure, rather than replace with parallel token models.

3. **Delegated resource access contract**
   - `apps/system_manage/models/shared_resource_authorization.py`
   - `apps/system_manage/models/chat_user.py`
   - `apps/common/utils/shared_resource_auth.py`
   - `apps/application/api/application_chat_user_authorize.py`
   - `apps/knowledge/api/knowledge_chat_user_authorize.py`

   Shared-resource authorization, resource chat-user/group authorization, and canonical filter helpers are already defined here. `external-integrations` should consume these as preconditions when an external provider grants access to an application or dataset.

4. **Permission and role vocabulary**
   - `apps/common/constants/permission_constants.py`

   Existing role and operate constants, including channel-oriented operate names such as Feishu, DingTalk, WeCom, WeChat public account, and Slack, should be treated as the permission vocabulary baseline rather than reintroduced in connector-specific form.

### What belongs to `external-integrations` instead

- Provider credential forms and validation
- Callback and webhook endpoints
- Connector readiness and partial-configuration states
- Feishu document import/sync execution semantics
- Provider-specific error handling and retry behavior

## Open Questions

- Which shared resource types should be included in the first community-edition rollout?
- Should auto-assignment behavior be modeled as part of authorization policy or as a separate onboarding rule?
- Do datasets and applications need different default-deny semantics, or can they share a common protected-access baseline?
