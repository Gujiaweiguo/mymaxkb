<template>
  <div v-loading="loading" class="scan-height">
    <el-scrollbar>
      <div v-for="item in platforms" :key="item.key" class="mb-16">
        <el-card class="border-none mb-16" shadow="never">
          <div class="flex-between">
            <div>
              <div class="flex align-center">
                <img :src="item.logoSrc" alt="" width="24px" />
                <h5 class="ml-8">{{ item.name }}</h5>
                <el-tag size="small" type="info" effect="plain" class="ml-8">
                  {{ $t(item.isConfigured ? 'common.status.configured' : 'common.status.unconfigured') }}
                </el-tag>
                <el-tag
                  v-if="item.isConfigured"
                  size="small"
                  :type="getReadinessTagType(item)"
                  class="ml-8"
                >
                  {{ getReadinessLabel(item) }}
                </el-tag>
              </div>
              <div v-if="showFailureReason(item)" class="mt-8">
                <el-text type="danger" size="small">
                  {{ `${$t('common.reason')}: ${item.failureReason}` }}
                </el-text>
              </div>
            </div>
            <div>
              <el-button type="primary" v-if="!item.isConfigured" @click="showDialog(item)"
                >{{ $t('views.system.authentication.scanTheQRCode.access') }}
              </el-button>
              <span v-else>
                <span class="mr-4">{{ getActivationLabel(item) }}</span>
                <el-switch
                  size="small"
                  v-model="item.isActive"
                  :disabled="!canTogglePlatform(item)"
                  @change="changeStatus(item)"
                />
              </span>
            </div>
          </div>
          <el-collapse-transition>
            <div v-if="item.isConfigured" class="border-t mt-16">
              <el-row :gutter="12" class="mt-16">
                <el-col v-for="(value, key) in item.config" :key="key" :span="12">
                  <el-text class="color-secondary lighter">{{ formatFieldName(key, item) }}</el-text>
                  <div class="mt-4 mb-16 flex align-center">
                    <span
                      v-if="key !== 'app_secret'"
                      class="vertical-middle lighter break-all ellipsis-1"
                      >{{ value }}</span
                    >
                    <span
                      v-if="key === 'app_secret' && !showPassword[item.key]?.[key]"
                      class="vertical-middle lighter break-all ellipsis-1"
                      >************</span
                    >
                    <span
                      v-if="key === 'app_secret' && showPassword[item.key]?.[key]"
                      class="vertical-middle lighter break-all ellipsis-1"
                      >{{ value }}</span
                    >
                    <span>
                      <el-button type="primary" text @click="() => copyClick(value)">
                        <AppIcon iconName="app-copy" />
                      </el-button>
                    </span>

                    <span class="ml-4">
                      <el-button
                        v-if="key === 'app_secret'"
                        type="primary"
                        text
                        @click="toggleShowPassword(item.key)"
                      >
                        <AppIcon
                          iconName="app-password-hide"
                          v-if="key === 'app_secret' && !showPassword[item.key]?.[key]"
                        />

                        <el-icon v-if="key === 'app_secret' && showPassword[item.key]?.[key]">
                          <View />
                        </el-icon> </el-button
                    ></span>
                  </div>
                </el-col>
              </el-row>
              <el-button type="primary" @click="showDialog(item)">
                {{ $t('common.edit') }}
              </el-button>
              <el-button @click="validateConnection(item)">
                {{ $t('views.system.authentication.scanTheQRCode.validate') }}
              </el-button>
            </div>
          </el-collapse-transition>
        </el-card>
      </div>
      <EditModel ref="EditModelRef" @refresh="refresh" />
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { copyClick } from '@/utils/clipboard'
import EditModel from './EditModal.vue'
import platformApi from '@/api/chat-user/auth-setting.ts'
import type { ExternalIntegrationPlatformInfo } from '@/api/type/external-integration'
import { MsgError, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'

interface PlatformConfig {
  [key: string]: string
}

interface Platform {
  key: string
  logoSrc: string
  name: string
  isActive: boolean
  isValid: boolean
  isConfigured: boolean
  state: string
  failureReason: string
  config: PlatformConfig
}

const readinessPlatformKeys = new Set(['wecom', 'dingtalk', 'lark'])
const readyStates = new Set(['ready', 'enabled', 'active', 'valid', 'success'])
const failedStates = new Set(['failed', 'invalid', 'error'])

const EditModelRef = ref()
const loading = ref(false)
const platforms = reactive<Platform[]>(initializePlatforms())
const showPassword = reactive<{ [platformKey: string]: { [key: string]: boolean } }>({})

onMounted(() => {
  getPlatformInfo()
})

function initializePlatforms(): Platform[] {
  return [
    createPlatform('wecom', t('views.system.authentication.scanTheQRCode.wecom')),
    createPlatform('dingtalk', t('views.system.authentication.scanTheQRCode.dingtalk')),
    createPlatform('lark', t('views.system.authentication.scanTheQRCode.lark')),
  ]
}

function createPlatform(key: string, name: string): Platform {
  let logo = ''
  switch (key) {
    case 'wecom':
      logo = 'wechat-work'
      break
    case 'dingtalk':
      logo = 'dingtalk'
      break
    case 'lark':
      logo = 'lark'
      break
    default:
      logo = '' // 默认值
      break
  }

  const config = {
    ...(key === 'wecom' ? { corp_id: '', agent_id: '' } : { app_key: '' }),
    app_secret: '',
    callback_url: '',
  }

  return {
    key,
    logoSrc: new URL(`../../../../assets/logo/logo_${logo}.svg`, import.meta.url).href,
    name,
    isActive: false,
    isValid: false,
    isConfigured: false,
    state: '',
    failureReason: '',
    config,
  }
}

function formatFieldName(key?: any, item?: Platform): string {
  const fieldNames: { [key: string]: string } = {
    corp_id: 'Corp ID',
    app_key: item?.key != 'lark' ? 'APP Key' : 'App ID',
    app_secret: 'APP Secret',
    agent_id: 'Agent ID',
    callback_url: t('views.application.applicationAccess.callback'),
  }
  return (
    fieldNames[key as keyof typeof fieldNames] ||
    (key ? key.charAt(0).toUpperCase() + key.slice(1) : '')
  )
}

function getPlatformInfo() {
  loading.value = true
  platformApi.getPlatformInfo(loading).then((res: any) => {
    if (res) {
      platforms.forEach((platform) => {
        const data = res.data.find(
          (item: ExternalIntegrationPlatformInfo<PlatformConfig>) => item.auth_type === platform.key,
        )
        if (data) {
          applyPlatformInfo(platform, data)
          showPassword[platform.key] = {}
          showPassword[platform.key]['app_secret'] = false
        }
      })
    }
  })
}

function validateConnection(currentPlatform: Platform) {
  platformApi.validateConnection(currentPlatform, loading).then((res: any) => {
    if (typeof res.data === 'object' && res.data !== null) {
      applyPlatformInfo(currentPlatform, res.data)
    } else if (typeof res.data === 'boolean') {
      currentPlatform.isValid = res.data
      currentPlatform.state = res.data ? 'ready' : currentPlatform.state
      currentPlatform.failureReason = res.data ? '' : currentPlatform.failureReason
    }

    if (resolveValidationResult(res.data)) {
      MsgSuccess(t('views.system.authentication.scanTheQRCode.validateSuccess'))
    } else {
      MsgError(t('views.system.authentication.scanTheQRCode.validateFailed'))
    }
  })
}

function refresh() {
  getPlatformInfo()
}

function changeStatus(currentPlatform: Platform) {
  platformApi.updateConfig(currentPlatform, loading).then((res: any) => {
    MsgSuccess(t('common.saveSuccess'))
  })
}

function applyPlatformInfo(
  platform: Platform,
  data: ExternalIntegrationPlatformInfo<PlatformConfig>,
) {
  const config = normalizePlatformConfig(platform.key, data.config)
  const state = normalizeState(data.state)
  const isConfigured =
    typeof data.is_configured === 'boolean' ? data.is_configured : hasConfiguredValue(config)

  Object.assign(platform, {
    isConfigured,
    isValid:
      typeof data.is_valid === 'boolean'
        ? data.is_valid
        : state
          ? readyStates.has(state)
          : isConfigured,
    isActive: typeof data.is_active === 'boolean' ? data.is_active : platform.isActive,
    state,
    failureReason: typeof data.failure_reason === 'string' ? data.failure_reason : '',
    config,
  })
}

function normalizePlatformConfig(key: string, config?: PlatformConfig) {
  const nextConfig = {
    ...createPlatform(key, '').config,
    ...(config || {}),
  }

  if (key === 'dingtalk') {
    const { corp_id, app_key, app_secret } = nextConfig
    return {
      corp_id,
      app_key,
      app_secret,
      callback_url: nextConfig.callback_url,
    }
  }

  return nextConfig
}

function hasConfiguredValue(config: PlatformConfig) {
  return Object.entries(config).some(
    ([field, value]) => field !== 'callback_url' && String(value ?? '').trim().length > 0,
  )
}

function normalizeState(state?: string | null) {
  return typeof state === 'string' ? state.toLowerCase() : ''
}

function resolveValidationResult(data: ExternalIntegrationPlatformInfo<PlatformConfig> | boolean) {
  if (typeof data === 'boolean') {
    return data
  }

  const state = normalizeState(data?.state)
  if (typeof data?.is_valid === 'boolean') {
    return data.is_valid
  }

  return state
    ? readyStates.has(state)
    : typeof data?.is_configured === 'boolean'
      ? data.is_configured
      : hasConfiguredValue(data?.config || {})
}

function getReadinessLabel(platform: Platform) {
  if (platform.isValid) {
    return t('common.status.ready')
  }

  return t(hasFailedState(platform) ? 'common.status.fail' : 'common.status.notReady')
}

function getReadinessTagType(platform: Platform) {
  if (platform.isValid) {
    return 'success'
  }

  return hasFailedState(platform) ? 'danger' : 'warning'
}

function hasFailedState(platform: Platform) {
  return Boolean(platform.failureReason) || failedStates.has(platform.state)
}

function showFailureReason(platform: Platform) {
  return platform.isConfigured && !platform.isValid && Boolean(platform.failureReason)
}

function canTogglePlatform(platform: Platform) {
  return platform.isConfigured && (!readinessPlatformKeys.has(platform.key) || platform.isValid)
}

function getActivationLabel(platform: Platform) {
  if (platform.isActive) {
    return t('common.status.enabled')
  }

  if (canTogglePlatform(platform)) {
    return t('common.status.disabled')
  }

  return t('common.status.notReady')
}

function toggleShowPassword(platformKey: string) {
  if (!showPassword[platformKey]) {
    showPassword[platformKey] = {}
  }
  showPassword[platformKey]['app_secret'] = !showPassword[platformKey]['app_secret']
}

function showDialog(platform: Platform) {
  EditModelRef.value?.open(platform)
}
</script>

<style lang="scss" scoped>
.scan-height {
  height: calc(100vh - var(--app-header-height) - var(--app-view-padding) * 2 - 70px);
}
</style>
