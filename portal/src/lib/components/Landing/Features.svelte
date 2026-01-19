<script lang="ts">
	const features = [
		{
			icon: '🚀',
			title: 'Rápido y Eficiente',
			description: 'Optimizado para el mejor rendimiento y experiencia de usuario'
		},
		{
			icon: '🔒',
			title: 'Seguro',
			description: 'Autenticación robusta y protección de datos garantizada'
		},
		{
			icon: '🎨',
			title: 'Personalizable',
			description: 'Temas claros y oscuros para adaptarse a tus preferencias'
		}
	];
</script>

<section class="section section-features">
	<div class="section-container">
		<h2 class="title-section features-title">Características principales</h2>
		<div class="grid grid-auto-fit">
			{#each features as feature}
				<div class="card card-centered">
					<div class="feature-icon">{feature.icon}</div>
					<h3 class="feature-title">{feature.title}</h3>
					<p class="feature-description">{feature.description}</p>
				</div>
			{/each}
		</div>
	</div>
</section>
