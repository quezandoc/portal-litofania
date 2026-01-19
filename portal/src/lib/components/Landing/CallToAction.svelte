<script lang="ts">
	import { goto } from '$app/navigation';
	let { onOpenDrawer }: { onOpenDrawer?: () => void } = $props();
</script>

<section class="section bg-gradient-accent">
	<div class="section-container-sm">
		<div class="cta-content">
			<h2 class="cta-title">¿Listo para comenzar?</h2>
			<p class="cta-text">
				Inicia sesión y descubre todo lo que puedes hacer con Quezan SVK
			</p>
			<button onclick={() => onOpenDrawer ? onOpenDrawer() : goto('/login')} class="btn btn-lg btn-secondary">
				Acceder ahora
			</button>
		</div>
	</div>
</section>
