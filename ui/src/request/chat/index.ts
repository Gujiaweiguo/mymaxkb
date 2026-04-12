import { MsgError } from '@/utils/message'
import useStore from '@/stores'

import { createDownloadMethods } from '@/request/download'
import { createRequestInstance, createRequestMethods } from '@/request/core'
import { createPostStream } from '@/request/stream'
import { socket } from '@/request/websocket'

const getRequestContext = () => {
    const { chatUser } = useStore()
    return {
      token: chatUser.getToken(),
      language: chatUser.getLanguage(),
    }
}

const instance = createRequestInstance(
  (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/chat') + '/api',
  600000,
  getRequestContext,
)

instance.interceptors.response.use(
  (response: any) => {
    if (response.data) {
      if (response.data.code !== 200 && !(response.data instanceof Blob)) {
        MsgError(response.data.message)
        return Promise.reject(response.data)
      }
    }
    return response
  },
  (err: any) => {
    if (err.code === 'ECONNABORTED') {
      MsgError(err.message)
      console.error(err)
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
