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
			if (data?.email) notify.error('errors.email_taken')
			else if (data?.password) notify.error('errors.password_weak')
			else notify.error('errors.validation')
			break
		case 401:
			notify.error('errors.invalid_credentials')
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
