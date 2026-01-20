export type Vec3 = {
    x?: number;
    y?: number;
    z?: number;
};

export type StlItem = {
    file: Blob;

    rotation?: Vec3; // grados
    offset?: Vec3;   // unidades Three.js
};
