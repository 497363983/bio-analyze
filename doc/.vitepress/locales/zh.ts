import { getSidebar } from '../utils/sidebar'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const docRoot = path.resolve(__dirname, '../../')

export const zhConfig = {
  label: '简体中文',
  lang: 'zh',
  link: '/zh/',
  title: 'Bio Analyze',
  description: '一个可拓展的生物信息学分析工具箱',
  themeConfig: {
    nav: [
      { text: '首页', link: '/zh/' },
      { text: '指南', link: '/zh/guide/introduction' },
      {
        text: '模块',
        items: getSidebar(docRoot, 'zh/modules', '模块')[0]?.items || []
      },
      { text: '开发者', link: '/zh/develop/architecture' }
    ],
    sidebar: {
      '/zh/guide/': getSidebar(docRoot, 'zh/guide', '指南'),
      '/zh/modules/': getSidebar(docRoot, 'zh/modules', '模块'),
      '/zh/develop/': [
        ...getSidebar(docRoot, 'zh/develop', '开发指南'),
        ...getSidebar(docRoot, 'zh/develop/modules', '模块开发')
      ]
    },
    docFooter: {
      prev: '上一页',
      next: '下一页'
    },
    outline: {
      label: '页面导航'
    },
    lastUpdated: {
      text: '最后更新于'
    },
    darkModeSwitchLabel: '外观',
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '返回顶部',
    langMenuLabel: '多语言'
  }
}
