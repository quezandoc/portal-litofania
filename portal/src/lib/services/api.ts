/**
 * Servicio de API para conectar con el backend
 * Backend frontend-driven
 */

const API_BASE_URL =
	import.meta.env.VITE_API_URL || 'http://localhost:8000';

/* ======================================================
 * Tipos
 * ====================================================== */

export interface GenerateModelRequest {
	file: File | Blob;
	filename?: string;
}

export interface GenerateTextBaseRequest {
	texto: string;
}

/* ======================================================
 * Imagen → STL (litofanía)
 * ====================================================== */

export async function generateModel(
	{ file, filename = 'litho.png' }: GenerateModelRequest
): Promise<Blob> {

	const formData = new FormData();
	formData.append('file', file, filename);

	const response = await fetch(
		`${API_BASE_URL}/api/generate-3d/`,
		{
			method: 'POST',
			body: formData,
		}
	);

	if (!response.ok) {
		let message = 'Error generating model';
		try {
			const error = await response.json();
			message = error.detail || message;
		} catch {}
		throw new Error(message);
	}

	return await response.blob();
}

/* ======================================================
 * Texto → Base STL
 * ====================================================== */

export async function generateTextBase(
	{ texto }: GenerateTextBaseRequest
): Promise<Blob> {

	const formData = new FormData();
	formData.append('texto', texto);

	const response = await fetch(
		`${API_BASE_URL}/api/generate-text-base/`,
		{
			method: 'POST',
			body: formData,
		}
	);

	if (!response.ok) {
		let message = 'Error generating text base';
		try {
			const error = await response.json();
			message = error.detail || message;
		} catch {}
		throw new Error(message);
	}

	return await response.blob();
}

/* ======================================================
 * Health check
 * ====================================================== */

export async function healthCheck(): Promise<boolean> {
	try {
		const response = await fetch(`${API_BASE_URL}/health`);
		return response.ok;
	} catch {
		return false;
	}
}
