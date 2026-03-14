import { getSidebar } from '../utils/sidebar'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const docRoot = path.resolve(__dirname, '../../')

export const enConfig = {
  label: 'English',
  lang: 'en',
  link: '/',
  title: 'Bio Analyze',
  description: 'An extensible bioinformatics analysis toolkit',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/introduction' },
      {
        text: 'Modules',
        items: getSidebar(docRoot, 'modules', 'Modules')[0]?.items || []
      },
      { text: 'Developer', link: '/develop/architecture' }
    ],
    sidebar: {
      '/guide/': getSidebar(docRoot, 'guide', 'Guide'),
      '/modules/': getSidebar(docRoot, 'modules', 'Modules'),
      '/develop/': [
        ...getSidebar(docRoot, 'develop', 'Developer Guide'),
        ...getSidebar(docRoot, 'develop/modules', 'Modules (Dev)')
      ]
    },
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present Bio Analyze Contributors'
    }
  }
}
