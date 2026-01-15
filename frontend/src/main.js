import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import i18n from './i18n'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import '@/styles/main.scss'
import '@/styles/toast-custom.scss'

const app = createApp(App)

const toastOptions = {
	transition: 'Vue-Toastification__fade', 
	maxToasts: 3,
	newestOnTop: true,
	position: 'top-right',
	timeout: 3000,
	hideProgressBar: false,
	closeOnClick: true,
	pauseOnFocusLoss: true,
	pauseOnHover: true,
	draggable: true,
	draggablePercent: 0.6,
	hideProgressBar: true, 
}


app.use(router)
app.use(i18n)
app.use(Toast, toastOptions)

app.mount('#app')
