<script lang="ts">
    let {
        src,
        shape,
        frameWidth,
        zoom,
        offsetX = $bindable(),
        offsetY = $bindable(),
        brightness = 1,
        contrast = 1,
        rotation = 0,
        size = 400,
    } = $props<{
        src: string;
        shape: "Círculo" | "Cuadrado" | "Corazón";
        frameWidth: number;
        zoom: number;
        offsetX: number;
        offsetY: number;
        brightness?: number;
        contrast?: number;
        rotation?: number;
        size?: number;
    }>();

    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;

    let image = new Image();
    let imageReady = $state(false);

    // Estado drag
    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    /* ───────── Canvas context ───────── */

    $effect(() => {
        if (!canvas) return;
        ctx = canvas.getContext("2d");
    });

    function getCssVar(name: string, fallback = "#2b2b2b") {
        return (
            getComputedStyle(document.documentElement)
                .getPropertyValue(name)
                .trim() || fallback
        );
    }

    function drawCircleMask(
        ctx: CanvasRenderingContext2D,
        r: number,
        inset = 0,
    ) {
        ctx.arc(0, 0, r - inset, 0, Math.PI * 2);
    }

    function drawSquareMask(
        ctx: CanvasRenderingContext2D,
        r: number,
        inset = 0,
    ) {
        const s = (r - inset) * 2;
        ctx.rect(-s / 2, -s / 2, s, s);
    }

    function drawHeartMask(
        ctx: CanvasRenderingContext2D,
        r: number,
        inset = 0,
    ) {
        const s = r - inset;

        // Proporciones basadas en la imagen (estilo V)
        const topY = -s * 1.05; // Altura máxima de las ondas
        const bottomY = s * 1; // Punta inferior bien estirada
        const joinY = -s * 0.6; // Hendidura central (donde se cruzan las ondas)
        const sideX = s * 1.25; // Anchura lateral

        ctx.moveTo(0, bottomY);

        // Onda Izquierda
        ctx.bezierCurveTo(
            -sideX * 1.3,
            -s * 0.2, // Control 1: ensancha el lateral bajo
            -sideX * 0.7,
            topY * 1.4, // Control 2: eleva y redondea la onda
            0,
            joinY, // Punto final: hendidura
        );

        // Onda Derecha
        ctx.bezierCurveTo(
            sideX * 0.7,
            topY * 1.4, // Control 1: eleva y redondea la onda
            sideX * 1.3,
            -s * 0.2, // Control 2: ensancha el lateral bajo
            0,
            bottomY, // Punto final: punta
        );

        ctx.closePath();
    }

    function drawFrame(
        ctx: CanvasRenderingContext2D,
        shape: "Círculo" | "Cuadrado" | "Corazón",
        size: number,
        frameWidth: number,
        color = "#2b2b2b",
    ) {
        const r = size / 2;

        // 🧱 Padding de seguridad (NO se quita)
        const padding = frameWidth + 4;
        const drawable = size - padding * 2;

        // Escala independiente para liberar aspecto
        const scaleX = drawable / size;
        const scaleY = drawable / size;
        ctx.save();

        // Centro del canvas + padding + corrección corazón
        ctx.translate(r, r);

        // Ajuste al área permitida
        ctx.scale(scaleX, scaleY);

        ctx.beginPath();

        // ── Forma exterior ──
        switch (shape) {
            case "Círculo":
                drawCircleMask(ctx, r);
                break;
            case "Cuadrado":
                drawSquareMask(ctx, r);
                break;
            case "Corazón":
                drawHeartMask(ctx, r);
                break;
        }

        // ── Forma interior (resta) ──
        switch (shape) {
            case "Círculo":
                drawCircleMask(ctx, r, frameWidth);
                break;
            case "Cuadrado":
                drawSquareMask(ctx, r, frameWidth);
                break;
            case "Corazón":
                drawHeartMask(ctx, r, frameWidth * 1.3);
                break;
        }

        ctx.fillStyle = color;
        ctx.fill("evenodd");

        ctx.restore();
    }

    /* ───────── Imagen ───────── */

    $effect(() => {
        if (!src) return;

        imageReady = false;
        image = new Image();

        image.onload = () => {
            imageReady = true;
        };

        image.src = src;
    });

    /* ───────── Render ───────── */

    $effect(() => {
        if (!ctx || !imageReady) return;

        ctx.clearRect(0, 0, size, size);

        const baseScale = Math.max(size / image.width, size / image.height);
        const scale = baseScale * zoom;

        const w = image.width * scale;
        const h = image.height * scale;

        const x = (size - w) / 2 + offsetX;
        const y = (size - h) / 2 + offsetY;

        const cx = x + w / 2;
        const cy = y + h / 2;

        ctx.save();

        // 🎨 filtros SOLO para la imagen
        ctx.filter = `
    grayscale(100%)
    brightness(${brightness})
    contrast(${contrast})
  `;

        // 🔄 transformaciones
        ctx.translate(cx, cy);
        ctx.rotate((rotation * Math.PI) / 180);

        // 🎯 dibujar desde el centro
        ctx.drawImage(image, -w / 2, -h / 2, w, h);

        ctx.restore();

        // 🧱 frame encima (SIN ROTAR)
        drawFrame(
            ctx,
            shape,
            size,
            frameWidth,
            getCssVar("--color-primary-900"),
        );
    });

    /* ───────── Drag helpers ───────── */

    function clamp(value: number, min: number, max: number) {
        return Math.min(max, Math.max(min, value));
    }

    function startDrag(x: number, y: number) {
        dragging = true;
        lastX = x;
        lastY = y;
    }

    function moveDrag(x: number, y: number) {
        if (!dragging) return;

        offsetX = clamp(offsetX + (x - lastX), -120, 120);
        offsetY = clamp(offsetY + (y - lastY), -120, 120);

        lastX = x;
        lastY = y;
    }

    function endDrag() {
        dragging = false;
    }

    function getPos(e: MouseEvent | TouchEvent) {
        const rect = canvas.getBoundingClientRect();

        if (e instanceof TouchEvent) {
            const t = e.touches[0] ?? e.changedTouches[0];
            return {
                x: t.clientX - rect.left,
                y: t.clientY - rect.top,
            };
        }

        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        };
    }

    /* ───────── Eventos ───────── */

    function onPointerDown(e: PointerEvent) {
        canvas.setPointerCapture(e.pointerId);

        const rect = canvas.getBoundingClientRect();
        startDrag(e.clientX - rect.left, e.clientY - rect.top);
    }

    function onPointerMove(e: PointerEvent) {
        if (!dragging) return;

        const rect = canvas.getBoundingClientRect();
        moveDrag(e.clientX - rect.left, e.clientY - rect.top);
    }

    function onPointerUp(e: PointerEvent) {
        dragging = false;
        canvas.releasePointerCapture(e.pointerId);
    }

    $effect(() => {
        offsetX = clamp(offsetX, -120, 120);
        offsetY = clamp(offsetY, -120, 120);
    });

    /* ───────── Mask Work ───────── */

    function drawInnerMaskPath(
        ctx: CanvasRenderingContext2D,
        shape: "Círculo" | "Cuadrado" | "Corazón",
        size: number,
        frameWidth: number,
    ) {
        const r = size / 2;

        const padding = frameWidth + 4;
        const drawable = size - padding * 2;
        const scale = drawable / size;

        ctx.translate(r, r);
        ctx.scale(scale, scale);

        ctx.beginPath();

        switch (shape) {
            case "Círculo":
                drawCircleMask(ctx, r, frameWidth);
                break;
            case "Cuadrado":
                drawSquareMask(ctx, r, frameWidth);
                break;
            case "Corazón":
                drawHeartMask(ctx, r, frameWidth * 1.3);
                break;
        }
    }

    export function exportMasked(): Promise<Blob> {
        return new Promise((resolve) => {
            const out = document.createElement("canvas");
            out.width = size;
            out.height = size;

            const octx = out.getContext("2d")!;
            octx.clearRect(0, 0, size, size);

            // ───────── CLIP ─────────
            octx.save();

            // sistema limpio SOLO para el clip
            octx.setTransform(1, 0, 0, 1, 0, 0);
            drawInnerMaskPath(octx, shape, size, frameWidth);
            octx.clip();

            // ───────── RESET TOTAL ─────────
            octx.setTransform(1, 0, 0, 1, 0, 0);

            // ───────── DIBUJO IMAGEN ─────────
            const baseScale = Math.max(size / image.width, size / image.height);
            const scale = baseScale * zoom;

            const w = image.width * scale;
            const h = image.height * scale;

            const x = (size - w) / 2 + offsetX;
            const y = (size - h) / 2 + offsetY;

            const cx = x + w / 2;
            const cy = y + h / 2;

            octx.filter = `
            grayscale(100%)
            brightness(${brightness})
            contrast(${contrast})
        `;

            octx.translate(cx, cy);
            octx.rotate((rotation * Math.PI) / 180);
            octx.drawImage(image, -w / 2, -h / 2, w, h);

            octx.restore(); // ← libera el clip

            drawFrame(octx, shape, size, frameWidth, "#FF0000");

            out.toBlob((blob) => {
                if (blob) resolve(blob);
            }, "image/png");
        });
    }
</script>

<canvas
    bind:this={canvas}
    width={size}
    height={size}
    class="image-canvas"
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
>
</canvas>

<style>
    .image-canvas {
        width: 100%;
        aspect-ratio: 1 / 1;
        background-color: var(--color-primary-200);
        border-radius: 0.75rem;
        touch-action: none;
        cursor: grab;
    }

    .image-canvas:active {
        cursor: grabbing;
    }
</style>
