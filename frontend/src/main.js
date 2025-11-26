import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import '@/styles/main.scss'
import axios from 'axios'

axios.defaults.baseURL = 'http://127.0.0.1:8000'

axios.interceptors.request.use(config => {
	const token = localStorage.getItem('access_token')
	if (token) {
		config.headers.Authorization = `Bearer ${token}`
	}
	return config
})

const app = createApp(App)
app.use(router)
app.mount('#app')
