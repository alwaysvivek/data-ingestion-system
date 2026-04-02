const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;

export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Upload failed.");
  }

  return response.json();
}

export async function getDatasets() {
  const response = await fetch(`${API_BASE_URL}/datasets`);
  if (!response.ok) {
    throw new Error("Failed to fetch datasets.");
  }
  return response.json();
}

export async function getDatasetById(id) {
  const response = await fetch(`${API_BASE_URL}/datasets/${id}`);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to fetch dataset details.");
  }
  return response.json();
}

export async function deleteDataset(id) {
  const response = await fetch(`${API_BASE_URL}/datasets/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to delete dataset.");
  }
  return response.json();
}

export function openDatasetsSocket(onMessage) {
  const socket = new WebSocket(`${WS_BASE_URL}/ws`);
  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      onMessage(payload);
    } catch {
      // Ignore malformed websocket messages.
    }
  };
  return socket;
}
