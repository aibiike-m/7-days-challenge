import { createRouter, createWebHistory } from 'vue-router'
import TodayView from '@/views/TodayView.vue'
import CalendarView from '@/views/CalendarView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SettingsView from '@/views/SettingsView.vue'
import AuthView from '@/views/AuthView.vue'
import ConfirmAccountDeletionView from '@/views/ConfirmAccountDeletionView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'

const routes = [
	{
		path: '/',
		redirect: '/today',
	},
	{
		path: '/today',
		name: 'today',
		component: TodayView,
		meta: { requiresAuth: true },
	},
	{
		path: '/calendar',
		name: 'calendar',
		component: CalendarView,
		meta: { requiresAuth: true },
	},
	{
		path: '/profile',
		name: 'profile',
		component: ProfileView,
		meta: { requiresAuth: true },
	},
	{
		path: '/settings',
		name: 'settings',
		component: SettingsView,
		meta: { requiresAuth: true },
	},
	{
		path: '/auth',
		name: 'auth',
		component: AuthView,
	},
	{
		path: '/confirm-account-deletion',
		name: 'confirm-account-deletion',
		component: ConfirmAccountDeletionView,
	},
	{
		path: '/reset-password',
		name: 'reset-password',
		component: ResetPasswordView,
	},
]

const router = createRouter({
	history: createWebHistory(),
	routes,
})

router.beforeEach((to, from, next) => {
	const token = localStorage.getItem('access_token')

	if (to.meta.requiresAuth && !token) {
		next('/auth')
	} else if (to.path === '/auth' && token) {
		next('/today')
	} else {
		next()
	}
})

export default router
