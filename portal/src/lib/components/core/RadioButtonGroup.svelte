<script lang="ts">
    type Option<T = string> = {
        readonly label: string;
        readonly value: T;
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
        options: readonly Option<string>[];
        orientation?: "vertical" | "horizontal";
        value: string;
    }>();
</script>

<div class="radio-field">
    <span class="radio-title">{title}</span>

    <div
        class="radio-group"
        class:vertical={orientation === "vertical"}
        class:horizontal={orientation === "horizontal"}
    >
        {#each options as option}
            <label class="radio-option">
                <input
                    type="radio"
                    name={id}
                    value={option.value}
                    bind:group={value}
                />

                <span class="radio-custom"></span>

                <span class="radio-label">
                    {option.label}
                </span>
            </label>
        {/each}
    </div>
</div>

<style>
    .radio-field {
        margin-block: 1.5rem;
    }

    .radio-title {
        display: block;
        margin-bottom: 0.75rem;
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    .radio-group {
        display: grid;
        gap: 0.75rem;
    }

    /* ORIENTATIONS */

    .radio-group.vertical {
        grid-auto-flow: row;
    }

    .radio-group.horizontal {
        display: flex;
        flex-wrap: wrap; /* 🔥 permite romper */
        gap: 1rem;
    }

    .radio-option {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: pointer;
        font-size: 0.95rem;
        color: var(--text-secondary);
    }

    /* Ocultar input real */
    .radio-option input {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }

    /* Custom radio */
    .radio-custom {
        width: 1.25rem;
        height: 1.25rem;
        border-radius: 50%;
        border: 2px solid var(--color-primary-300);
        background-color: var(--bg-primary);
        display: grid;
        place-items: center;
        transition: all 0.15s ease;
    }

    .radio-custom::after {
        content: "";
        width: 0.6rem;
        height: 0.6rem;
        border-radius: 50%;
        background-color: var(--color-primary-500);
        transform: scale(0);
        transition: transform 0.15s ease;
    }

    input:checked + .radio-custom {
        border-color: var(--color-primary-500);
    }

    input:checked + .radio-custom::after {
        transform: scale(1);
    }

    .radio-label {
        user-select: none;
    }
</style>
