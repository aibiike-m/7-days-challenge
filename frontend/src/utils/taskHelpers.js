export function getTasksForDate(tasks, challenges, targetDate) {
	return tasks.filter(task => {
		const challenge = challenges.find(c => c.id === task.challenge_id)
		if (!challenge) return false

		const taskDate = new Date(challenge.start_date)
		taskDate.setDate(taskDate.getDate() + (task.day_number - 1))
		taskDate.setHours(0, 0, 0, 0)

		return isSameDay(taskDate, targetDate)
	})
}

export function isSameDay(d1, d2) {
	return (
		d1.getDate() === d2.getDate() &&
		d1.getMonth() === d2.getMonth() &&
		d1.getFullYear() === d2.getFullYear()
	)
}
