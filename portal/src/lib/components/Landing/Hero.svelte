<script lang="ts">
	import { goto } from '$app/navigation';
</script>

<section class="hero">
	<div class="hero-content">
		<h1 class="title-hero">Software a medida que impulsa tu productividad</h1>
		<p class="subtitle hero-subtitle">
			Diseñamos y desarrollamos soluciones escalables que se adaptan a tus procesos específicos y conectan con tus clientes.
		</p>
		<div class="hero-actions">
			<button 
				onclick={() => goto('/login')} 
				class="btn btn-primary"
			>
				Comienza tu proyecto
			</button>
		</div>
	</div>
</section>
