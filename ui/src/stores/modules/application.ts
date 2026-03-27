import { getChatBaseUrl } from '@/utils/common'

import { defineStore } from 'pinia'
const useApplicationStore = defineStore('application', {
  state: () => ({
    location: `${getChatBaseUrl()}/`,
  }),
  actions: {},
})

export default useApplicationStore
