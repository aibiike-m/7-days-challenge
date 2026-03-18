<template>
	<div class="not-found-view page-container">
		<div class="not-found-content">
			<div class="not-found-icon">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
					<path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-1.442c1.146-.573 2.437.463 2.126 1.706l-.709 2.836.042-.02a.75.75 0 01.67 1.34l-.04.022c-1.147.573-2.438-.463-2.127-1.706l.71-2.836-.042.02a.75.75 0 11-.671-1.34l.041-.022zM12 9a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd" />
				</svg>
			</div>

			<h1 class="not-found-code">404</h1>
			<p class="not-found-message">{{ $t('not_found.message') }}</p>

			<button class="btn-home" @click="goHome">
				{{ $t('not_found.go_home') }}
			</button>
		</div>
	</div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
	router.push('/today')
}
</script>

<style scoped lang="scss">
.not-found-view {
	max-width: 700px;
	padding-top: $spacing-responsive-md;
	padding-bottom: 100px;

	@include md {
		padding-top: $spacing-responsive-lg;
		padding-bottom: 120px;
	}

	@include xl {
		max-width: 800px;
	}
}

.not-found-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
	padding: $spacing-responsive-lg;

	@include md {
		padding: $spacing-responsive-xl;
	}
}

.not-found-icon {
	display: flex;
	justify-content: center;
	color: $text-muted;
	margin-bottom: $spacing-responsive-md;

	svg {
		width: 64px;
		height: 64px;

		@include md {
			width: 80px;
			height: 80px;
		}
	}

	@include md {
		margin-bottom: $spacing-responsive-lg;
	}
}

.not-found-code {
	font-size: 72px;
	font-weight: $font-weight-semibold;
	color: $primary;
	margin: 0 0 $spacing-responsive-sm;
	line-height: 1;

	@include md {
		font-size: 96px;
	}
}

.not-found-message {
	font-size: $font-size-responsive-base;
	color: $text-muted;
	margin: 0 0 $spacing-responsive-lg;

	@include md {
		font-size: $font-size-responsive-lg;
		margin-bottom: $spacing-responsive-xl;
	}
}

.btn-home {
	padding: $spacing-responsive-md $spacing-responsive-lg;
	background: $primary;
	color: $white;
	border: none;
	border-radius: $radius-md;
	font-size: $font-size-responsive-base;
	font-weight: $font-weight-semibold;
	cursor: pointer;
	transition: all 0.2s ease;

	&:hover {
		background: $primary-hover;
		transform: translateY(-2px);
		box-shadow: $shadow-sm;
	}
}
</style>