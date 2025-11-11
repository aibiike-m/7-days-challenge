import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChallengeView from '../views/ChallengeView.vue'

const routes = [
	{ path: '/', name: 'home', component: HomeView },
	{ path: '/challenge/:id', name: 'challenge', component: ChallengeView },
	{ path: '/active', name: 'active', component: ChallengeView }, 
]

const router = createRouter({
	history: createWebHistory(),
	routes,
})

export default router
