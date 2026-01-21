<script lang="ts">
    import RangeSlider from "$lib/components/ui/RangeSlider.svelte";
    import RadioButtonGroup from "$lib/components/ui/RadioButtonGroup.svelte";
    import ImageUploader from "$lib/components/core/ImageUploader.svelte";
    import ImageCanvas from "$lib/components/core/ImageCanvas.svelte";
    import KeyTextInput from "$lib/components/core/KeyTextInput.svelte";

    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher<{
        generar: {
            imagen?: Blob;
            texto?: string;
        };
    }>();

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

    async function generar() {
        // ============================
        // Validaciones obligatorias
        // ============================
        if (!imageSrc) {
            alert("Debes cargar una imagen antes de continuar.");
            return;
        }

        if (!canvasRef) {
            alert("El lienzo no está listo todavía.");
            return;
        }

        if (!text || text.trim() === "") {
            alert("Debes ingresar un texto para generar la base.");
            return;
        }

        // ============================
        // 1. Exportar máscara final
        // ============================
        let blob: Blob = await canvasRef.exportMasked();

        if (!blob || blob.size === 0) {
            alert("No se pudo generar la máscara final.");
            return;
        }

        dispatch("generar", {
            imagen: blob,
            texto: text.trim().toUpperCase(),
        });
    }
</script>

<section class="hero bg-surface-1">
    <!-- <h2 class="title-section">Card Title</h2> -->
    <div class="card grid grid-2 bg-gradient-glass p-4">
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
                        onclick={() => generar()}
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
