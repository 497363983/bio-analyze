// .vitepress/theme/index.ts
import DefaultTheme from 'vitepress/theme'
import ParamTable from './components/ParamTable.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ParamTable', ParamTable)
  }
}
