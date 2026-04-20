<template>
  <div class="orchestrator-panel mt-16" v-loading="loading">
    <div class="flex-between align-center mb-12">
      <el-text type="info">{{ $t('views.applicationOverview.appInfo.orchestratorIntegration') }}</el-text>
      <el-button type="primary" text @click="copyFullPayload">
        <AppIcon iconName="app-copy" class="mr-4"></AppIcon>
        {{ $t('views.applicationOverview.appInfo.copyIntegrationJson') }}
      </el-button>
    </div>

    <div class="orchestrator-panel__field mb-12">
      <div class="orchestrator-panel__label">
        {{ $t('views.applicationOverview.appInfo.endpointUrl') }}
      </div>
      <div class="orchestrator-panel__value break-all">
        {{ integration.endpoint_url || '-' }}
      </div>
    </div>

    <div class="orchestrator-panel__field mb-12">
      <div class="orchestrator-panel__label">
        {{ $t('views.applicationOverview.appInfo.authToken') }}
      </div>
      <div class="orchestrator-panel__value break-all">
        {{ integration.auth_token || '-' }}
      </div>
    </div>

    <div class="orchestrator-panel__field">
      <div class="orchestrator-panel__label">
        {{ $t('views.applicationOverview.appInfo.defaultParams') }}
      </div>
      <pre class="orchestrator-panel__json">{{ defaultParamsText }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

defineOptions({ name: 'OrchestratorIntegrationPanel' })

interface OrchestratorIntegrationPayload {
  endpoint_url: string
  auth_token: string
  default_params: Record<string, any>
}

const route = useRoute()
const {
  params: { id },
} = route as any

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  }

  return 'workspace'
})

const loading = ref(false)
const integration = ref<OrchestratorIntegrationPayload>({
  endpoint_url: '',
  auth_token: '',
  default_params: {},
})

const fullPayload = computed(() => ({
  endpoint_url: integration.value.endpoint_url,
  auth_token: integration.value.auth_token,
  default_params: integration.value.default_params,
}))

const defaultParamsText = computed(() => JSON.stringify(integration.value.default_params || {}, null, 2))

function copyFullPayload() {
  copyClick(JSON.stringify(fullPayload.value, null, 2))
}

function getOrchestratorIntegration() {
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getOrchestratorIntegration(id, loading)
    .then((res: any) => {
      integration.value = {
        endpoint_url: res?.data?.endpoint_url || '',
        auth_token: res?.data?.auth_token || '',
        default_params: res?.data?.default_params || {},
      }
    })
}

onMounted(() => {
  getOrchestratorIntegration()
})
</script>

<style lang="scss" scoped>
.orchestrator-panel {
  border: 1px solid var(--el-border-color);
  border-radius: var(--app-border-radius-base);
  padding: 16px;
  background: var(--el-fill-color-blank);

  &__field {
    &:last-child {
      margin-bottom: 0;
    }
  }

  &__label {
    font-size: 13px;
    color: var(--app-text-color-secondary);
    margin-bottom: 4px;
  }

  &__value {
    line-height: 22px;
    color: var(--el-text-color-primary);
  }

  &__json {
    margin: 0;
    padding: 12px;
    border-radius: var(--app-border-radius-small);
    background: var(--app-layout-bg-color);
    color: var(--el-text-color-primary);
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 20px;
    font-size: 12px;
  }
}
</style>
