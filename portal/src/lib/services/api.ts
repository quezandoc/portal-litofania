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
	{ file, filename = 'litho.png', texto = '', texto_alto_mm = 12, texto_margin_mm = 4 }: GenerateModelRequest
): Promise<Blob> {

	const formData = new FormData();
	formData.append('file', file, filename);
	// agrego los campos del texto (coinciden con los nombres Form(...) del backend)
	formData.append('texto', texto);
	formData.append('texto_alto_mm', String(texto_alto_mm));
	formData.append('texto_margin_mm', String(texto_margin_mm));

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
