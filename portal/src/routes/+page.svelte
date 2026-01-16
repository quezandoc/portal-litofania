<script lang="ts">
	import './design.css';
	import Hero from '$lib/components/Landing/Hero.svelte';
	import Features from '$lib/components/Landing/Features.svelte';
	import About from '$lib/components/Landing/About.svelte';
	import CallToAction from '$lib/components/Landing/CallToAction.svelte';
	import Generate from '$lib/components/client-sections/GenerateFigure.svelte';
</script>

<main class="landing-page">
	<Generate />
	<!-- <Hero/>
	<Features />
	<About />
	<CallToAction /> -->
</main>