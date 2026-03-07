import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createRouter, createWebHistory } from 'vue-router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createPinia } from 'pinia'

const app = createApp(App)

// Basic Router Setup
const routes = [
    { path: '/', component: () => import('./views/Home.vue') },
    { path: '/login', component: () => import('./views/Login.vue') },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Register Icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.use(createPinia())
app.mount('#app')
