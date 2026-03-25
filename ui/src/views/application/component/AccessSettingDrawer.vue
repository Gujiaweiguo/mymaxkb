<template>
  <el-drawer v-model="visible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <h4>{{ drawerTitle }}</h4>
      </div>
    </template>

    <el-form
      v-if="dataLoaded"
      ref="formRef"
      :model="form[configType]"
      label-width="120px"
      :rules="rules[configType]"
      label-position="top"
      require-asterisk-position="right"
    >
      <div class="mb-16" v-if="supportsReadiness">
        <div class="flex align-center flex-wrap gap-8">
          <el-tag size="small" type="info" effect="plain">
            {{ $t(readiness.isConfigured ? 'common.status.configured' : 'common.status.unconfigured') }}
          </el-tag>
          <el-tag v-if="readiness.isConfigured" size="small" :type="getReadinessTagType()">
            {{ getReadinessLabel() }}
          </el-tag>
        </div>
        <div v-if="showFailureReason" class="mt-8">
          <el-text type="danger" size="small">
            {{ `${$t('common.reason')}: ${readiness.failureReason}` }}
          </el-text>
        </div>
      </div>
      <h4 class="title-decoration-1 mb-16">{{ infoTitle }}</h4>

      <template v-for="(item, key) in configFields[configType]" :key="key">
        <el-form-item :label="item.label" :prop="key">
          <el-input
            v-model="form[configType][key]"
            :type="isPasswordField(key) ? (passwordVisible[key] ? 'text' : 'password') : 'text'"
            :placeholder="item.placeholder"
            :show-password="isPasswordField(key)"
          >
          </el-input>
        </el-form-item>
      </template>
      <div v-if="configType === 'wechat'" class="flex align-center mb-16">
        <span class="lighter mr-8">{{
          $t('views.application.applicationAccess.wecomSetting.authenticationSuccessful')
        }}</span>
        <el-switch v-if="configType === 'wechat'" v-model="form[configType].is_certification" />
      </div>

      <h4 class="title-decoration-1 mb-16">
        {{ $t('views.application.applicationAccess.callback') }}
      </h4>
      <el-form-item label="URL" prop="callback_url">
        <el-input
          v-model="form[configType].callback_url"
          :placeholder="$t('views.application.applicationAccess.callbackTip')"
          readonly
        >
          <template #append>
            <el-button @click="copyClick(form[configType].callback_url)">
              <AppIcon iconName="app-copy"></AppIcon>
            </el-button>
          </template>
        </el-input>
        <el-text type="info" v-if="configType === 'wechat'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="color-primary"
            href="https://mp.weixin.qq.com/advanced/advanced?action=dev&t=advanced/dev"
            target="_blank"
            >{{ $t('views.application.applicationAccess.wechatPlatform') }}</a
          >{{ $t('views.application.applicationAccess.wechatSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'dingtalk'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="color-primary"
            href="https://open-dev.dingtalk.com/fe/app?hash=%23%2Fcorp%2Fapp#/corp/app"
            target="_blank"
            >{{ $t('views.application.applicationAccess.dingtalkPlatform') }}</a
          >{{ $t('views.application.applicationAccess.dingtalkSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'wecom'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="color-primary"
            href="https://work.weixin.qq.com/wework_admin/frame#apps"
            target="_blank"
            >{{ $t('views.application.applicationAccess.wecomPlatform') }}</a
          >{{ $t('views.application.applicationAccess.wecomSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'lark'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a class="color-primary" href="https://open.feishu.cn/app/" target="_blank">{{
            $t('views.application.applicationAccess.larkPlatform')
          }}</a
          >{{ $t('views.application.applicationAccess.larkSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'wecomBot'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="color-primary"
            href="https://work.weixin.qq.com/wework_admin/frame#/manageTools"
            target="_blank"
            >{{ $t('views.application.applicationAccess.wecomPlatform') }}</a
          >{{ $t('views.application.applicationAccess.wecomBotSetting.urlInfo') }}
        </el-text>
      </el-form-item>
    </el-form>

    <template #footer>
      <div>
        <el-button @click="closeDrawer">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :disabled="loading">
          {{ $t('common.save') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import { useRoute } from 'vue-router'
import type {
  ExternalIntegrationPlatformInfo,
  ExternalIntegrationPlatformStatus,
} from '@/api/type/external-integration'
import { MsgError, MsgSuccess } from '@/utils/message'
import { copyClick } from '@/utils/clipboard'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

type PlatformType = 'wechat' | 'dingtalk' | 'wecom' | 'lark' | 'slack' | 'wecomBot'

interface PlatformReadinessState {
  isConfigured: boolean
  isValid: boolean
  state: string
  failureReason: string
}

interface DrawerPlatformStatus extends PlatformReadinessState {
  key: PlatformType
  exists: boolean
  supportsReadiness: boolean
}

const readyStates = new Set(['ready', 'enabled', 'active', 'valid', 'success'])
const failedStates = new Set(['failed', 'invalid', 'error'])
const readinessPlatformTypes = new Set<PlatformType>(['wecom', 'dingtalk', 'lark'])

const route = useRoute()

const {
  params: { id },
} = route as any
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const emit = defineEmits(['refresh'])
const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const dataLoaded = ref(false)
const configType = ref<PlatformType>('wechat')
const readiness = reactive<PlatformReadinessState>({
  isConfigured: false,
  isValid: false,
  state: '',
  failureReason: '',
})

const form = reactive<any>({
  wechat: {
    app_id: '',
    app_secret: '',
    token: '',
    encoding_aes_key: '',
    is_certification: false,
    callback_url: '',
  },
  dingtalk: {
    client_id: '',
    client_secret: '',
    token: '',
    encoding_aes_key: '',
    callback_url: '',
  },
  wecom: {
    app_id: '',
    agent_id: '',
    secret: '',
    token: '',
    encoding_aes_key: '',
    callback_url: '',
  },
  lark: { app_id: '', app_secret: '', verification_token: '', callback_url: '' },
  slack: { signing_secret: '', bot_user_token: '', callback_url: '' },
  wecomBot: {
    token: '',
    encoding_aes_key: '',
    callback_url: '',
  },
})

const rules = reactive<{ [propName: string]: any }>({
  wechat: {
    app_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.appIdPlaceholder'),
        trigger: 'blur',
      },
    ],
    app_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.appSecretPlaceholder'),
        trigger: 'blur',
      },
    ],
    token: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.tokenPlaceholder'),
        trigger: 'blur',
      },
    ],
    encoding_aes_key: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.aesKeyPlaceholder'),
        trigger: 'blur',
      },
    ],
  },
  dingtalk: {
    client_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.dingtalkSetting.clientIdPlaceholder'),
        trigger: 'blur',
      },
    ],
    client_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.dingtalkSetting.clientSecretPlaceholder'),
        trigger: 'blur',
      },
    ],
    token: [
      {
        required: true,
        message: t('views.application.applicationAccess.dingtalkSetting.tokenPlaceholder'),
        trigger: 'blur',
      },
    ],
    encoding_aes_key: [
      {
        required: true,
        message: t('views.application.applicationAccess.dingtalkSetting.encodingAesKeyPlaceholder'),
        trigger: 'blur',
      },
    ],
  },
  wecom: {
    app_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.cropIdPlaceholder'),
        trigger: 'blur',
      },
    ],
    agent_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.agentIdPlaceholder'),
        trigger: 'blur',
      },
    ],
    secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.secretPlaceholder'),
        trigger: 'blur',
      },
    ],
    token: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.tokenPlaceholder'),
        trigger: 'blur',
      },
    ],
    encoding_aes_key: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.encodingAesKeyPlaceholder'),
        trigger: 'blur',
      },
    ],
  },
  lark: {
    app_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
        trigger: 'blur',
      },
    ],
    app_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
        trigger: 'blur',
      },
    ],
    verification_token: [
      {
        required: false,
        message: t('views.application.applicationAccess.larkSetting.verificationTokenPlaceholder'),
        trigger: 'blur',
      },
    ],
  },
  slack: {
    signing_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.slackSetting.signingSecretPlaceholder'),
        trigger: 'blur',
      },
    ],
    bot_user_token: [
      {
        required: true,
        message: t('views.application.applicationAccess.slackSetting.botUserTokenPlaceholder'),
        trigger: 'blur',
      },
    ],
  },
  wecomBot: {
    token: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.tokenPlaceholder'),
        trigger: 'blur',
      },
    ],
    encoding_aes_key: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.encodingAesKeyPlaceholder'),
        trigger: 'blur',
      },
    ],
  },
})

