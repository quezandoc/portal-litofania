<script lang="ts">
    import * as THREE from "three";
    import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";

    type Vec3 = {
        x?: number;
        y?: number;
        z?: number;
    };

    export type StlItem = {
        file: Blob;

        rotation?: Vec3; // grados
        offset?: Vec3; // unidades Three.js

        color?: string | number;
    };

    /* ───────── Props ───────── */

    let { stls = [], size = 400 } = $props<{
        stls: StlItem[];
        size?: number;
    }>();

    /* ───────── DOM ───────── */

    let canvas: HTMLCanvasElement;

    /* ───────── Three core ───────── */

    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;
    let group: THREE.Group | null = null;

    let baseCameraZ = 120;

    /* ───────── Estado interacción ───────── */

    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    let rotationX = $state(0);
    let rotationY = $state(0);

    /* ───────── Init ───────── */

    let initialized = false;

    function getCssVar(name: string, fallback = "#2b2b2b") {
        return (
            getComputedStyle(document.documentElement)
                .getPropertyValue(name)
                .trim() || fallback
        );
    }

    $effect(() => {
        if (!canvas || initialized) return;
        initialized = true;

        scene = new THREE.Scene();
        scene.background = new THREE.Color(getCssVar("--color-primary-300"));

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

        group = new THREE.Group();
        scene.add(group);

        animate();
    });

    /* ───────── STL load ───────── */

    $effect(() => {
        if (!scene || !group) return;

        // limpiar grupo
        group.clear();

        if (!stls.length) return;

        const loader = new STLLoader();
        const box = new THREE.Box3();

        let loaded = 0;

        for (const item of stls) {
            const reader = new FileReader();

            reader.onload = () => {
                const geometry = loader.parse(reader.result as ArrayBuffer);
                geometry.computeVertexNormals();

                const material = new THREE.MeshStandardMaterial({
                    color: item.color
                        ? new THREE.Color(item.color)
                        : new THREE.Color(0x8a8a8a),
                    roughness: 0.6,
                    metalness: 0.1,
                });

                const mesh = new THREE.Mesh(geometry, material);

                /* ───── ROTACIÓN (grados → radianes) ───── */

                if (item.rotation) {
                    mesh.rotation.set(
                        item.rotation.x
                            ? THREE.MathUtils.degToRad(item.rotation.x)
                            : 0,
                        item.rotation.y
                            ? THREE.MathUtils.degToRad(item.rotation.y)
                            : 0,
                        item.rotation.z
                            ? THREE.MathUtils.degToRad(item.rotation.z)
                            : 0,
                    );
                }

                /* ───── OFFSET ───── */

                if (item.offset) {
                    mesh.position.set(
                        item.offset.x ?? 0,
                        item.offset.y ?? 0,
                        item.offset.z ?? 0,
                    );
                }

                group!.add(mesh);
                box.expandByObject(mesh);

                loaded++;

                if (loaded === stls.length) {
                    const center = box.getCenter(new THREE.Vector3());
                    group!.position.sub(center);

                    const len = box.getSize(new THREE.Vector3()).length();
                    baseCameraZ = len * 1.3;

                    resetView();
                }
            };

            reader.readAsArrayBuffer(item.file);
        }
    });

    /* ───────── Render loop ───────── */

    function animate() {
        requestAnimationFrame(animate);

        if (group) {
            group.rotation.x = rotationX;
            group.rotation.y = rotationY;
        }

        camera.position.z = baseCameraZ;
        renderer.render(scene, camera);
    }

    /* ───────── Helpers ───────── */

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
        background-color: var(--color-primary-200);
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
