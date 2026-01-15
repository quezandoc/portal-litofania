<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Alert, AlertDescription, AlertTitle } from '$lib/components/ui/alert';
	import { generateModel as apiGenerateModel } from '$lib/api';
	import { obtenerMascaras, dibujarMascara } from '$lib/masks';
	import STLViewer from '$lib/components/STLViewer.svelte';
	import { AlertCircle, Download, Zap, CheckCircle } from '@lucide/svelte';

	// Estado de la app
	let selectedShape: 'Corazón' | 'Círculo' | 'Cuadrado' = 'Corazón';
	let frameWidth: number = 3.0;
	let zoom: number = 1.2;
	let offsetX: number = 0;
	let offsetY: number = 0;
	let uploadedFile: File | null = null;
	let previewUrl: string | null = null;
	let isLoading: boolean = false;
	let modelUrl: string | null = null;
	let errorMessage: string | null = null;
	let imagePreviewCanvas: HTMLCanvasElement | null = null;

	const shapes = ['Corazón', 'Círculo', 'Cuadrado'] as const;

	// Actualizar previsualización combinada (máscara + imagen)
	function actualizarPreviewCombinada() {
		if (!imagePreviewCanvas || !previewUrl) return;

		const img = new Image();
		img.onload = () => {
			const ctx = imagePreviewCanvas!.getContext('2d');
			if (!ctx) return;

			// Limpiar canvas
			ctx.fillStyle = 'white';
			ctx.fillRect(0, 0, 450, 450);

			// Dibujar máscara como fondo
			try {
				const { maskFrame, maskLitho } = obtenerMascaras(selectedShape, 450, frameWidth);
				const imageData = ctx.createImageData(450, 450);
				const data = imageData.data;

				for (let i = 0; i < 450 * 450; i++) {
					const idx = i * 4;
					if (maskLitho[i]) {
						data[idx] = 50;
						data[idx + 1] = 50;
						data[idx + 2] = 50;
					} else if (maskFrame[i]) {
						data[idx] = 200;
						data[idx + 1] = 200;
						data[idx + 2] = 200;
					} else {
						data[idx] = 255;
						data[idx + 1] = 255;
						data[idx + 2] = 255;
					}
					data[idx + 3] = 255;
				}
				ctx.putImageData(imageData, 0, 0);
			} catch (error) {
				console.error('Error dibujando máscara:', error);
			}

			// Dibujar imagen con desplazamiento
			const RES_PX_MM = 5.0;
			const PIXELS = 450;
			const scaledWidth = Math.round(PIXELS * zoom);
			const scaledHeight = Math.round((img.height / img.width) * PIXELS * zoom);

			const posX = Math.round((PIXELS - scaledWidth) / 2 + offsetX * RES_PX_MM);
			const posY = Math.round((PIXELS - scaledHeight) / 2 + offsetY * RES_PX_MM);

			ctx.globalAlpha = 0.8;
			ctx.drawImage(img, posX, posY, scaledWidth, scaledHeight);
			ctx.globalAlpha = 1.0;
		};
		img.src = previewUrl;
	}

	// Manejo de subida de archivo
	function handleFileUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) {
			uploadedFile = file;
			const reader = new FileReader();
			reader.onload = (e) => {
				previewUrl = e.target?.result as string;
				// Actualizar canvas cuando se carga la imagen
				setTimeout(() => actualizarPreviewCombinada(), 100);
			};
			reader.readAsDataURL(file);
		}
	}

	// Generar modelo 3D
	async function generateModel() {
		if (!uploadedFile) {
			errorMessage = 'Por favor sube una imagen primero';
			return;
		}

		isLoading = true;
		errorMessage = null;

		try {
			const blob = await apiGenerateModel({
				file: uploadedFile,
				shape: selectedShape,
				zoom,
				frame_width: frameWidth,
				offset_x: offsetX,
				offset_y: offsetY
			});

			modelUrl = URL.createObjectURL(blob);
			errorMessage = null; // Limpiar errores anteriores
		} catch (error) {
			console.error('Error:', error);
			errorMessage = error instanceof Error ? error.message : 'Error desconocido';
			modelUrl = null; // Limpiar modelo anterior si hay error
		} finally {
			isLoading = false;
		}
	}

	// Limpiar mensaje de error
	function clearError() {
		errorMessage = null;
	}

	function downloadModel() {
		if (modelUrl) {
			const a = document.createElement('a');
			a.href = modelUrl;
			a.download = `litho_${selectedShape.toLowerCase()}_manifold.stl`;
			a.click();
		}
	}

	onMount(() => {
		if (imagePreviewCanvas) {
			imagePreviewCanvas.width = 200;
			imagePreviewCanvas.height = 200;
		}
	});
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
	<div class="mx-auto max-w-5xl">
		<!-- Header -->
		<div class="mb-8 text-center">
			<h1 class="mb-2 text-5xl font-bold text-white">
				💎 LithoMaker Pro: Geometría Manifold
			</h1>
			<p class="text-lg text-slate-300">Convierte tus fotos en modelos 3D listos para imprimir</p>
		</div>

		<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
			<!-- Panel de Control (Sidebar) -->
			<div class="space-y-6 lg:col-span-1">
				<!-- Sección 1: Producto -->
				<Card class="bg-slate-800 border-slate-700">
					<CardHeader>
						<CardTitle class="text-white">1. Producto</CardTitle>
					</CardHeader>
					<CardContent class="space-y-4">
						<div>
							<Label for="shape" class="mb-2 block text-white">Forma</Label>
							<div class="space-y-2">
								{#each shapes as shape}
									<label class="flex items-center gap-2">
										<input
											type="radio"
											name="shape"
											on:change={actualizarPreviewCombinada}
											value={shape}
											bind:group={selectedShape}
											class="h-4 w-4 cursor-pointer"
										/>
										<span class="text-white">{shape}</span>
									</label>
								{/each}
							</div>
						</div>

						<div>
							<Label for="frameWidth" class="mb-2 block text-white">
								Ancho Marco: {frameWidth.toFixed(1)} mm
							</Label>
							<input
								id="frameWidth"
								type="range"
								min="2.0"
								max="5.0"
								step="0.1"
								on:change={actualizarPreviewCombinada}
								bind:value={frameWidth}
								class="w-full cursor-pointer"
							/>
						</div>
					</CardContent>
				</Card>

				<!-- Sección 2: Imagen -->
				<Card class="bg-slate-800 border-slate-700">
					<CardHeader>
						<CardTitle class="text-white">2. Imagen</CardTitle>
					</CardHeader>
					<CardContent class="space-y-4">
						<div>
							<Label for="zoom" class="mb-2 block text-white">Zoom: {zoom.toFixed(1)}x</Label>
							<input
								id="zoom"
								type="range"
								min="0.5"
								max="3.0"
								step="0.1"
								bind:value={zoom}
								on:change={actualizarPreviewCombinada}
								class="w-full cursor-pointer"
							/>
						</div>

						<div>
							<Label for="offsetX" class="mb-2 block text-white">Mover X: {offsetX}px</Label>
							<input
								id="offsetX"
								type="range"
								min="-60"
								max="60"
								step="1"
								bind:value={offsetX}
								on:change={actualizarPreviewCombinada}
								class="w-full cursor-pointer"
							/>
						</div>

						<div>
							<Label for="offsetY" class="mb-2 block text-white">Mover Y: {offsetY}px</Label>
							<input
								id="offsetY"
								type="range"
								min="-60"
								max="60"
								step="1"
								bind:value={offsetY}
								on:change={actualizarPreviewCombinada}
								class="w-full cursor-pointer"
							/>
						</div>
					</CardContent>
				</Card>
			</div>

			<!-- Área Principal -->
			<div class="space-y-6 lg:col-span-2">
				<!-- Upload Section -->
				<Card class="bg-slate-800 border-slate-700 flex flex-col">
					<CardHeader>
						<CardTitle class="text-white">Subir Fotografía</CardTitle>
						<CardDescription class="text-slate-400">JPG, PNG o JPEG</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="space-y-4">
							<input
								id="fileUpload"
								type="file"
								accept="image/*"
								on:change={handleFileUpload}
								class="file:bg-blue-600 file:text-white file:cursor-pointer"
							/>

							{#if previewUrl}
								<p class="mb-2 text-sm text-slate-300">Previsualización: Imagen + Máscara {selectedShape}</p>
								<div class="rounded-lg border-2 border-slate-500 bg-slate-900">
									<canvas
										bind:this={imagePreviewCanvas}
										class="w-full h-auto rounded-lg"
									/>
								</div>
								<p class="mt-2 text-xs text-slate-400">
									Gris oscuro = área de litho | Gris claro = marco | Tu imagen se mueve con los sliders
								</p>
							{/if}
						</div>
					</CardContent>
				</Card>

				<!-- Info Card -->
				{#if uploadedFile}
					<Card class="border-blue-900 bg-blue-950">
						<CardContent class="flex gap-3 pt-6">
							<AlertCircle class="h-5 w-5 text-blue-400" />
							<div class="text-sm text-blue-200">
								<p class="font-semibold">Resolución de Ingeniería: 5 px/mm | 0.2 mm/pixel</p>
								<p>Lienzo: 450x450 px | Vértices estimados: ~405,000</p>
							</div>
						</CardContent>
					</Card>
				{/if}

				<!-- Error Message -->
				{#if errorMessage}
				<Alert class="border-red-900 bg-red-950">
					<AlertCircle class="h-4 w-4 text-red-600" />
					<AlertTitle class="text-red-600">Error</AlertTitle>
					<AlertDescription class="text-red-200">{errorMessage}</AlertDescription>
				</Alert>
			{/if}
				<!-- Generate Button -->
				<Button
					onclick={generateModel}
					disabled={!uploadedFile || isLoading}
					class="w-full bg-gradient-to-r from-blue-600 to-blue-500 py-6 text-lg font-bold text-white hover:from-blue-700 hover:to-blue-600 disabled:opacity-50"
				>
					{#if isLoading}
						<span class="animate-spin mr-2">⚙️</span>
						Procesando geometría cerrada...
					{:else}
						<Zap class="mr-2 h-5 w-5" />
						🚀 Generar {selectedShape} Sólido (Manifold)
					{/if}
				</Button>

				<!-- Download Section -->
			{#if modelUrl}
				<Alert class="border-green-900 bg-green-950">
					<CheckCircle class="h-4 w-4 text-green-600" />
					<AlertTitle class="text-green-600">Éxito</AlertTitle>
					<AlertDescription class="text-green-200">
						Geometría generada correctamente. Bordes cerrados.
					</AlertDescription>
				</Alert>

				<Card class="bg-slate-800 border-slate-700 flex flex-col">
					<CardHeader>
						<CardTitle class="text-white">👀 Inspección 3D - Gira para ver tu modelo</CardTitle>
						<CardDescription class="text-slate-400">Visualización interactiva con rotación automática</CardDescription>
					</CardHeader>
					<CardContent class="flex-1 min-h-[500px]">
						{#await fetch(modelUrl).then(r => r.arrayBuffer())}
							<div class="flex items-center justify-center h-full">
								<p class="text-slate-400">Cargando modelo 3D...</p>
							</div>
						{:then stlBytes}
							<STLViewer {stlBytes} />
						{:catch error}
							<div class="flex items-center justify-center h-full">
								<p class="text-red-400">Error cargando modelo: {error.message}</p>
							</div>
						{/await}
					</CardContent>
				</Card>

				<Button
					onclick={downloadModel}
					class="w-full gap-2 bg-green-600 py-6 text-lg font-bold text-white hover:bg-green-700"
				>
					<Download class="h-5 w-5" />
					📥 DESCARGAR {selectedShape.toUpperCase()} FINAL
				</Button>
			{/if}
			</div>
		</div>
	</div>
</div>

<style>
	:global(body) {
		/* @apply bg-slate-800; */
	}
</style>
