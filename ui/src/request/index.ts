import { MsgError } from '@/utils/message'
import useStore from '@/stores'
import router from '@/router'

import { createDownloadMethods } from '@/request/download'
import { createRequestInstance, createRequestMethods } from '@/request/core'
import { createPostStream } from '@/request/stream'
import { socket } from '@/request/websocket'

const getRequestContext = () => {
    const { user, login } = useStore()
    return {
      token: login.getToken(),
      language: user.getLanguage(),
    }
}

const instance = createRequestInstance(
  (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api',
  1800000,
  getRequestContext,
)

instance.interceptors.response.use(
  (response: any) => {
    if (response.data) {
      if (response.data.code !== 200 && !(response.data instanceof Blob)) {
        if (response.config.url.includes('/application/authentication')) {
          return Promise.reject(response.data)
        }
        if (
          !response.config.url.includes('/valid') &&
          !response.config.url.includes('/tool/debug')
        ) {
          MsgError(response.data.message)
          return Promise.reject(response.data)
        }
      }
    }
    return response
  },
  (err: any) => {
    if (err.code === 'ECONNABORTED') {
      MsgError(err.message)
      console.error(err)
    }
    if (err.response?.status === 404) {
      if (!err.response.config.url.includes('/application/authentication')) {
        router.push('/404 ')
      }
    }
    if (err.response?.status === 401) {
      if (
        !err.response.config.url.includes('chat/open') &&
        !err.response.config.url.includes('application/profile')
      ) {
        router.push({ name: 'login' })
      }
    }

    if (err.response?.status === 403 && !err.response.config.url.includes('chat/open')) {
      MsgError(
        err.response.data && err.response.data.message
          ? err.response.data.message
          : 'No permission to access',
      )
    }
    return Promise.reject(err)
  },
)

export const request = instance
export const { get, post, put, del } = createRequestMethods(request)
export const { exportExcel, exportFile, exportExcelPost, exportFilePost, download } =
  createDownloadMethods(request)
export const postStream = createPostStream(getRequestContext)
export { socket }

export default instance
