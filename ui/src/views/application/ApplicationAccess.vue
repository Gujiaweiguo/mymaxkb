<template>
  <div class="p-16-24">
    <h4 class="mb-16">{{ $t('views.application.applicationAccess.title') }}</h4>

    <el-row :gutter="16">
      <el-col
        :xs="24"
        :sm="24"
        :md="12"
        :lg="12"
        :xl="12"
        class="mb-16"
        v-for="(item, index) in platforms"
        :key="index"
      >
        <el-card shadow="never" class="border-none cursor">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img :src="item.logoSrc" alt="" class="icon" />
              <div class="ml-12">
                <h5 class="mb-4">{{ item.name }}</h5>
                <el-text type="info" class="font-small">{{ item.description }}</el-text>
                <div class="mt-8 flex align-center flex-wrap gap-8">
                  <el-tag size="small" type="info" effect="plain">
                    {{ $t(item.exists ? 'common.status.configured' : 'common.status.unconfigured') }}
                  </el-tag>
                  <el-tag
                    v-if="item.supportsReadiness && item.exists"
                    size="small"
                    :type="getReadinessTagType(item)"
                  >
                    {{ getReadinessLabel(item) }}
                  </el-tag>
                </div>
                <div v-if="showFailureReason(item)" class="mt-4">
                  <el-text type="danger" size="small">
                    {{ `${$t('common.reason')}: ${item.failureReason}` }}
                  </el-text>
                </div>
              </div>
            </div>
            <div class="flex align-center">
              <span class="mr-8 font-small color-secondary" v-if="permissionPrecise.access_edit(id)">
                {{ getActivationLabel(item) }}
              </span>
              <el-switch
                size="small"
                v-model="item.isActive"
                @change="changeStatus(item.key, item.isActive)"
                :disabled="!canTogglePlatform(item)"
                v-if="permissionPrecise.access_edit(id)"
              />
              <el-divider direction="vertical" />
              <el-button
                class="mr-4"
                @click="openDrawer(item)"
                v-if="permissionPrecise.access_edit(id)"
                >{{ $t('views.application.applicationAccess.setting') }}</el-button
              >
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <AccessSettingDrawer ref="AccessSettingDrawerRef" @refresh="refresh" />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import type {
  ExternalIntegrationLegacyStatus,
  ExternalIntegrationPlatformStatus,
} from '@/api/type/external-integration'
import AccessSettingDrawer from './component/AccessSettingDrawer.vue'
import { MsgSuccess } from '@/utils/message'
import { useRoute } from 'vue-router'
import { t } from '@/locales'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

interface ApplicationPlatform {
  key: string
  logoSrc: string
  name: string
  description: string
  isActive: boolean
  exists: boolean
  isValid: boolean
  state: string
  failureReason: string
  supportsReadiness: boolean
}

const readyStates = new Set(['ready', 'enabled', 'active', 'valid', 'success'])
const failedStates = new Set(['failed', 'invalid', 'error'])
const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

