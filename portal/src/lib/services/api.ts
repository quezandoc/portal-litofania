/**
 * Servicio de API para conectar con el backend
 * Backend frontend-driven (imagen final → STL)
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface GenerateModelRequest {
	file: File | Blob;
	filename?: string;
	texto?: string;
	texto_alto_mm?: number;
	texto_margin_mm?: number;
}

export async function generateModel(
	{ file, filename = 'litho.png'}: GenerateModelRequest
): Promise<Blob> {

	const formData = new FormData();
	formData.append('file', file, filename);

	const response = await fetch(`${API_BASE_URL}/api/generate-3d/`, {
		method: 'POST',
		body: formData
	});

	if (!response.ok) {
		let message = 'Error generating model';
		try {
			const error = await response.json();
			message = error.detail || message;
		} catch {
			// ignore JSON parse errors
		}
		throw new Error(message);
	}

	return await response.blob();
}


export async function healthCheck(): Promise<boolean> {
	try {
		const response = await fetch(`${API_BASE_URL}/health`);
		return response.ok;
	} catch {
		return false;
	}
}
