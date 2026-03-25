<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.accessControl')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="650"
  >
    <el-form label-position="top" ref="limitFormRef" :model="form">
      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.clientQueryLimitLabel')"
      >
        <el-input-number
          v-model="form.access_num"
          :min="0"
          :step="1"
          :max="10000000"
          :value-on-clear="0"
          controls-position="right"
          style="width: 268px"
          step-strictly
        />
        <span class="ml-4">{{
          $t('views.applicationOverview.appInfo.LimitDialog.timesDays')
        }}</span>
      </el-form-item>

      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.authentication')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.authentication" @change="firstGeneration"></el-switch>
      </el-form-item>

      <template v-if="form.authentication">
        <el-form-item>
          <el-radio-group v-model="form.authentication_value.type">
            <el-radio value="password">
              {{ $t('views.applicationOverview.appInfo.LimitDialog.authenticationValue') }}
            </el-radio>
            <el-radio value="login">
              {{ $t('views.system.authentication.title') }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="form.authentication_value.type === 'password'">
          <div class="complex-input flex align-center w-full">
            <el-input
              class="complex-input__left"
              v-model="form.authentication_value.password_value"
              readonly
              style="width: 268px"
            />
            <div>
              <el-tooltip :content="$t('common.copy')" placement="top">
                <el-button text @click="copyClick(form.authentication_value.password_value)">
                  <AppIcon iconName="app-copy" class="color-secondary"></AppIcon>
                </el-button>
              </el-tooltip>
              <el-tooltip :content="$t('common.refresh')" placement="top">
                <el-button text style="margin: 0 4px 0 0 !important" @click="refreshAuthentication">
                  <AppIcon iconName="app-refresh" class="color-secondary"></AppIcon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </el-form-item>

        <template v-else>
          <el-form-item
            :label="$t('views.applicationOverview.appInfo.LimitDialog.loginMethod')"
            prop="authentication_value.login_value"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.loginMethodRequired'),
                trigger: 'change',
              },
            ]"
          >
            <div class="flex-between w-full mb-8">
              <span class="color-secondary">{{ $t('views.system.authentication.title') }}</span>
              <el-button type="primary" link @click="router.push({ name: 'applicationChatUser' })">
                {{ $t('views.applicationOverview.appInfo.LimitDialog.toSettingChatUser') }}
              </el-button>
            </div>
            <el-checkbox-group v-model="form.authentication_value.login_value">
              <template v-for="authType in auth_list" :key="authType.value">
                <el-checkbox :label="authType.label" :value="authType.value" />
              </template>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item
            v-if="form.authentication_value?.login_value?.includes('LOCAL')"
            :label="$t('views.system.display_code')"
            prop="authentication_value.max_attempts"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.displayCodeRequired'),
                trigger: 'change',
              },
            ]"
          >
            <span class="font-small">{{ $t('views.system.loginFailed') }}</span>
            <el-input-number
              class="ml-8"
              v-model="form.authentication_value.max_attempts"
              :min="-1"
              :max="10"
              :step="1"
              controls-position="right"
            />
            <span class="ml-8 font-small">{{ $t('views.system.loginFailedMessage') }}</span>
            <span class="ml-8 font-small color-secondary">
              ({{ $t('views.system.display_codeTip') }})
            </span>
          </el-form-item>
        </template>
      </template>

      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.whitelistLabel')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.white_active"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="form.white_list"
          :placeholder="$t('views.applicationOverview.appInfo.LimitDialog.whitelistPlaceholder')"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(limitFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { copyClick } from '@/utils/clipboard'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const router = useRouter()
const route = useRoute()
const {
  params: { id },
} = route

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const emit = defineEmits(['refresh'])

const limitFormRef = ref()
const auth_list = ref<Array<{ label: string; value: string }>>([])
const form = ref<any>({
  access_num: 0,
  white_active: true,
  white_list: '',
   authentication_value: {
     type: 'password',
     max_attempts: 1,
   },
   authentication: false,
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      access_num: 0,
      white_active: true,
      white_list: '',
      authentication_value: {
        type: 'password',
        max_attempts: 1,
      },
      authentication: false,
    }
  }
})

const open = (data: any) => {
  form.value.access_num = data.access_num
  form.value.white_active = data.white_active
  form.value.white_list = data.white_list?.length ? data.white_list?.join('\n') : ''
   form.value.authentication_value = data.authentication_value || {
     type: 'password',
     max_attempts: 1,
   }
   if (
     form.value.authentication_value.type === 'password' &&
     !form.value.authentication_value.password_value
   ) {
     refreshAuthentication()
   }
   if (!form.value.authentication_value.max_attempts) {
     form.value.authentication_value.max_attempts = 1
   }
   form.value.authentication = data.authentication
   dialogVisible.value = true
   loadSharedApi({ type: 'application', systemType: apiType.value })
     .getChatUserAuthType()
     .then((ok: any) => {
       auth_list.value = ok.data
     })
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        white_list: form.value.white_list ? form.value.white_list.split('\n') : [],
        white_active: form.value.white_active,
        access_num: form.value.access_num,
        authentication: form.value.authentication,
        authentication_value: form.value.authentication_value,
      }
      loadSharedApi({ type: 'application', systemType: apiType.value })
        .putAccessToken(id as string, obj, loading)
        .then(() => {
          emit('refresh')

          MsgSuccess(t('common.settingSuccess'))
          dialogVisible.value = false
        })
    }
  })
}

function generateAuthenticationValue(length: number = 10) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const randomValues = new Uint8Array(length)
  window.crypto.getRandomValues(randomValues)
  return Array.from(randomValues)
    .map((value) => chars[value % chars.length])
    .join('')
}

function refreshAuthentication() {
  form.value.authentication_value.password_value = generateAuthenticationValue()
}

function firstGeneration() {
  if (form.value.authentication && !form.value.authentication_value.password_value) {
    form.value.authentication_value = {
      type: 'password',
      password_value: generateAuthenticationValue(),
      max_attempts: 1,
    }
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
