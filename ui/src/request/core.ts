import axios, { AxiosHeaders, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import type { NProgress } from 'nprogress'
import { ref, type Ref, type WritableComputedRef } from 'vue'

import type { Result } from '@/request/Result'

type Loading = NProgress | Ref<boolean> | WritableComputedRef<boolean>

export type RequestContext = {
  token?: string | null
  language?: string
}

export function createRequestInstance(
  baseURL: string,
  timeout: number,
  getRequestContext: () => RequestContext,
) {
  const instance = axios.create({
    baseURL,
    withCredentials: false,
    timeout,
    headers: {},
  })

  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      if (config.headers === undefined) {
        config.headers = new AxiosHeaders()
      }
      if (config.url && config.url.startsWith('http')) {
        return config
      }

      const { token, language } = getRequestContext()
      if (language) {
        config.headers['Accept-Language'] = `${language}`
      }
      if (token) {
        config.headers['AUTHORIZATION'] = `Bearer ${token}`
      }
      return config
    },
    (err: unknown) => Promise.reject(err),
  )

  return instance
}

export function promise(
  request: Promise<any>,
  loading: Loading = ref(false),
): Promise<Result<any>> {
  return new Promise((resolve, reject) => {
    if ((loading as NProgress).start) {
      ;(loading as NProgress).start()
    } else {
      ;(loading as Ref<boolean>).value = true
    }

    request
      .then((response) => {
        if (response.status === 200) {
          resolve(response?.data || response)
        } else {
          reject(response?.data || response)
        }
      })
      .catch((error) => {
        reject(error)
      })
      .finally(() => {
        if ((loading as NProgress).start) {
          ;(loading as NProgress).done()
        } else {
          ;(loading as Ref<boolean>).value = false
        }
      })
  })
}

export function createRequestMethods(request: AxiosInstance) {
  const get = (
    url: string,
    params?: unknown,
    loading?: NProgress | Ref<boolean>,
    timeout?: number,
  ) => {
    return promise(request({ url, method: 'get', params, timeout }), loading)
  }

  const post = (
    url: string,
    data?: unknown,
    params?: unknown,
    loading?: NProgress | Ref<boolean>,
    timeout?: number,
  ) => {
    return promise(request({ url, method: 'post', data, params, timeout }), loading)
  }

  const put = (
    url: string,
    data?: unknown,
    params?: unknown,
    loading?: NProgress | Ref<boolean>,
    timeout?: number,
  ) => {
    return promise(request({ url, method: 'put', data, params, timeout }), loading)
  }

  const del = (
    url: string,
    params?: unknown,
    data?: unknown,
    loading?: NProgress | Ref<boolean>,
    timeout?: number,
  ) => {
    return promise(request({ url, method: 'delete', params, data, timeout }), loading)
  }

  return {
    get,
    post,
    put,
    del,
  }
}
