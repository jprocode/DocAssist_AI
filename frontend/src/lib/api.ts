// lib/api.ts

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// ---------- Types ----------
export interface UploadResponse {
  doc_id: string;
  filename: string;
}

export interface SummarizeResponse {
  doc_id: string;
  summary: string;
  expanded?: boolean;
}

export interface AskResponse {
  doc_id: string;
  answer: string;
  sources: {
    document: boolean;
    web: boolean;
    web_results?: Array<{
      title: string;
      url: string;
      content: string;
      score: number;
    }>;
  };
  contexts: { 
    rank: number; 
    score: number; 
    text: string;
    page_numbers?: number[];
  }[];
}

// ---------- API Calls ----------

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export async function summarize(docId: string, expanded: boolean = false): Promise<SummarizeResponse> {
  const res = await fetch(`${BASE_URL}/summarize?doc_id=${docId}&expanded=${expanded}`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`Summarize failed: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export async function ask(
  docId: string, 
  question: string, 
  useWebSearch: boolean = false
): Promise<AskResponse> {
  const res = await fetch(`${BASE_URL}/${docId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      question,
      use_web_search: useWebSearch 
    }),
  });

  if (!res.ok) {
    throw new Error(`Ask failed: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export async function askStream(
  docId: string,
  question: string,
  useWebSearch: boolean = false,
  onChunk: (chunk: string) => void,
  onSources: (sources: { document: boolean; web: boolean }, contexts?: Array<{ page_numbers?: number[] }>) => void
): Promise<void> {
  const res = await fetch(`${BASE_URL}/${docId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      use_web_search: useWebSearch,
      stream: true
    }),
  });

  if (!res.ok) {
    throw new Error(`Ask failed: ${res.status} ${res.statusText}`);
  }

  const reader = res.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error("No response body");
  }

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "start" && data.sources) {
            onSources(data.sources, data.contexts);
          } else if (data.type === "chunk" && data.content) {
            onChunk(data.content);
          } else if (data.type === "done") {
            return;
          }
        } catch (e) {
          console.error("Error parsing SSE data:", e);
        }
      }
    }
  }
}

export interface Document {
  doc_id: string;
  filename: string;
  upload_date: string;
  pages: number;
  chunks: number;
  dim: number;
}

export interface DocumentsResponse {
  documents: Document[];
}

export async function listDocuments(): Promise<DocumentsResponse> {
  const res = await fetch(`${BASE_URL}/documents`);
  if (!res.ok) {
    throw new Error(`Failed to list documents: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getDocument(docId: string): Promise<Document> {
  const res = await fetch(`${BASE_URL}/documents/${docId}`);
  if (!res.ok) {
    throw new Error(`Failed to get document: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/documents/${docId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error(`Failed to delete document: ${res.status} ${res.statusText}`);
  }
}
