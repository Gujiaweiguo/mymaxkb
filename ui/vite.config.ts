import {fileURLToPath, URL} from 'node:url'
import type {ProxyOptions} from 'vite'
import {defineConfig, loadEnv, type Plugin} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import DefineOptions from 'unplugin-vue-define-options/vite'
import path from 'path'
import {createHtmlPlugin} from 'vite-plugin-html'
import fs from 'fs'
// import vueDevTools from 'vite-plugin-vue-devtools'
const envDir = './env'
// 自定义插件：重命名入口文件
const renameHtmlPlugin = (outDir: string, entry: string) => {
  return {
    name: 'rename-html',
    closeBundle: () => {
      const buildDir = path.resolve(__dirname, outDir)
      const oldFile = path.join(buildDir, entry)
      const newFile = path.join(buildDir, 'index.html')

      // 检查文件是否存在
      if (fs.existsSync(oldFile)) {
        // 删除已存在的 index.html
        if (fs.existsSync(newFile)) {
          fs.unlinkSync(newFile)
        }
        // 重命名文件
        fs.renameSync(oldFile, newFile)
      }
    },
  }
}

const normalizeEntryRedirectPlugin = (basePath: string, entry: string): Plugin => {
  const normalizedBasePath = basePath.endsWith('/') ? basePath : `${basePath}/`
  const malformedEntryPath = `${normalizedBasePath}.html`
  const validPaths = new Set([normalizedBasePath, malformedEntryPath])
  const targetLocation = `/${entry}`
  const shouldServeEntryForRoute = (requestUrl: string) => {
    if (!requestUrl.startsWith(normalizedBasePath)) {
      return false
    }

    const subPath = requestUrl.slice(normalizedBasePath.length)
    if (!subPath) {
      return false
    }

    if (subPath === 'api' || subPath.startsWith('api/')) {
      return false
    }

    if (subPath.includes('oss/file') || subPath.includes('oss/get_url')) {
      return false
    }

    const lastSegment = subPath.split('/').pop() || ''
    if (/\.[^/]+$/.test(lastSegment)) {
      return false
    }

    return true
  }

  return {
    name: 'normalize-entry-redirect',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const requestUrl = req.url ? req.url.split('?')[0] : ''
        if (!validPaths.has(requestUrl)) {
          if (shouldServeEntryForRoute(requestUrl)) {
            req.url = targetLocation
          }
          next()
          return
        }

        res.statusCode = 302
        res.setHeader('Location', targetLocation)
        res.end()
      })
    },
  }
}
// https://vite.dev/config/
export default defineConfig((conf: any) => {
  const mode = conf.mode
  const ENV = loadEnv(mode, envDir)
  const backendTarget = ENV.VITE_API_TARGET || 'http://127.0.0.1:3080'
  const devHost = ENV.VITE_DEV_HOST || '127.0.0.1'
  const proxyConf: Record<string, string | ProxyOptions> = {}
  proxyConf['/admin/api'] = {
    target: backendTarget,
    changeOrigin: true,
  }
  proxyConf['/chat/api'] = {
    target: backendTarget,
    changeOrigin: true,
  }
  proxyConf['/doc'] = {
    target: backendTarget,
    changeOrigin: true,
    rewrite: (path: string) => path.replace(ENV.VITE_BASE_PATH, '/'),
  }
  proxyConf['/schema'] = {
    target: backendTarget,
    changeOrigin: true,
    rewrite: (path: string) => path.replace(ENV.VITE_BASE_PATH, '/'),
  }
  proxyConf['/static'] = {
    target: backendTarget,
    changeOrigin: true,
    rewrite: (path: string) => path.replace(ENV.VITE_BASE_PATH, '/'),
  }

  // 前端静态资源转发到本身
  proxyConf[`^${ENV.VITE_BASE_PATH}.+\/oss\/file\/.*$`] = {
    target: backendTarget,
    changeOrigin: true,
  }
  // 前端静态资源转发到本身
  proxyConf[`^${ENV.VITE_BASE_PATH}oss\/file\/.*$`] = {
    target: backendTarget,
    changeOrigin: true,
  }
  proxyConf[`^${ENV.VITE_BASE_PATH}oss\/get_url\/.*$`] = {
    target: backendTarget,
    changeOrigin: true,
  }
  // 前端静态资源转发到本身
  proxyConf[ENV.VITE_BASE_PATH] = {
    target: `http://127.0.0.1:${ENV.VITE_APP_PORT}`,
    changeOrigin: true,
    rewrite: (path: string) => path.replace(ENV.VITE_BASE_PATH, '/'),
  }

  return {
    preflight: false,
    lintOnSave: false,
    base: './',
    envDir: envDir,
    plugins: [
      vue(),
      vueJsx(),
      DefineOptions(),
      createHtmlPlugin({template: ENV.VITE_ENTRY}),
      normalizeEntryRedirectPlugin(ENV.VITE_BASE_PATH, ENV.VITE_ENTRY),
      renameHtmlPlugin(`dist${ENV.VITE_BASE_PATH}`, ENV.VITE_ENTRY),
    ],
    server: {
      cors: true,
      host: devHost,
      port: Number(ENV.VITE_APP_PORT),
      strictPort: true,
      proxy: proxyConf,
    },
    build: {
      outDir: `dist${ENV.VITE_BASE_PATH}`,
      rollupOptions: {
        input: ENV.VITE_ENTRY,
      },
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  }
})
