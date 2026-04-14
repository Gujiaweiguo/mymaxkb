<template>
  <el-form class="reset-password-form" ref="formRef" :model="form" :rules="rules">
    <p class="mb-8 lighter">{{ $t('views.login.newPassword') }}</p>
    <el-form-item prop="password" style="margin-bottom: 8px">
      <el-input
        type="password"
        class="input-item"
        v-model="form.password"
        :placeholder="$t('views.login.enterPassword')"
        show-password
      />
    </el-form-item>
    <el-form-item prop="re_password">
      <el-input
        type="password"
        class="input-item"
        v-model="form.re_password"
        :placeholder="$t('views.login.enterPassword')"
        show-password
      />
    </el-form-item>
  </el-form>
  <div class="dialog-footer">
    <el-button v-if="!forced" @click="emit('cancel')">{{ $t('common.cancel') }}</el-button>
    <el-button type="primary" :loading="loading" @click="submit">
      {{ $t('common.save') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ResetCurrentUserPasswordRequest } from '@/api/type/user'
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from '@/api/user/user'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import { t } from '@/locales'

const props = withDefaults(
  defineProps<{
    forced?: boolean
  }>(),
  {
    forced: false,
  },
)

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

const router = useRouter()
const { login } = useStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const form = ref<ResetCurrentUserPasswordRequest>({
  code: '',
  password: '',
  re_password: '',
})

const rules = ref<FormRules<ResetCurrentUserPasswordRequest>>({
  password: [
    {
      required: true,
      message: t('views.login.enterPassword'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.login.loginForm.password.lengthMessage'),
      trigger: 'blur',
    },
  ],
  re_password: [
    {
      required: true,
      message: t('views.login.loginForm.re_password.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.login.loginForm.password.lengthMessage'),
      trigger: 'blur',
    },
    {
      validator: (rule, value, callback) => {
        if (form.value.password != form.value.re_password) {
          callback(new Error(t('views.login.loginForm.re_password.validatorMessage')))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})

const reset = () => {
  form.value = {
    code: '',
    password: '',
    re_password: '',
  }
  formRef.value?.resetFields()
}

const submit = () => {
  formRef.value?.validate().then(() => {
    loading.value = true
    return UserApi.resetCurrentPassword(form.value)
      .then(async () => {
        emit('success')
        login.clearToken()
        router.push({ name: 'login' })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ reset, submit })
</script>

<style lang="scss" scoped></style>
