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
