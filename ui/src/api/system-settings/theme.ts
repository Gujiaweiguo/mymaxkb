import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import type { Ref } from 'vue'

export interface SystemBrandingSettings {
  theme: string
  icon: string
  loginLogo: string
  loginImage: string
  title: string
  slogan: string
}

export interface SystemBrandingUpdatePayload {
  theme: string
  icon: string | File
  loginLogo: string | File
  loginImage: string | File
  title: string
  slogan: string
}

const prefix = '/display'

/**
 * 查看外观设置
 */
const getThemeInfo: (loading?: Ref<boolean>) => Promise<Result<SystemBrandingSettings>> = (loading) => {
  return get(`${prefix}/info`, undefined, loading)
}

/**
 * 更新外观设置
 * @param 参数
 * * formData {
 *   theme
 *   icon
 *   loginLogo
 *   loginImage
 *   title
 *   slogan
 * }
 */
const postThemeInfo: (
  data: FormData | SystemBrandingUpdatePayload,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (
  data,
  loading,
) => {
  return put(`${prefix}/update`, data, undefined, loading)
}

export default {
  getThemeInfo,
  postThemeInfo
}