const configFields: { [propName: string]: { [propName: string]: any } } = {
  wechat: {
    app_id: {
      label: t('views.application.applicationAccess.wechatSetting.appId'),
      placeholder: '',
    },
    app_secret: {
      label: t('views.application.applicationAccess.wechatSetting.appSecret'),
      placeholder: '',
    },
    token: { label: t('views.application.applicationAccess.wechatSetting.token'), placeholder: '' },
    encoding_aes_key: {
      label: t('views.application.applicationAccess.wechatSetting.aesKey'),
      placeholder: '',
    },
  },
  dingtalk: {
    client_id: {
      label: t('views.application.applicationAccess.dingtalkSetting.clientId'),
      placeholder: t('views.application.applicationAccess.dingtalkSetting.clientIdPlaceholder'),
    },
    client_secret: {
      label: t('views.application.applicationAccess.dingtalkSetting.clientSecret'),
      placeholder: t('views.application.applicationAccess.dingtalkSetting.clientSecretPlaceholder'),
    },
    token: {
      label: t('views.application.applicationAccess.dingtalkSetting.token'),
      placeholder: t('views.application.applicationAccess.dingtalkSetting.tokenPlaceholder'),
    },
    encoding_aes_key: {
      label: t('views.application.applicationAccess.dingtalkSetting.encodingAesKey'),
      placeholder: t('views.application.applicationAccess.dingtalkSetting.encodingAesKeyPlaceholder'),
    },
  },
  wecom: {
    app_id: {
      label: t('views.application.applicationAccess.wecomSetting.cropId'),
      placeholder: '',
    },
    agent_id: { label: 'Agent ID', placeholder: '' },
    secret: { label: 'Secret', placeholder: '' },
    token: { label: 'Token', placeholder: '' },
    encoding_aes_key: { label: 'EncodingAESKey', placeholder: '' },
  },
  wecomBot: {
    token: { label: 'Token', placeholder: '' },
    encoding_aes_key: { label: 'EncodingAESKey', placeholder: '' },
  },
  lark: {
    app_id: { label: 'App ID', placeholder: '' },
    app_secret: { label: 'App Secret', placeholder: '' },
    verification_token: { label: 'Verification Token', placeholder: '' },
  },
  slack: {
    signing_secret: { label: 'Signing Secret', placeholder: '' },
    bot_user_token: { label: 'Bot User Token', placeholder: '' },
  },
}

