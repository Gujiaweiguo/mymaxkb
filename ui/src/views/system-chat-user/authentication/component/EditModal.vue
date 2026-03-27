template
<template>
  <el-drawer
    v-model="visible"
    size="60%"
    :append-to-body="true"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <h4>
          {{ currentPlatform.name + $t('views.system.authentication.scanTheQRCode.setting') }}
        </h4>
      </div>
    </template>

    <el-form
      :model="currentPlatform.config"
      label-width="120px"
      label-position="top"
      require-asterisk-position="right"
      ref="formRef"
    >
      <div class="mb-16" v-if="currentPlatform.key">
        <div class="flex align-center flex-wrap gap-8">
          <el-tag size="small" type="info" effect="plain">
            {{ $t(currentPlatform.isConfigured ? 'common.status.configured' : 'common.status.unconfigured') }}
          </el-tag>
          <el-tag
            v-if="currentPlatform.isConfigured"
            size="small"
            :type="getReadinessTagType()"
          >
            {{ getReadinessLabel() }}
          </el-tag>
        </div>
        <div v-if="showFailureReason" class="mt-8">
          <el-text type="danger" size="small">
            {{ `${$t('common.reason')}: ${currentPlatform.failureReason}` }}
          </el-text>
        </div>
      </div>
      <el-form-item
        v-for="(value, key) in currentPlatform.config"
        :key="key"
        :label="formatFieldName(key)"
        :prop="key"
        :rules="getValidationRules(key)"
      >
        <el-input
          v-model="currentPlatform.config[key]"
          :type="isPasswordField(key) ? 'password' : 'text'"
          :show-password="isPasswordField(key)"
        >
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
        <el-button @click="validateConnection">{{
          $t('views.system.authentication.scanTheQRCode.validate')
        }}</el-button>
        <el-button type="primary" @click="validateForm">{{ $t('common.save') }}</el-button>
      </span>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElForm } from 'element-plus'
import platformApi from '@/api/chat-user/auth-setting.ts'
import type { ExternalIntegrationPlatformInfo } from '@/api/type/external-integration'
import { MsgError, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { getChatApiBaseUrl } from '@/utils/common'

const visible = ref(false)
const loading = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

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

const readyStates = new Set(['ready', 'enabled', 'active', 'valid', 'success'])
const failedStates = new Set(['failed', 'invalid', 'error'])

const currentPlatform = reactive<Platform>({
  key: '',
  logoSrc: '',
  name: '',
  isActive: false,
  isValid: false,
  isConfigured: false,
  state: '',
  failureReason: '',
  config: {},
})

const showFailureReason = computed(
  () => currentPlatform.isConfigured && !currentPlatform.isValid && Boolean(currentPlatform.failureReason),
)

const formatFieldName = (key?: any): string => {
  const fieldNames: { [key: string]: string } = {
    corp_id: 'Corp ID',
    app_key: currentPlatform?.key != 'lark' ? 'APP Key' : 'App ID',
    app_secret: 'APP Secret',
    agent_id: 'Agent ID',
    callback_url: t('views.application.applicationAccess.callback'),
  }
  return (
    fieldNames[key as keyof typeof fieldNames] ||
    (key ? key.charAt(0).toUpperCase() + key.slice(1) : '')
  )
}

const getValidationRules = (key: any) => {
  switch (key) {
    case 'app_key':
      return [
        {
          required: true,
          message: t('views.system.authentication.scanTheQRCode.appKeyPlaceholder'),
          trigger: ['blur', 'change'],
        },
      ]
    case 'app_secret':
      return [
        {
          required: true,
          message: t('views.system.authentication.scanTheQRCode.appSecretPlaceholder'),
          trigger: ['blur', 'change'],
        },
      ]
    case 'corp_id':
      return [
        {
          required: true,
          message: t('views.system.authentication.scanTheQRCode.corpIdPlaceholder'),
          trigger: ['blur', 'change'],
        },
      ]
    case 'agent_id':
      return [
        {
          required: true,
          message: t('views.system.authentication.scanTheQRCode.agentIdPlaceholder'),
          trigger: ['blur', 'change'],
        },
      ]
    case 'callback_url':
      return [
        {
          required: true,
          message: t('views.application.applicationAccess.callbackTip'),
          trigger: ['blur', 'change'],
        },
        {
          pattern: /^https?:\/\/.+/,
          message: t('views.system.authentication.scanTheQRCode.callbackWarning'),
          trigger: ['blur', 'change'],
        },
      ]
    default:
      return []
  }
}

const open = async (platform: Platform) => {
  visible.value = true
  loading.value = true
  Object.assign(currentPlatform, {
    ...platform,
    config: { ...platform.config },
  })

  // 设置默认的 callback_url
  const defaultCallbackUrl = getChatApiBaseUrl()
  switch (platform.key) {
    case 'wecom':
      if (currentPlatform.config.app_key) {
        currentPlatform.config.agent_id = currentPlatform.config.app_key
        delete currentPlatform.config.app_key
      }
        currentPlatform.config.callback_url = `${defaultCallbackUrl}/auth/wecom`
      break
    case 'dingtalk':
      if (currentPlatform.config.agent_id) {
        currentPlatform.config.corp_id = currentPlatform.config.agent_id
        delete currentPlatform.config.agent_id
      }
      currentPlatform.config = {
        corp_id: currentPlatform.config.corp_id,
        app_key: currentPlatform.config.app_key,
        app_secret: currentPlatform.config.app_secret,
        callback_url: defaultCallbackUrl,
      }
      currentPlatform.config.callback_url = `${defaultCallbackUrl}/auth/dingtalk`
      break
    case 'lark':
      currentPlatform.config.callback_url = `${defaultCallbackUrl}/auth/lark`
      break
    default:
      break
  }
  formRef.value?.clearValidate()
}
defineExpose({ open })

const validateForm = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      saveConfig()
    } else {
      MsgError(t('views.system.authentication.scanTheQRCode.validateFailedTip'))
    }
  })
}

