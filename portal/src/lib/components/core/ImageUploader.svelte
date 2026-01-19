<script lang="ts">
    let {
        accept = "image/*",
        maxSizeMb = 5,
        src = $bindable(),
        file = $bindable(),
    } = $props<{
        accept?: string;
        maxSizeMb?: number;
        src?: string;
        file?: File | null;
    }>();

    let input: HTMLInputElement;

    function handleFiles(files: FileList | null) {
        if (!files || files.length === 0) return;

        const f = files[0];

        if (!f.type.startsWith("image/")) return;
        if (f.size > maxSizeMb * 1024 * 1024) {
            alert(`La imagen supera ${maxSizeMb}MB`);
            return;
        }

        file = f;
        src = URL.createObjectURL(f);
    }

    function onChange(e: Event) {
        handleFiles((e.target as HTMLInputElement).files);
    }

    function onDrop(e: DragEvent) {
        e.preventDefault();
        handleFiles(e.dataTransfer?.files ?? null);
    }
</script>

<button
    type="button"
    class="uploader"
    onclick={() => input.click()}
    ondragover={(e) => e.preventDefault()}
    ondrop={onDrop}
>
    <span class="placeholder"> 📷 Arrastra una imagen o presiona Enter </span>

    <input bind:this={input} type="file" {accept} hidden onchange={onChange} />
</button>

<style>
    .uploader {
        width: 100%;
        padding: 1rem 2rem;
        border-radius: 0.75rem;
        border: 2px dashed var(--color-primary-300);
        background-color: var(--bg-secondary);
        place-items: center;
        cursor: pointer;
        overflow: hidden;
        position: relative;
    }

    .uploader:hover {
        background-color: var(--bg-tertiary);
    }

    .placeholder {
        color: var(--text-secondary);
        font-size: 0.9rem;
        text-align: center;
        padding: 1rem;
    }
</style>
