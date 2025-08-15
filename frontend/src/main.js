import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#216093',     // Blue
          secondary: '#001B48',   // Navy Blue
          accent: '#57949A',      // Teal
          error: '#DB162F',       // Red
          info: '#224870',        // Medium Blue
          success: '#2E933C',     // Green
          warning: '#E18331',     // Orange
          background: '#F9FAFA',  // Light Gray
          surface: '#FFFFFF',     // White
          'on-background': '#000000', // Black
          'on-surface': '#000000'
        }
      }
    }
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')