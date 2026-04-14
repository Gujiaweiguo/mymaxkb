<template>
  <el-dialog
    v-model="resetPasswordDialog"
    :title="$t('views.login.resetPassword')"
    destroy-on-close
    append-to-body
    align-center
    :show-close="!props.forced"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <CurrentPasswordResetForm ref="currentPasswordResetFormRef" :forced="props.forced" @success="close(true)" @cancel="close()" />
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import CurrentPasswordResetForm from '@/components/user/CurrentPasswordResetForm.vue'

const props = defineProps<{
  forced?: boolean
}>()

const resetPasswordDialog = ref<boolean>(false)
const currentPasswordResetFormRef = ref<InstanceType<typeof CurrentPasswordResetForm>>()

const open = () => {
  currentPasswordResetFormRef.value?.reset?.()
  resetPasswordDialog.value = true
}

const close = (force = false) => {
  if (props.forced && !force) {
    return
  }
  resetPasswordDialog.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scope></style>
