<script lang="ts">
	import "./design.css";
	import Generate from "$lib/components/client-sections/GenerateFigure.svelte";
	import Visualize from "$lib/components/client-sections/VisualizeFigure.svelte";
	import LoadingOverlay from "$lib/components/ui/LoadingOverlay.svelte";
	import { generateModel, generateTextBase } from "$lib/services/api";

	let loading = $state(false);

	let stl = $state<{
		figura: Blob | null;
		base: Blob | null;
	}>({
		figura: null,
		base: null,
	});

	async function onGenerar(
		event: CustomEvent<{
			imagen?: Blob;
			texto?: string;
		}>,
	) {
		loading = true;
		const { imagen, texto } = event.detail;

		if (!imagen || !texto) return;

		try {
			stl.figura = await generateModel({
				file: imagen,
				filename: "litho.png",
			});

			stl.base = await generateTextBase({
				texto,
			});
		} catch (e) {
			loading = false;
			console.error(e);
		} finally {
			loading = false;
		}
	}
</script>

<main>
	<LoadingOverlay show={loading} text="Generando STL…" />
	<div id="generator">
		<Generate on:generar={onGenerar} />
	</div>
	<div id="visualizer">
		<Visualize stlFigura={stl.figura} stlBase={stl.base} />
	</div>
</main>