// 平台数据
const platforms = reactive<ApplicationPlatform[]>([
  {
    key: 'wecomBot',
    logoSrc: new URL(`../../assets/logo/logo_wechat-bot.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.wecomBot'),
    description: t('views.application.applicationAccess.wecomBotTip'),
    isActive: false,
    exists: false,
    isValid: false,
    state: '',
    failureReason: '',
    supportsReadiness: false,
  },
  {
    key: 'wecom',
    logoSrc: new URL(`../../assets/logo/logo_wechat-work.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.wecom'),
    description: t('views.application.applicationAccess.wecomTip'),
    isActive: false,
    exists: false,
    isValid: false,
    state: '',
    failureReason: '',
    supportsReadiness: true,
  },
  {
    key: 'dingtalk',
    logoSrc: new URL(`../../assets/logo/logo_dingtalk.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.dingtalk'),
    description: t('views.application.applicationAccess.dingtalkTip'),
    isActive: false,
    exists: false,
    isValid: false,
    state: '',
    failureReason: '',
    supportsReadiness: true,
  },
  {
    key: 'wechat',
    logoSrc: new URL(`../../assets/logo/logo_wechat.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.wechat'),
    description: t('views.application.applicationAccess.wechatTip'),
    isActive: false,
    exists: false,
    isValid: false,
    state: '',
    failureReason: '',
    supportsReadiness: false,
  },
  {
    key: 'lark',
    logoSrc: new URL(`../../assets/logo/logo_lark.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.lark'),
    description: t('views.application.applicationAccess.larkTip'),
    isActive: false,
    exists: false,
    isValid: false,
    state: '',
    failureReason: '',
    supportsReadiness: true,
  },
  {
    key: 'slack',
    logoSrc: new URL(`../../assets/logo/logo_slack.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.slack'),
    description: t('views.application.applicationAccess.slackTip'),
    isActive: false,
    exists: false,
    isValid: false,
    state: '',
    failureReason: '',
    supportsReadiness: false,
  },
])

const AccessSettingDrawerRef = ref()
const loading = ref(false)
const {
  params: { id },
} = route as any

function openDrawer(platform: ApplicationPlatform) {
  AccessSettingDrawerRef.value.open(id, platform.key, platform)
}

function refresh() {
  getPlatformStatus()
}

function getPlatformStatus() {
  loading.value = true
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getPlatformStatus(id)
    .then((res: any) => {
      platforms.forEach((platform) => {
        applyPlatformStatus(platform, res.data[platform.key])
      })
      loading.value = false
    })
}

function changeStatus(type: string, value: boolean) {
  const data = {
    type: type,
    status: value,
  }
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .updatePlatformStatus(id, data)
    .then(() => {
      MsgSuccess(t('common.saveSuccess'))
    })
}

onMounted(() => {
  getPlatformStatus()
})

function applyPlatformStatus(
  platform: ApplicationPlatform,
  data?: ExternalIntegrationPlatformStatus | ExternalIntegrationLegacyStatus,
) {
  if (Array.isArray(data)) {
    platform.exists = Boolean(data[0])
    platform.isActive = Boolean(data[1])
    platform.isValid = Boolean(data[0])
    platform.state = platform.isValid ? 'ready' : ''
    platform.failureReason = ''
    return
  }

  const state = normalizeState(data?.state)
  const exists =
    typeof data?.exists === 'boolean'
      ? data.exists
      : typeof data?.is_configured === 'boolean'
        ? data.is_configured
        : Object.keys(data || {}).length > 0

  platform.exists = exists
  platform.isActive = typeof data?.is_active === 'boolean' ? data.is_active : false
  platform.isValid =
    typeof data?.is_valid === 'boolean'
      ? data.is_valid
      : state
        ? readyStates.has(state)
        : exists
  platform.state = state
  platform.failureReason = typeof data?.failure_reason === 'string' ? data.failure_reason : ''
}

function normalizeState(state?: string | null) {
  return typeof state === 'string' ? state.toLowerCase() : ''
}

function hasFailedState(platform: ApplicationPlatform) {
  return Boolean(platform.failureReason) || failedStates.has(platform.state)
}

function getReadinessLabel(platform: ApplicationPlatform) {
  if (platform.isValid) {
    return t('common.status.ready')
  }

  return t(hasFailedState(platform) ? 'common.status.fail' : 'common.status.notReady')
}

function getReadinessTagType(platform: ApplicationPlatform) {
  if (platform.isValid) {
    return 'success'
  }

  return hasFailedState(platform) ? 'danger' : 'warning'
}

function showFailureReason(platform: ApplicationPlatform) {
  return platform.supportsReadiness && platform.exists && !platform.isValid && Boolean(platform.failureReason)
}

function canTogglePlatform(platform: ApplicationPlatform) {
  return platform.exists && (!platform.supportsReadiness || platform.isValid)
}

function getActivationLabel(platform: ApplicationPlatform) {
  if (platform.isActive) {
    return t('common.status.enabled')
  }

  if (canTogglePlatform(platform)) {
    return t('common.status.disabled')
  }

  return t('common.status.notReady')
}
</script>

<style lang="scss" scoped></style>
