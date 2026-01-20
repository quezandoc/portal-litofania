<script lang="ts">
    import StlViewer from "../core/StlViewer.svelte";
    import type { StlItem } from "$lib/types/stl";

    const { stlFigura, stlBase } = $props<{
        stlFigura: Blob | null;
        stlBase: Blob | null;
    }>();

    // ✅ derivado puro, sin efectos
    const stls = $derived(
        [
            stlBase && {
                file: stlBase,
                rotation: { x: 0, y: -90, z: 0 },
                offset: { x: 90, y: -10, z: -10 },
            },
            stlFigura && {
                file: stlFigura,
                rotation: { x: 0, y: 0, z: 0 },
                offset: { x: 0, y: 0, z: 0 },
            },
        ].filter(Boolean) as StlItem[],
    );
</script>

{#if stls.length}
    <StlViewer {stls} />
{/if}
