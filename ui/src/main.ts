import router from '@/router'
import useThemeStore from '@/stores/modules/theme'
import { createConfiguredApp } from '@/bootstrap/createApp'

const { app, pinia } = createConfiguredApp(router)
useThemeStore(pinia).hydrateTheme()
app.mount('#app')
