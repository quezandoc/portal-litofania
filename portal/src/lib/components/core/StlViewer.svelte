<script lang="ts">
    import * as THREE from "three";
    import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";

    /* ───────── Props ───────── */

    let {
        stl,
        size = 400,
        background = "#f6f6f6",
    } = $props<{
        stl: Blob | null;
        size?: number;
        background?: string;
    }>();

    /* ───────── DOM ───────── */

    let canvas: HTMLCanvasElement;

    /* ───────── Three core ───────── */

    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;
    let mesh: THREE.Mesh | null = null;

    let baseCameraZ = 120;

    /* ───────── Estado interacción ───────── */

    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    let rotationX = $state(0);
    let rotationY = $state(0);

    /* ───────── Init ───────── */

    $effect(() => {
        if (!canvas) return;

        scene = new THREE.Scene();
        scene.background = new THREE.Color(background);

        camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
        camera.position.set(0, 0, baseCameraZ);

        renderer = new THREE.WebGLRenderer({
            canvas,
            antialias: true,
            alpha: false,
        });
        renderer.setSize(size, size);
        renderer.setPixelRatio(window.devicePixelRatio);

        scene.add(new THREE.AmbientLight(0xffffff, 0.6));

        const light = new THREE.DirectionalLight(0xffffff, 0.9);
        light.position.set(10, 20, 10);
        scene.add(light);

        animate();
    });

    /* ───────── STL load ───────── */

    $effect(() => {
        if (!stl || !scene) return;

        const reader = new FileReader();
        reader.onload = () => {
            const loader = new STLLoader();
            const geometry = loader.parse(reader.result as ArrayBuffer);

            geometry.center();
            geometry.computeVertexNormals();

            const material = new THREE.MeshStandardMaterial({
                color: 0x8a8a8a,
                roughness: 0.6,
                metalness: 0.1,
            });

            if (mesh) scene.remove(mesh);

            mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);

            // 📐 ajuste cámara
            const box = new THREE.Box3().setFromObject(mesh);
            const len = box.getSize(new THREE.Vector3()).length();
            baseCameraZ = len * 1.3;

            resetView();
        };

        reader.readAsArrayBuffer(stl);
    });

    /* ───────── Render loop ───────── */

    function animate() {
        requestAnimationFrame(animate);

        if (mesh) {
            mesh.rotation.x = rotationX;
            mesh.rotation.y = rotationY;
        }

        camera.position.z = baseCameraZ;
        renderer.render(scene, camera);
    }

    /* ───────── Helpers ───────── */

    function clamp(v: number, min: number, max: number) {
        if (!Number.isFinite(v)) return min;
        return Math.min(max, Math.max(min, v));
    }

    function resetView() {
        rotationX = 0;
        rotationY = 0;

        camera.position.set(0, 0, baseCameraZ);
        camera.lookAt(0, 0, 0);
    }

    /* ───────── Eventos ───────── */

    function onMouseDown(e: MouseEvent) {
        dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
    }

    function onMouseMove(e: MouseEvent) {
        if (!dragging) return;

        rotationY += (e.clientX - lastX) * 0.01;
        rotationX += (e.clientY - lastY) * 0.01;

        lastX = e.clientX;
        lastY = e.clientY;
    }

    function onMouseUp() {
        dragging = false;
    }

    $effect(() => {
        if (!canvas) return;

        const preventWheel = (e: WheelEvent) => e.preventDefault();
        canvas.addEventListener("wheel", preventWheel, { passive: false });

        return () => {
            canvas.removeEventListener("wheel", preventWheel);
        };
    });
</script>

<div class="viewer">
    <canvas
        bind:this={canvas}
        width={size}
        height={size}
        onmousedown={onMouseDown}
        onmousemove={onMouseMove}
        onmouseup={onMouseUp}
        onmouseleave={onMouseUp}
    ></canvas>

    <button class="reset" onclick={resetView}> Reset </button>
</div>

<style>
    .viewer {
        position: relative;
        width: fit-content;
    }

    canvas {
        border-radius: 0.75rem;
        background: var(--color-primary-100);
        cursor: grab;
    }

    canvas:active {
        cursor: grabbing;
    }

    .reset {
        position: absolute;
        bottom: 0.75rem;
        right: 0.75rem;
        padding: 0.4rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        background: var(--color-primary-500);
        color: white;
        opacity: 0.85;
    }

    .reset:hover {
        opacity: 1;
    }
</style>
