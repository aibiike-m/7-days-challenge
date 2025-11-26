import { createRouter, createWebHistory } from 'vue-router'
import TodayView from '@/views/TodayView.vue'
import CalendarView from '@/views/CalendarView.vue'
import ProfileView from '@/views/ProfileView.vue'
import AuthView from '@/views/AuthView.vue'

const routes = [
	{ path: '/', redirect: '/today' },
	{ path: '/today', component: TodayView },
	{ path: '/calendar', component: CalendarView },
	{ path: '/profile', component: ProfileView },
	{ path: '/auth', component: AuthView },
]

export default createRouter({
	history: createWebHistory(),
	routes,
})