const handleClose = () => {
  visible.value = false
  formRef.value?.clearValidate()
  emit('refresh')
}

function validateConnection() {
  platformApi.validateConnection(currentPlatform, loading).then((res: any) => {
    if (typeof res.data === 'object' && res.data !== null) {
      applyPlatformReadiness(res.data)
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

const passwordFields = new Set(['app_secret', 'client_secret', 'secret'])

const isPasswordField = (key: any) => passwordFields.has(key)
const emit = defineEmits(['refresh'])

function saveConfig() {
  platformApi.updateConfig(currentPlatform, loading).then((res: any) => {
    MsgSuccess(t('common.saveSuccess'))
    emit('refresh')
    visible.value = false
    formRef.value?.clearValidate()
  })
}

function applyPlatformReadiness(data: ExternalIntegrationPlatformInfo<PlatformConfig>) {
  const state = normalizeState(data.state)
  const config = data.config ? { ...currentPlatform.config, ...data.config } : currentPlatform.config
  const isConfigured =
    typeof data.is_configured === 'boolean' ? data.is_configured : hasConfiguredValue(config)

  Object.assign(currentPlatform, {
    isConfigured,
    isValid:
      typeof data.is_valid === 'boolean'
        ? data.is_valid
        : state
          ? readyStates.has(state)
          : isConfigured,
    isActive: typeof data.is_active === 'boolean' ? data.is_active : currentPlatform.isActive,
    state,
    failureReason: typeof data.failure_reason === 'string' ? data.failure_reason : '',
    config,
  })
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
      : hasConfiguredValue(data?.config || currentPlatform.config)
}

function getReadinessLabel() {
  if (currentPlatform.isValid) {
    return t('common.status.ready')
  }

  return t(
    Boolean(currentPlatform.failureReason) || failedStates.has(currentPlatform.state)
      ? 'common.status.fail'
      : 'common.status.notReady',
  )
}

function getReadinessTagType() {
  if (currentPlatform.isValid) {
    return 'success'
  }

  return Boolean(currentPlatform.failureReason) || failedStates.has(currentPlatform.state)
    ? 'danger'
    : 'warning'
}
</script>

<style lang="scss" scoped></style>
import { getChatApiBaseUrl } from '@/utils/common'
