import type { AxiosInstance } from 'axios'
import type { NProgress } from 'nprogress'
import type { Ref } from 'vue'

import { MsgError } from '@/utils/message'
import { promise } from '@/request/core'

function triggerDownload(blob: Blob, fileName: string) {
  const link = document.createElement('a')
  link.href = window.URL.createObjectURL(blob)
  link.download = fileName
  link.click()
  window.URL.revokeObjectURL(link.href)
}

function extractFilename(contentDisposition: string) {
  if (!contentDisposition) return null

  const urlEncodedMatch =
    contentDisposition.match(/filename=([^;]*)/i) ||
    contentDisposition.match(/filename\*=UTF-8''([^;]*)/i)
  if (urlEncodedMatch && urlEncodedMatch[1]) {
    try {
      return decodeURIComponent(urlEncodedMatch[1].replace(/"/g, ''))
    } catch (e) {
      console.error('解码URL编码文件名失败:', e)
    }
  }

  const base64Part = contentDisposition.match(/=\?utf-8\?b\?(.*?)\?=/i)?.[1]
  if (base64Part) {
    try {
      const decoded = decodeURIComponent(escape(atob(base64Part)))
      const filenameMatch = decoded.match(/filename="(.*?)"/i)
      return filenameMatch ? filenameMatch[1] : null
    } catch (e) {
      console.error('解码Base64文件名失败:', e)
    }
  }

  return null
}

function createFileTransform(defaultFileName: string, onFilename: (fileName: string) => void) {
  return [
    function (data: Blob, headers: Record<string, string>) {
      if (data.type === 'application/json') {
        data.text().then((text: string) => {
          try {
            const json = JSON.parse(text)
            MsgError(json.message || text)
          } catch {
            MsgError(text)
          }
        })
        throw new Error('Response is not a valid file')
      }

      const contentDisposition = headers['content-disposition']
      onFilename(extractFilename(contentDisposition) || defaultFileName)
      return data
    },
  ]
}

export function createDownloadMethods(request: AxiosInstance) {
  const exportExcel = (
    fileName: string,
    url: string,
    params: any,
    loading?: NProgress | Ref<boolean>,
  ): Promise<any> => {
    return promise(request({ url, method: 'get', params, responseType: 'blob' }), loading).then(
      (res: any) => {
        if (res) {
          triggerDownload(
            new Blob([res], {
              type: 'application/vnd.ms-excel',
            }),
            fileName,
          )
        }
        return true
      },
    )
  }

  const exportFile = (
    fileName: string,
    url: string,
    params: any,
    loading?: NProgress | Ref<boolean>,
  ): Promise<any> => {
    let resolvedFileName = fileName

    return promise(
      request({
        url,
        method: 'get',
        params,
        responseType: 'blob',
        transformResponse: createFileTransform(fileName, (nextFileName) => {
          resolvedFileName = nextFileName
        }),
      }),
      loading,
    )
      .then((res: any) => {
        if (res) {
          triggerDownload(
            new Blob([res], {
              type: 'application/octet-stream',
            }),
            resolvedFileName,
          )
        }
        return true
      })
      .catch(() => {})
  }

  const exportExcelPost = (
    fileName: string,
    url: string,
    params: any,
    data: any,
    loading?: NProgress | Ref<boolean>,
  ): Promise<any> => {
    return promise(
      request({
        url,
        method: 'post',
        params,
        data,
        responseType: 'blob',
      }),
      loading,
    ).then((res: any) => {
      if (res) {
        triggerDownload(
          new Blob([res], {
            type: 'application/vnd.ms-excel',
          }),
          fileName,
        )
      }
      return true
    })
  }

  const exportFilePost = (
    fileName: string,
    url: string,
    params: any,
    data: any,
    loading?: NProgress | Ref<boolean>,
  ): Promise<any> => {
    let resolvedFileName = fileName

    return promise(
      request({
        url,
        method: 'post',
        params,
        data,
        responseType: 'blob',
        transformResponse: createFileTransform(fileName, (nextFileName) => {
          resolvedFileName = nextFileName
        }),
      }),
      loading,
    )
      .then((res: any) => {
        if (res) {
          triggerDownload(
            new Blob([res], {
              type: 'application/octet-stream',
            }),
            resolvedFileName,
          )
        }
        return true
      })
      .catch(() => {})
  }

  const download = (
    url: string,
    method: string,
    data?: any,
    params?: any,
    loading?: NProgress | Ref<boolean>,
  ): Promise<any> => {
    return promise(request({ url, method, data, params, responseType: 'blob' }), loading)
  }

  return {
    exportExcel,
    exportFile,
    exportExcelPost,
    exportFilePost,
    download,
  }
}
