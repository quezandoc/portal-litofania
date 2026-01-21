<script lang="ts">
    import StlViewer, {
        type StlItem,
    } from "$lib/components/core/StlViewer.svelte";
    import ColorRadioGroup, {
        type ColorOption,
    } from "$lib/components/ui/ColorRadioGroup.svelte";

    const colorOptions: readonly ColorOption[] = [
        { label: "Azul", value: "#2563eb", swatch: "#2563eb" },
        { label: "Rojo", value: "#dc2626", swatch: "#dc2626" },
        { label: "Verde", value: "#16a34a", swatch: "#16a34a" },
        { label: "Gris", value: "#6b7280", swatch: "#6b7280" },
        { label: "Negro", value: "#111827", swatch: "#111827" },
    ] as const;

    const { stlFigura, stlBase } = $props<{
        stlFigura: Blob | null;
        stlBase: Blob | null;
    }>();

    let colorBase = $state<string>("#00F");

        

    let colorCanvas = $state<string>("#ffffff");

    // ✅ derivado puro, sin efectos
    const stls = $derived(
        [
            stlBase && {
                file: stlBase,
                rotation: { x: 0, y: -90, z: 0 },
                offset: { x: 45, y: -10, z: -10 },
                color: colorBase,
            },
            stlFigura && {
                file: stlFigura,
                rotation: { x: 0, y: 0, z: 0 },
                offset: { x: -45, y: 0, z: 0 },
                color: "#fff",
            },
        ].filter(Boolean) as StlItem[],
    );

    $effect(() => {
        console.log(stls.length);
    });
</script>

{#if stls.length}
    <section class="hero bg-surface-1">
        <!-- <h2 class="title-section">Card Title</h2> -->
        <div class="card d-flex centered bg-gradient-glass p-4">
            <div class="m-4">
                <ColorRadioGroup
                    title=""
                    id="preset-colors"
                    options={colorOptions}
                    orientation="vertical"
                    bind:value={colorBase}
                />
            </div>

            <StlViewer {stls} size={600}/>
        </div>
    </section>
{/if}
