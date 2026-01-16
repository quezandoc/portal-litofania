<script lang="ts">
	import './design.css';
	import Hero from '$lib/components/Landing/Hero.svelte';
	import Features from '$lib/components/Landing/Features.svelte';
	import About from '$lib/components/Landing/About.svelte';
	import CallToAction from '$lib/components/Landing/CallToAction.svelte';
	import Generate from '$lib/components/client-sections/GenerateFigure.svelte';
	import Visualize from '$lib/components/client-sections/VisualizeFigure.svelte';
</script>

<main class="landing-page">
	<Generate />
	<Visualize />
	<!-- <Hero/>
	<Features />
	<About />
	<CallToAction /> -->
</main>