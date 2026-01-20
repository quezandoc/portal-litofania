<script lang="ts">
	const {
		show,
		text = "Procesando…"
	} = $props<{
		show: boolean;
		text?: string;
	}>();
</script>

{#if show}
	<div class="overlay">
		<div class="panel">
			<div class="spinner"></div>
			<p class="label">{text}</p>
		</div>
	</div>
{/if}

<style>
	/* === OVERLAY === */
	.overlay {
		position: fixed;
		inset: 0;
		z-index: 9999;

		display: flex;
		align-items: center;
		justify-content: center;

		background-color: rgba(0, 0, 0, 0.25);
		backdrop-filter: blur(4px);

		pointer-events: all;
	}

	/* === PANEL === */
	.panel {
		background-color: var(--bg-primary);
		border-radius: 1rem;
		padding: 2rem 2.5rem;
		min-width: 240px;

		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;

		box-shadow:
			0 10px 30px rgba(0, 0, 0, 0.15),
			inset 0 0 0 1px var(--bg-secondary);
	}

	/* === SPINNER === */
	.spinner {
		width: 44px;
		height: 44px;

		border-radius: 50%;
		border: 4px solid var(--bg-secondary);
		border-top-color: var(--color-primary-500);

		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	/* === TEXT === */
	.label {
		font-size: 0.95rem;
		font-weight: 500;
		color: var(--text-primary);
	}
</style>
