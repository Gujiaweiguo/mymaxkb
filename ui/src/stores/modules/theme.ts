import { defineStore } from 'pinia'
import { useElementPlusTheme } from 'use-element-plus-theme'
import ThemeApi from '@/api/system-settings/theme'
import type { Ref } from 'vue'
import { defaultPlatformSetting, defaultSetting } from '@/utils/theme'

type BrandingAssetKey = 'icon' | 'loginLogo' | 'loginImage'
type BrandingAssetUrlState = Record<BrandingAssetKey, string>

interface SetThemeOptions {
  persist?: boolean
}

export interface themeStateTypes {
  themeInfo: any
  brandingAssetUrls: BrandingAssetUrlState
}

const defalueColor = '#3370FF'
const themeCacheKey = 'MaxKB-theme-info'
const brandingAssetKeys: BrandingAssetKey[] = ['icon', 'loginLogo', 'loginImage']

const defaultFaviconHref =
  typeof document !== 'undefined'
    ? ((document.querySelector("link[rel*='icon']") as HTMLLinkElement | null)?.href ?? '')
    : ''

const createBrandingAssetUrlState = (): BrandingAssetUrlState => ({
  icon: '',
  loginLogo: '',
  loginImage: '',
})

const getThemeDefaults = () => ({
  theme: defalueColor,
  ...defaultSetting,
  ...defaultPlatformSetting,
})

const normalizeThemeInfo = (data?: any) => {
  return {
    ...getThemeDefaults(),
    ...(data || {}),
  }
}

const brandingAssetSources: Partial<Record<BrandingAssetKey, string | File>> = {}
const brandingAssetUrls = createBrandingAssetUrlState()

const ensureFaviconElement = () => {
  if (typeof document === 'undefined') {
    return null
  }

  const existingIconElement = document.querySelector("link[rel*='icon']") as HTMLLinkElement | null

  if (existingIconElement) {
    return existingIconElement
  }

  const iconElement = document.createElement('link')
  iconElement.rel = 'icon'
  document.head.appendChild(iconElement)
  return iconElement
}

const getSerializableThemeInfo = (data?: any) => {
  const nextThemeInfo = normalizeThemeInfo(data)

  brandingAssetKeys.forEach((key) => {
    nextThemeInfo[key] = typeof nextThemeInfo[key] === 'string' ? nextThemeInfo[key] : ''
  })

  return nextThemeInfo
}

const getStoredThemeInfo = () => {
  if (typeof window === 'undefined') {
    return null
  }

  const cachedThemeInfo = window.localStorage.getItem(themeCacheKey)

  if (!cachedThemeInfo) {
    return null
  }

  try {
    return normalizeThemeInfo(JSON.parse(cachedThemeInfo))
  } catch (error) {
    window.localStorage.removeItem(themeCacheKey)
    return null
  }
}

const cacheThemeInfo = (data?: any) => {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(themeCacheKey, JSON.stringify(getSerializableThemeInfo(data)))
}

const revokeBrandingAssetUrl = (key: BrandingAssetKey) => {
  const previousSource = brandingAssetSources[key]
  const previousUrl = brandingAssetUrls[key]

  if (previousSource && typeof previousSource !== 'string' && previousUrl) {
    URL.revokeObjectURL(previousUrl)
  }
}

const resolveBrandingAssetUrl = (key: BrandingAssetKey, value?: string | File) => {
  if (brandingAssetSources[key] === value) {
    return brandingAssetUrls[key]
  }

  revokeBrandingAssetUrl(key)
  brandingAssetSources[key] = value
  brandingAssetUrls[key] = !value ? '' : typeof value === 'string' ? value : URL.createObjectURL(value)

  return brandingAssetUrls[key]
}

const syncBrandingAssetUrls = (data?: any) => {
  brandingAssetKeys.forEach((key) => {
    resolveBrandingAssetUrl(key, data?.[key])
  })

  return { ...brandingAssetUrls }
}

const applyThemeMeta = (data: any, iconHref?: string) => {
  if (typeof document === 'undefined') {
    return
  }

  document.title = data?.title || defaultSetting.title

  const iconElement = ensureFaviconElement()

  if (iconElement) {
    iconElement.href = iconHref || defaultFaviconHref
  }
}

const applyThemeColor = (themeColor?: string) => {
  const { changeTheme } = useElementPlusTheme(themeColor || defalueColor)

  changeTheme(themeColor || defalueColor)
}

const initialThemeInfo = getStoredThemeInfo() || normalizeThemeInfo()
const initialBrandingAssetUrls = syncBrandingAssetUrls(initialThemeInfo)

applyThemeMeta(initialThemeInfo, initialBrandingAssetUrls.icon)

const useThemeStore = defineStore('theme', {
  state: (): themeStateTypes => ({
    themeInfo: { ...initialThemeInfo },
    brandingAssetUrls: { ...initialBrandingAssetUrls },
  }),
  actions: {
    isDefaultTheme() {
      return !this.themeInfo?.theme || this.themeInfo?.theme === defalueColor
    },

    getBrandingAssetUrl(key: BrandingAssetKey) {
      return this.brandingAssetUrls[key] || ''
    },

    hydrateTheme() {
      this.setTheme(this.themeInfo)
    },

    setTheme(data?: any, options: SetThemeOptions = {}) {
      const nextThemeInfo = normalizeThemeInfo(data || this.themeInfo)

      applyThemeColor(nextThemeInfo.theme)
      this.themeInfo = { ...nextThemeInfo }
      this.brandingAssetUrls = syncBrandingAssetUrls(nextThemeInfo)
      applyThemeMeta(nextThemeInfo, this.brandingAssetUrls.icon)

      if (options.persist) {
        cacheThemeInfo(nextThemeInfo)
      }
    },

    async theme(loading?: Ref<boolean>) {
      return await ThemeApi.getThemeInfo(loading).then((ok) => {
        this.setTheme(ok.data || {}, { persist: true })
      })
    },
  },
})

export default useThemeStore
