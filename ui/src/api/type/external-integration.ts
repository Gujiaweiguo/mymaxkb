export type ExternalIntegrationState =
  | 'configured'
  | 'ready'
  | 'failed'
  | 'invalid'
  | 'disabled'
  | 'enabled'
  | 'unconfigured'
  | string

export interface ExternalIntegrationReadinessPayload {
  state?: ExternalIntegrationState | null
  failure_reason?: string | null
  is_valid?: boolean
  is_active?: boolean
  is_configured?: boolean
}

export interface ExternalIntegrationPlatformInfo<T = Record<string, any>>
  extends ExternalIntegrationReadinessPayload {
  auth_type?: string
  type?: string
  config?: T
}

export type ExternalIntegrationLegacyStatus = [boolean, boolean]

export interface ExternalIntegrationPlatformStatus extends ExternalIntegrationReadinessPayload {
  exists?: boolean
}