const passwordFields = new Set([
  'app_secret',
  'client_secret',
  'secret',
  'bot_user_token',
  'signing_secret',
])

const drawerTitle = computed(
  () =>
    ({
      wechat: t('views.application.applicationAccess.wechatSetting.title'),
      dingtalk: t('views.application.applicationAccess.dingtalkSetting.title'),
      wecom: t('views.application.applicationAccess.wecomSetting.title'),
      lark: t('views.application.applicationAccess.larkSetting.title'),
      slack: t('views.application.applicationAccess.slackSetting.title'),
      wecomBot: t('views.application.applicationAccess.wecomBotSetting.title'),
    })[configType.value],
)

const infoTitle = computed(
  () =>
    ({
      wechat: t('common.info'),
      dingtalk: t('common.info'),
      wecom: t('common.info'),
      lark: t('common.info'),
      slack: t('common.info'),
      wecomBot: t('common.info'),
    })[configType.value],
)

const passwordVisible = reactive<Record<string, boolean>>(
  Object.keys(configFields[configType.value]).reduce(
    (acc, key) => {
      if (passwordFields.has(key)) {
        acc[key] = false
      }
      return acc
    },
    {} as Record<string, boolean>,
  ),
)

const isPasswordField = (key: any) => passwordFields.has(key)
const supportsReadiness = computed(() => readinessPlatformTypes.has(configType.value))
const showFailureReason = computed(
  () => supportsReadiness.value && readiness.isConfigured && !readiness.isValid && Boolean(readiness.failureReason),
)

