import { randomUUID } from 'node:crypto'

const E2E_PREFIX = 'E2E'

export function uniqueId(prefix = ''): string {
  const uuid = randomUUID().slice(0, 8)
  return prefix ? `${prefix}-${uuid}` : uuid
}

export function uniqueName(baseName: string): string {
  return `${E2E_PREFIX} ${baseName} ${randomUUID().slice(0, 8)}`
}

export function uniqueUsername(baseUsername = 'testuser'): string {
  return `${baseUsername}_${randomUUID().slice(0, 8)}`
}

export function uniqueEmail(baseEmail = 'testuser'): string {
  return `${baseEmail}_${randomUUID().slice(0, 8)}@e2e.test`
}

export function uniqueWorkspaceName(): string {
  return uniqueName('Workspace')
}

export function uniqueApplicationName(): string {
  return uniqueName('Application')
}

export function uniqueKnowledgeName(): string {
  return uniqueName('Knowledge')
}

export function uniqueModelName(): string {
  return uniqueName('Model')
}

export function uniqueChatAppName(): string {
  return uniqueName('Chat App')
}

export function uniqueDocumentName(): string {
  return uniqueName('Document')
}

export function timestampSuffix(): string {
  return Date.now().toString(36)
}

export type TrackedResource = {
  type: 'user' | 'workspace' | 'application' | 'knowledge' | 'model' | 'document'
  id: string
  name?: string
}

export class ResourceTracker {
  private resources: TrackedResource[] = []

  track(resource: TrackedResource): void {
    this.resources.push(resource)
  }

  getByType(type: TrackedResource['type']): TrackedResource[] {
    return this.resources.filter((r) => r.type === type)
  }

  getAll(): TrackedResource[] {
    return [...this.resources]
  }

  clear(): void {
    this.resources = []
  }

  get count(): number {
    return this.resources.length
  }
}
