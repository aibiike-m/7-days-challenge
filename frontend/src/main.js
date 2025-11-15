import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.scss' 
import axios from 'axios'

createApp(App).use(router).mount('#app')

axios.defaults.withCredentials = true
axios.defaults.baseURL = 'http://127.0.0.1:8000'

axios.interceptors.request.use(config => {
	const token = localStorage.getItem('access_token')
	if (token) {
		config.headers.Authorization = `Bearer ${token}`
	}
	return config
})