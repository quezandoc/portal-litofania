<script lang="ts">
    let {
        label,
        placeholder = "",
        maxLength = 12,
        value = $bindable(),
    } = $props<{
        label: string;
        placeholder?: string;
        maxLength?: number;
        value: string;
    }>();

    function onInput(e: Event) {
        const v = (e.target as HTMLInputElement).value;
        value = v.slice(0, maxLength).toUpperCase();
    }
</script>

<div class="text-field">
    <label class="text-label" for="keyTextInput">
        {label}
        <span class="counter">
            {value.length}/{maxLength}
        </span>
    </label>

    <input
        id="keyTextInput"
        type="text"
        class="text-input"
        {placeholder}
        maxlength={maxLength}
        bind:value
        oninput={onInput}
        autocomplete="off"
        spellcheck="false"
    />
</div>

<style>
    .text-field {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    /* Label */
    .text-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    .counter {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    /* INPUT */
    .text-input {
        height: 3rem;
        padding-inline: 1rem;

        /* Texto */
        text-align: center;
        font-weight: 700; /* bold */
        text-transform: uppercase; /* uppercase */
        letter-spacing: 0.35em; /* 🔥 separación */
        font-size: 1.1rem;

        /* Estilo */
        border-radius: 0.75rem;
        border: 2px solid var(--color-primary-400);
        background-color: var(--bg-primary);
        color: var(--color-primary-900);

        outline: none;
        transition:
            border-color 0.15s ease,
            box-shadow 0.15s ease;
    }

    /* Placeholder centrado y suave */
    .text-input::placeholder {
        color: var(--text-secondary);
        letter-spacing: 0.25em;
    }

    /* Focus */
    .text-input:focus {
        border-color: var(--color-primary-600);
        box-shadow: 0 0 0 4px
            color-mix(in oklab, var(--color-primary-500) 30%, transparent);
    }
</style>
