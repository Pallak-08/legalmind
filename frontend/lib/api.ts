const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type UploadResponse = {
  contract_id: string;
  filename: string;
  num_clauses: number;
  num_pages: number | null;
  detected_doc_type: string;
};

export type Citation = {
  section: string;
  title: string | null;
  page: number | null;
  excerpt: string;
  score: number;
};

export type QueryResponse = {
  answer: string;
  citations: Citation[];
  contract_id: string;
};

export async function uploadContract(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
  if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
  return res.json();
}

export async function askQuestion(contract_id: string, question: string): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contract_id, question }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Query failed");
  return res.json();
}
