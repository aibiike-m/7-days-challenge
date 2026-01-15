import { useToast } from 'vue-toastification'
import { useI18n } from 'vue-i18n'

export const useNotification = () => {
	const toast = useToast()
	const { t } = useI18n()

	return {
		success(messageKey) {
			toast.success(t(messageKey))
		},

		error(messageKey) {
			toast.error(t(messageKey))
		},

		warning(messageKey) {
			toast.warning(t(messageKey))
		},

		info(messageKey) {
			toast.info(t(messageKey))
		},
	}
}
