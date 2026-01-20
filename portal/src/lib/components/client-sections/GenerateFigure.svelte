<script lang="ts">
    import RangeSlider from "$lib/components/core/RangeSlider.svelte";
    import RadioButtonGroup from "$lib/components/core/RadioButtonGroup.svelte";
    import ImageUploader from "$lib/components/core/ImageUploader.svelte";
    import ImageCanvas from "$lib/components/core/ImageCanvas.svelte";
    import KeyTextInput from "$lib/components/core/KeyTextInput.svelte";
    import StlViewer from "$lib/components/core/StlViewer.svelte";

    import { generateModel, generateTextBase } from "$lib/services/api";

    let frameWidth = $state(24.0);
    let zoom = $state(1.0);
    let offsetX = $state(0.0);
    let offsetY = $state(0.0);
    let brightness = $state(1.0); // 1 = normal
    let contrast = $state(1.0); // 1 = normal
    let rotation = $state(0); // en grados

    let selectedShape = $state<"Corazón" | "Círculo" | "Cuadrado">("Corazón");

    let imageSrc = $state<string | undefined>();
    let stlPreview = $state<Blob | null>(null);

    let text = $state("");

    const options = [
        { label: "Corazón", value: "Corazón" },
        { label: "Círculo", value: "Círculo" },
        { label: "Cuadrado", value: "Cuadrado" },
    ] as const;

    // svelte-ignore non_reactive_update
    let canvasRef: any;

    async function generarFigura() {
        // ============================
        // Validaciones obligatorias
        // ============================
        if (!imageSrc) {
            alert("Debes cargar una imagen antes de continuar.");
            return;
        }

        if (!text || text.trim() === "") {
            alert("Debes ingresar un texto para generar la litofanía.");
            return;
        }

        if (!canvasRef) {
            alert("El lienzo no está listo todavía.");
            return;
        }

        try {
            // ============================
            // 1. Exportar máscara final
            // ============================
            const blob: Blob = await canvasRef.exportMasked();

            if (!blob || blob.size === 0) {
                alert("No se pudo generar la máscara final.");
                return;
            }
            // ============================
            // 3. Enviar al backend
            // ============================
            const stlBlob = await generateModel({
                file: blob,
                filename: "litho.png",
            });

            stlPreview = stlBlob;

            // ============================
            // 4. Descargar STL
            // ============================
            const url = URL.createObjectURL(stlBlob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "litho.stl";
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
            alert(
                err instanceof Error
                    ? err.message
                    : "Error al generar el modelo 3D",
            );
        }
    }

    async function generarTextoBase() {
        // ============================
        // Validaciones obligatorias
        // ============================
        if (!text || text.trim() === "") {
            alert("Debes ingresar un texto para generar la base.");
            return;
        }

        try {
            // ============================
            // 1. Enviar texto al backend
            // ============================
            const stlBlob = await generateTextBase({
                texto: text.trim().toUpperCase(),
            });

            // (opcional) preview
            stlPreview = stlBlob;

            // ============================
            // 2. Descargar STL
            // ============================
            const url = URL.createObjectURL(stlBlob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "base_texto.stl";
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
            alert(
                err instanceof Error
                    ? err.message
                    : "Error al generar la base de texto",
            );
        }
    }
</script>

<section class="hero bg-surface-1">
    <!-- <h2 class="title-section">Card Title</h2> -->
    <div class="card grid grid-2 bg-gradient-glass border-2 p-4">
        <div>
            <ImageUploader bind:src={imageSrc} />
            <KeyTextInput
                label="Texto"
                placeholder="Escribe algo…"
                bind:value={text}
            />

            {#if imageSrc}
                <div>
                    <RadioButtonGroup
                        title="Selecciona la forma:"
                        id="shapeOptions"
                        orientation="horizontal"
                        {options}
                        bind:value={selectedShape}
                    />

                    <RangeSlider
                        title="Ancho del marco:"
                        id="frameWidth"
                        min={24}
                        max={60}
                        step={0.1}
                        bind:value={frameWidth}
                    />
                    <RangeSlider
                        title="Zoom:"
                        id="zoom"
                        min={0.5}
                        max={3.0}
                        step={0.01}
                        bind:value={zoom}
                    />
                    <RangeSlider
                        title="Brillo"
                        id="brightness"
                        min={0.2}
                        max={2}
                        step={0.01}
                        bind:value={brightness}
                    />

                    <RangeSlider
                        title="Contraste"
                        id="contrast"
                        min={0.2}
                        max={2}
                        step={0.01}
                        bind:value={contrast}
                    />

                    <RangeSlider
                        title="Rotación"
                        id="rotation"
                        min={-180}
                        max={180}
                        step={1}
                        bind:value={rotation}
                    />
                    <button
                        onclick={() => generarTextoBase()}
                        class="btn btn-primary block"
                    >
                        Comienza tu proyecto
                    </button>
                </div>
            {/if}
        </div>

        {#if imageSrc}
            <ImageCanvas
                bind:this={canvasRef}
                src={imageSrc}
                shape={selectedShape}
                {frameWidth}
                {zoom}
                {brightness}
                {contrast}
                {rotation}
                bind:offsetX
                bind:offsetY
                size={900}
            />
        {/if}
    </div>
</section>
{#if stlPreview}
    <section class="hero bg-surface-1">
        <StlViewer stl={stlPreview} size={1200} />
    </section>
{/if}
