import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'


const app = createApp(App)

// 挂到全局，组件内以 this.$http 使用；不设置 baseURL，/api 前缀由开发代理转发
app.config.globalProperties.$http = axios

app.use(router)

app.mount('#app')