export function handleApiError(error, notify, customHandlers = {}) {
	if (!error.response) {
		notify.error('errors.network')
		return
	}

	const status = error.response.status
	const data = error.response.data

	if (customHandlers[status]) {
		customHandlers[status](data)
		return
	}

	switch (status) {
		case 400:
			if (data?.password && Array.isArray(data.password)) {
				const passwordError = data.password[0].toLowerCase()

				if (passwordError.includes('incorrect')) {
					notify.error('errors.invalid_password')
				}
				else if (
					passwordError.includes('similar') &&
					passwordError.includes('email')
				) {
					notify.error('errors.password_similar_to_email')
				} else if (
					passwordError.includes('similar') &&
					passwordError.includes('username')
				) {
					notify.error('errors.password_similar_to_username')
				} else if (passwordError.includes('too common')) {
					notify.error('errors.password_too_common')
				} else if (passwordError.includes('entirely numeric')) {
					notify.error('errors.password_only_numbers')
				} else if (passwordError.includes('too short')) {
					notify.error('errors.password_too_short')
				} else {
					notify.error('errors.password_weak')
				}
			}
			else if (data?.email) {
				notify.error('errors.email_taken')
			}
			else if (data?.username) {
				notify.error('errors.username_taken')
			}
			else if (data?.error) {
				const errorKey = `errors.${data.error.toLowerCase().replace(/ /g, '_')}`
				notify.error(errorKey)
			}
			else {
				notify.error('errors.validation')
			}
			break

		case 401:
			notify.error('errors.unauthorized')
			break

		case 403:
			notify.error('errors.forbidden')
			break

		case 404:
			notify.error('errors.not_found')
			break

		case 500:
			notify.error('errors.server')
			break

		default:
			notify.error('errors.unknown')
	}
}
