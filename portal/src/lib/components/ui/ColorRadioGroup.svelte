<script lang="ts">
    export type ColorOption = {
        label: string;
        value: string;
        swatch: string;
    };

    let {
        title,
        id,
        options,
        orientation = "vertical",
        value = $bindable(),
    } = $props<{
        title: string;
        id: string;
        orientation?: "vertical" | "horizontal";
        options: readonly ColorOption[];
        value: string;
    }>();
</script>

<div class="color-field">
    <span class="title">{title}</span>

    <div
        class="palette"
        class:vertical={orientation === "vertical"}
        class:horizontal={orientation === "horizontal"}
    >
        {#each options as opt}
            <label class="swatch" title={opt.label}>
                <input
                    type="radio"
                    name={id}
                    value={opt.value}
                    bind:group={value}
                />

                <span
                    class="color"
                    style="--swatch:{opt.swatch}"
                ></span>

                <span class="label">{opt.label}</span>
            </label>
        {/each}
    </div>
</div>


<style>
    .color-field {
        margin-block: 1.25rem;
    }

    .title {
        display: block;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    /* =======================
   PALETTE LAYOUT
   ======================= */

    .palette {
        display: grid;
        gap: 0.75rem;
    }

    /* Vertical = lista limpia */

    .palette.vertical {
        grid-template-columns: 1fr;
    }

    /* Horizontal = grid PRO */

    .palette.horizontal {
        grid-template-columns: repeat(auto-fill, minmax(2.5rem, 1fr));
    }

    /* =======================
   SWATCH
   ======================= */

    .swatch {
        position: relative;
        display: grid;
        justify-items: center;
        gap: 0.35rem;
        cursor: pointer;
    }

    /* ocultar input */
    .swatch input {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }

    /* color box */
    .color {
        width: 2.25rem;
        height: 2.25rem;
        border-radius: 0.6rem;
        background: var(--swatch);
        border: 2px solid var(--color-primary-200);
        transition:
            transform 0.15s ease,
            border-color 0.15s ease,
            box-shadow 0.15s ease;
    }

    /* hover */
    .swatch:hover .color {
        transform: translateY(-1px);
        border-color: var(--color-primary-400);
    }

    /* selected */
    .swatch input:checked + .color {
        border-color: var(--color-primary-600);
        box-shadow:
            0 0 0 2px var(--color-primary-200),
            0 6px 14px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }

    /* =======================
   LABEL
   ======================= */

    .label {
        font-size: 0.65rem;
        color: var(--text-secondary);
        text-align: center;
        line-height: 1;
    }

    /* horizontal = label secundario */
    .palette.horizontal .label {
        opacity: 0.6;
    }

    /* =======================
   FOCUS (accesibilidad PRO)
   ======================= */

    .swatch input:focus-visible + .color {
        outline: 2px solid var(--color-primary-400);
        outline-offset: 2px;
    }
</style>
