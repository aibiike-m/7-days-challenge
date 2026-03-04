import axios from 'axios'

const api = axios.create({
	baseURL: 'http://localhost:8000/api/',
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
				const refresh = localStorage.getItem('refresh')
				if (refresh) {
					const res = await axios.post(
						'http://localhost:8000/api/token/refresh/',
						{ refresh }
					)
					localStorage.setItem('access_token', res.data.access)
					error.config.headers.Authorization = `Bearer ${res.data.access}`
					return api(error.config)
				}
			} catch (refreshError) {
				localStorage.removeItem('access_token')
				localStorage.removeItem('refresh')
				window.location.href = '/auth'
			}
		}
		return Promise.reject(error)
	}
)


api.getChallenges = () => api.get('challenges/')
api.getAllTasks = () => api.get('tasks/')
api.getTasks = challengeId => api.get(`challenges/${challengeId}/tasks/`)
api.updateTaskStatus = (taskId, isCompleted) => api.patch(`tasks/${taskId}/`, { is_completed: isCompleted })
api.deleteChallenge = id => api.delete(`challenges/${id}/`)
api.getTasksByChallenge = challengeId =>
	api.get(`challenges/${challengeId}/tasks/`)

export default api
