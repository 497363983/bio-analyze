import { defineConfig } from 'vitepress'
import { enConfig } from './locales/en'
import { zhConfig } from './locales/zh'
import { footer } from './configs/footer'

export default defineConfig({
  title: "Bio Analyze",
  description: "An extensible bioinformatics analysis toolkit",

  themeConfig: {
    outline: {
        level: [2, 3],
        label: 'On this page'
    },
    logo: '/logo.svg',
    socialLinks: [],
    search: {
      provider: 'local'
    },
    footer,
  },

  locales: {
    root: enConfig,
    zh: zhConfig
  },
})
