import router from '@/router/chat'
import { createConfiguredApp } from '@/bootstrap/createApp'

const { app } = createConfiguredApp(router)
app.mount('#app')

export { app }
