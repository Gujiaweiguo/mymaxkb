<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.displaySetting')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="550"
  >
    <el-form label-position="top" ref="displayFormRef" :model="form">
      <el-form-item>
        <el-card shadow="never">
          <div class="flex-between mb-8">
            <span class="lighter">{{ $t('views.application.title') + ' LOGO' }}</span>
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/jpeg, image/png, image/gif"
              :on-change="onChange"
            >
              <el-button size="small">
                {{ $t('views.applicationOverview.SettingDisplayDialog.replace') }}
              </el-button>
            </el-upload>
          </div>
          <div class="flex align-center mb-8">
            <el-avatar shape="square" :size="32" style="background: none" class="mr-12">
              <img :src="iconUrl" alt="" />
            </el-avatar>
            <el-text type="info" size="small">
              {{ $t('views.applicationOverview.SettingDisplayDialog.imageMessage') }}
            </el-text>
          </div>
        </el-card>
      </el-form-item>
      <el-form-item>
        <span>{{
          $t('layout.language')
        }}</span>
        <el-select v-model="form.language" clearable>
          <el-option
            v-for="item in langList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-space direction="vertical" alignment="start" :size="2">
          <el-checkbox
            v-model="form.show_source"
            :label="$t('views.applicationOverview.SettingDisplayDialog.showSourceLabel')"
          />

          <el-checkbox
            v-model="form.show_exec"
            :label="
              $t('views.applicationOverview.SettingDisplayDialog.showExecutionDetail')
            "
          />
        </el-space>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(displayFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, UploadFiles } from 'element-plus'
import { MsgSuccess, MsgError } from '@/utils/message'
import { langList, t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { resetUrl } from '@/utils/common'

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

const displayFormRef = ref()
const form = ref<any>({
  show_source: false,
  show_exec: false,
  language: '',
  icon: '',
})

const detail = ref<any>(null)
const iconUrl = ref(resetUrl('./favicon.ico'))

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false,
      show_exec: false,
      language: '',
      icon: '',
    }
    iconUrl.value = resetUrl('./favicon.ico')
  }
})

const onChange = (file: any, fileList: UploadFiles) => {
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    MsgError(t('common.EditAvatarDialog.fileSizeExceeded'))
    return false
  }

  form.value.icon = file.raw
  iconUrl.value = URL.createObjectURL(file.raw)
}

const open = (data: any, content: any) => {
  detail.value = content
  form.value.show_source = data.show_source
  form.value.show_exec = data.show_exec
  form.value.language = data.language
  form.value.icon = data.icon || content?.icon || ''
  iconUrl.value = resetUrl(form.value.icon, resetUrl('./favicon.ico'))
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const fd = new FormData()
      fd.append('show_source', String(form.value.show_source))
      fd.append('show_exec', String(form.value.show_exec))
      fd.append('language', form.value.language || '')
      if (form.value.icon instanceof File) {
        fd.append('icon', form.value.icon)
      }

      loadSharedApi({ type: 'application', systemType: apiType.value })
        .putAccessToken(id as string, fd, loading)
        .then(() => {
          emit('refresh')

          MsgSuccess(t('common.settingSuccess'))
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
