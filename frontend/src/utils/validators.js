export const validatePassword = password => {
	const pwd = password || ''
	const minLength = pwd.length >= 8
	const notOnlyNumbers = /[a-zA-Zа-яА-Я!@#$%^&*(),.?":{}|<>]/.test(pwd)

	return {
		minLength,
		notOnlyNumbers,
		isValid: minLength && notOnlyNumbers,
	}
}

export const validateEmail = email => {
	const em = email || ''
	const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)
	return { isValid }
}