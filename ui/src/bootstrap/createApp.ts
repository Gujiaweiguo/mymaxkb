import '@/styles/index.scss'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enUs from 'element-plus/es/locale/lang/en'
import zhTW from 'element-plus/es/locale/lang/zh-tw'
import { createApp, type App as VueApp } from 'vue'
import { createPinia, type Pinia } from 'pinia'
import type { Router } from 'vue-router'
import { getDefaultWhiteList } from 'xss'
import { config, XSSPlugin } from 'md-editor-v3'
import screenfull from 'screenfull'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import mermaid from 'mermaid'
import highlight from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

import App from '@/App.vue'
import i18n from '@/locales'
import Components from '@/components'
import directives from '@/directives'

config({
  editorExtensions: {
    highlight: {
      instance: highlight,
    },
    screenfull: {
      instance: screenfull,
    },
    katex: {
      instance: katex,
    },
    cropper: {
      instance: Cropper,
    },
    mermaid: {
      instance: mermaid,
    },
  },
  markdownItPlugins(plugins) {
    return [
      ...plugins,
      {
        type: 'xss',
        plugin: XSSPlugin,
        options: {
          xss() {
            return {
              whiteList: Object.assign({}, getDefaultWhiteList(), {
                video: ['src', 'controls', 'width', 'height', 'preload', 'playsinline'],
                source: ['src', 'type'],
                input: ['class', 'disabled', 'type', 'checked'],
                iframe: [
                  'class',
                  'width',
                  'height',
                  'src',
                  'title',
                  'border',
                  'frameborder',
                  'framespacing',
                  'allow',
                  'allowfullscreen',
                ],
              }),
              onTagAttr: (tag: string, name: string, value: string) => {
                if (tag === 'video') {
                  if (name === 'autoplay') return ''

                  if (name === 'preload' && !['none', 'metadata'].includes(value)) {
                    return 'preload="metadata"'
                  }
                }
                return undefined
              },
            }
          },
        },
      },
    ]
  },
})

const localeMap: Record<string, typeof zhCn> = {
  'zh-CN': zhCn,
  'zh-Hant': zhTW,
  'en-US': enUs,
}

export function createConfiguredApp(router: Router): { app: VueApp; pinia: Pinia } {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  for (const [key, component] of Object.entries(ElementPlusIcons)) {
    app.component(key, component)
  }

  app.use(ElementPlus, {
    locale: localeMap[localStorage.getItem('MaxKB-locale') || navigator.language || 'en-US'],
  })
  app.use(directives)
  app.use(router)
  app.use(i18n)
  app.use(Components)

  return { app, pinia }
}
