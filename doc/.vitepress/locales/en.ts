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
      {
        text: 'Developer',
        items: [
          { text: 'Architecture', link: '/develop/architecture' },
          { text: 'Environment', link: '/develop/environment' },
          { text: 'Code Style', link: '/develop/standards/code-style' },
          { text: 'Plugin Development', link: '/develop/plugins' }
        ]
      }
    ],
    sidebar: {
      '/guide/': getSidebar(docRoot, 'guide', 'Guide'),
      '/modules/': getSidebar(docRoot, 'modules', 'Modules'),
      '/develop/': [
        ...getSidebar(docRoot, 'develop', 'Developer Guide'),
        ...getSidebar(docRoot, 'develop/modules', 'Modules (Dev)')
      ]
    }
  }
}
