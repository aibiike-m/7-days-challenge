import { createRouter, createWebHistory } from 'vue-router'
import TodayView from '@/views/TodayView.vue'
import CalendarView from '@/views/CalendarView.vue'
import ProfileView from '@/views/ProfileView.vue'
import AuthView from '@/views/AuthView.vue'

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{
			path: '/auth',
			name: 'Auth',
			component: AuthView,
			meta: { requiresAuth: false },
		},
		{
			path: '/today',
			name: 'Today',
			component: TodayView,
			meta: { requiresAuth: true },
		},
		{
			path: '/calendar',
			name: 'Calendar',
			component: CalendarView,
			meta: { requiresAuth: true },
		},
		{
			path: '/profile',
			name: 'Profile',
			component: ProfileView,
			meta: { requiresAuth: true },
		},
		{
			path: '/',
			redirect: '/today',
		},
	],
})

router.beforeEach((to, from, next) => {
	const token = localStorage.getItem('access_token')
	const requiresAuth = to.meta.requiresAuth

	if (requiresAuth && !token) {
		next({ path: '/auth', query: { redirect: to.fullPath } })
	} else if (to.path === '/auth' && token) {
		const redirect = to.query.redirect || '/today'
		next(redirect)
	} else {
		next()
	}
})

export default router
