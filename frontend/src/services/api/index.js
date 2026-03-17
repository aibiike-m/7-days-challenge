import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/'

const api = axios.create({
	baseURL: API_URL,
	timeout: 60000,
})

api.interceptors.request.use(config => {
	const token = localStorage.getItem('access_token')
	if (token) {
		config.headers.Authorization = `Bearer ${token}`
	}
	return config
})

api.interceptors.response.use(
	response => response,
	async error => {
		if (error.response?.status === 401 && !error.config._retry) {
			error.config._retry = true
			try {
				const refresh = localStorage.getItem('refresh_token')
				if (refresh) {
					const res = await axios.post(`${API_URL}token/refresh/`, { refresh })
					const newAccess = res.data.access
					localStorage.setItem('access_token', newAccess)
					error.config.headers.Authorization = `Bearer ${newAccess}`
					return api(error.config)
				}
			} catch (refreshError) {
				localStorage.clear()
				window.location.href = '/auth'
			}
		}
		return Promise.reject(error)
	}
)

api.getChallenges = () => api.get('challenges/')
api.getAllTasks = () => api.get('tasks/')
// api.getTasks = challengeId => api.get(`tasks/?challenge=${challengeId}`)
api.completeTask = taskId => api.post(`tasks/${taskId}/complete/`)
api.uncompleteTask = taskId => api.post(`tasks/${taskId}/uncomplete/`)
api.getTasks = challengeId => api.get(`tasks/?challenge_ids=${challengeId}`)
api.bulkDeleteChallenges = ids =>
	api.delete('challenges/bulk-delete/', { data: { ids } })
api.cancelEmailChange = token =>
	api.get(`users/cancel-email-change/?token=${token}`)
export default api
