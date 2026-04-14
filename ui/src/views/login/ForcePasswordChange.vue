<template>
  <login-layout>
    <LoginContainer>
      <h2 class="mb-24">{{ $t('views.login.resetPassword') }}</h2>
      <p class="mb-24 lighter">{{ $t('views.login.newPassword') }}</p>
      <CurrentPasswordResetForm forced />
    </LoginContainer>
  </login-layout>
</template>

<script setup lang="ts">
import LoginContainer from '@/layout/login-layout/LoginContainer.vue'
import LoginLayout from '@/layout/login-layout/LoginLayout.vue'
import CurrentPasswordResetForm from '@/components/user/CurrentPasswordResetForm.vue'
</script>

<style lang="scss" scoped></style>