const closeDrawer = () => {
  visible.value = false
}

const submit = async () => {
  if (loading.value) return

  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        loadSharedApi({ type: 'application', systemType: apiType.value })
          .updatePlatformConfig(id, configType.value, form[configType.value], loading)
          .then(() => {
            MsgSuccess(t('common.saveSuccess'))
            closeDrawer()
            emit('refresh')
          })
      } catch {
        MsgError(t('views.application.tip.saveErrorMessage'))
      }
    }
  })
}

const open = async (id: string, type: PlatformType, platform?: DrawerPlatformStatus) => {
  visible.value = true
  configType.value = type
  loading.value = true
  dataLoaded.value = false
  resetReadiness(platform)
  formRef.value?.resetFields()
  try {
    const res = await loadSharedApi({
      type: 'application',
      systemType: apiType.value,
    }).getPlatformConfig(id, type)
    if (res.data) {
      applyReadinessMeta(res.data, platform)
      form[configType.value] = getConfigPayload(res.data)
    }
    dataLoaded.value = true
  } catch {
    MsgError(t('views.application.tip.loadingErrorMessage'))
  } finally {
    loading.value = false
    form[configType.value].callback_url =
      `${window.location.origin}${window.MaxKB.prefix}/api/chat/${type}/${id}`
  }
}

defineExpose({ open })

function resetReadiness(platform?: DrawerPlatformStatus) {
  readiness.isConfigured = platform?.exists ?? false
  readiness.isValid = platform?.isValid ?? false
  readiness.state = platform?.state ?? ''
  readiness.failureReason = platform?.failureReason ?? ''
}

function applyReadinessMeta(
  payload: ExternalIntegrationPlatformInfo | ExternalIntegrationPlatformStatus,
  platform?: DrawerPlatformStatus,
) {
  const state = normalizeState(payload?.state)
  const isConfigured =
    'exists' in payload && typeof payload.exists === 'boolean'
      ? payload.exists
      : typeof payload?.is_configured === 'boolean'
        ? payload.is_configured
        : platform?.exists ?? readiness.isConfigured

  readiness.isConfigured = isConfigured
  readiness.isValid =
    typeof payload?.is_valid === 'boolean'
      ? payload.is_valid
      : state
        ? readyStates.has(state)
        : isConfigured
  readiness.state = state
  readiness.failureReason = typeof payload?.failure_reason === 'string' ? payload.failure_reason : ''
}

function getConfigPayload(payload: ExternalIntegrationPlatformInfo | Record<string, any>) {
  if ('config' in payload && payload.config && typeof payload.config === 'object') {
    return payload.config
  }

  return payload
}

function normalizeState(state?: string | null) {
  return typeof state === 'string' ? state.toLowerCase() : ''
}

function getReadinessLabel() {
  if (readiness.isValid) {
    return t('common.status.ready')
  }

  return t(
    Boolean(readiness.failureReason) || failedStates.has(readiness.state)
      ? 'common.status.fail'
      : 'common.status.notReady',
  )
}

function getReadinessTagType() {
  if (readiness.isValid) {
    return 'success'
  }

  return Boolean(readiness.failureReason) || failedStates.has(readiness.state) ? 'danger' : 'warning'
}
</script>
