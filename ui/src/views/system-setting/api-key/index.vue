<template>
  <div class="system-api-key p-16-24">
    <el-breadcrumb separator-icon="ArrowRight" class="mb-16">
      <el-breadcrumb-item>{{ t('views.system.subTitle') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ $t('layout.apiKey') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>

    <el-card style="--el-card-padding: 16px" v-loading="loading">
      <el-button
        type="primary"
        class="mb-16"
        @click="createApiKey"
        v-hasPermission="
          new ComplexPermission([RoleConst.ADMIN], [PermissionConst.SYSTEM_API_KEY_EDIT], [], 'OR')
        "
      >
        {{ $t('common.create') }}
      </el-button>

      <app-table
        :data="apiKey"
        :loading="loading"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getApiKeyList"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="secret_key" label="API Key">
          <template #default="{ row }">
            <div class="api-key-container">
              <el-tooltip :content="row.secret_key" placement="top" effect="light" :hide-after="0">
                <span class="api-key-text vertical-middle lighter break-all">
                  {{ row.secret_key }}
                </span>
              </el-tooltip>
              <el-button
                v-if="!isMaskedSecretKey(row.secret_key)"
                type="primary"
                text
                @click="copyClick(row.secret_key)"
                class="copy-btn"
              >
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="$t('views.document.enableStatus.label')" width="100">
          <template #default="{ row }">
            <div v-if="row.is_active" class="flex align-center">
              <el-icon class="color-success mr-8" style="font-size: 16px">
                <SuccessFilled />
              </el-icon>
              <span class="color-text-primary">
                {{ $t('common.status.enabled') }}
              </span>
            </div>
            <div v-else class="flex align-center">
              <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
              <span class="color-text-primary">
                {{ $t('common.status.disabled') }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="$t('layout.crossSettings')" width="100" prop="allow_cross_domain">
          <template #default="{ row }">
            <el-tag size="small" type="info" class="info-tag" v-if="row.allow_cross_domain">
              {{ $t('views.system.authentication.scanTheQRCode.alreadyTurnedOn') }}
            </el-tag>
            <el-tag size="small" class="blue-tag" v-else>
              {{ $t('views.system.authentication.scanTheQRCode.notEnabled') }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="$t('layout.about.expiredTime')" width="265">
          <template #default="{ row }">
            <span v-if="row.is_permanent" class="permanent-status">
              {{ t('layout.time.neverExpires') }}
            </span>
            <span v-else class="expiry-info">
              <span
                v-if="fromNowDate(row.expire_time)"
                :class="getExpiryClass(row.expire_time)"
                class="relative-time"
              >
                ({{ fromNowDate(row.expire_time) }})
              </span>
              {{ datetimeFormat(row.expire_time) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.createDate')" width="170" prop="create_time" sortable>
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.operation')" align="left" width="130">
          <template #default="{ row }">
            <span @click.stop>
              <el-switch size="small" v-model="row.is_active" @change="changeState($event, row)" />
            </span>
            <el-divider direction="vertical" />
            <span class="mr-4">
              <el-tooltip effect="dark" :content="$t('common.setting')" placement="top">
                <el-button type="primary" text @click.stop="settingApiKey(row)">
                  <AppIcon iconName="app-edit"></AppIcon>
                </el-button>
              </el-tooltip>
            </span>
            <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
              <el-button type="primary" text @click="deleteApiKey(row)">
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </app-table>
    </el-card>

    <SettingAPIKeyDialog ref="SettingAPIKeyDialogRef" @refresh="getApiKeyList" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { copyClick } from '@/utils/clipboard'
import SettingAPIKeyDialog from '@/views/application-overview/component/SettingAPIKeyDrawer.vue'
import { datetimeFormat, fromNowDate } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import systemApiKeyApi from '@/api/system/api-key'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'

const orderBy = ref<string>('')

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

function handleSizeChange() {
  paginationConfig.current_page = 1
  getApiKeyList()
}

const SettingAPIKeyDialogRef = ref()
const loading = ref(false)
const apiKey = ref<any[]>([])

function settingApiKey(row: any) {
  SettingAPIKeyDialogRef.value.open(row, 'SYSTEM')
}

function deleteApiKey(row: any) {
  MsgConfirm(
    `${t('views.applicationOverview.appInfo.APIKeyDialog.msgConfirm1')}: ${row.secret_key}?`,
    t('views.applicationOverview.appInfo.APIKeyDialog.msgConfirm2'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      systemApiKeyApi.delAPIKey(row.id, loading).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getApiKeyList()
      })
    })
    .catch(() => {})
}

async function changeState(bool: boolean, row: any) {
  const obj = {
    is_active: bool,
  }
  const str = obj.is_active ? t('common.status.enabled') : t('common.status.disabled')
  await systemApiKeyApi
    .putAPIKey(row.id, obj, loading)
    .then(() => {
      MsgSuccess(str)
      getApiKeyList()
      return true
    })
    .catch(() => {
      return false
    })
}

function createApiKey() {
  systemApiKeyApi.postAPIKey(loading).then(() => {
    MsgSuccess(t('common.createSuccess'))
    getApiKeyList()
  })
}

function getApiKeyList() {
  const param = {
    order_by: orderBy.value,
  }
  systemApiKeyApi
    .getAPIKey(paginationConfig.current_page, paginationConfig.page_size, param, loading)
    .then((res: any) => {
      apiKey.value = res.data.records
      paginationConfig.total = res.data.total
    })
}

function handleSortChange({ prop, order }: { prop: string; order: string }) {
  orderBy.value = order === 'ascending' ? prop : `-${prop}`
  getApiKeyList()
}

function getExpiryClass(expireTime: any) {
  const status = fromNowDate(expireTime)
  if (status === t('layout.time.expired')) {
    return 'color-danger'
  }

  return 'color-warning'
}

function isMaskedSecretKey(secretKey: string) {
  return secretKey?.includes('*')
}

onMounted(() => {
  getApiKeyList()
})
</script>

<style lang="scss" scoped>
.api-key-container {
  display: flex;
  align-items: center;
  gap: 8px;

  .api-key-text {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
    cursor: pointer;
  }

  .copy-btn {
    flex-shrink: 0;
  }
}
</style>
