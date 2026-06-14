"use client";

import { useState } from "react";
import { uploadContract, UploadResponse } from "@/lib/api";

export function Upload({ onUploaded }: { onUploaded: (r: UploadResponse) => void }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setBusy(true);
    setErr(null);
    try {
      const res = await uploadContract(file);
      onUploaded(res);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-3 items-start">
      <label className="inline-flex items-center gap-2 cursor-pointer bg-ink text-parchment px-6 py-3 rounded-full hover:bg-ink/85 transition text-sm font-medium">
        <span className="w-1.5 h-1.5 rounded-full bg-parchment" />
        {busy ? "Indexing your contract…" : "Upload contract"}
        <input
          type="file"
          accept=".pdf,.docx,.doc"
          disabled={busy}
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </label>
      <a
        href="https://github.com/Pallak-08/legalmind"
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center px-6 py-3 rounded-full border border-ink/30 hover:border-ink hover:bg-ink/5 transition text-sm font-medium"
      >
        View source
      </a>
      {err && <p className="text-sm text-accent w-full sm:w-auto sm:ml-2 sm:self-center">{err}</p>}
    </div>
  );
}
