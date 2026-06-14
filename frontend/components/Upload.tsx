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
    <div className="border-2 border-dashed border-ink/20 rounded-lg p-12 text-center bg-white/40">
      <h2 className="font-serif text-2xl mb-2">Upload a contract</h2>
      <p className="text-ink/60 mb-6 text-sm">PDF or DOCX, up to 20 MB. Nothing leaves your machine.</p>
      <label className="inline-block cursor-pointer bg-accent text-parchment px-5 py-2 rounded hover:bg-accent/90 transition">
        {busy ? "Indexing…" : "Choose file"}
        <input
          type="file"
          accept=".pdf,.docx,.doc"
          disabled={busy}
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </label>
      {err && <p className="mt-4 text-sm text-red-700">{err}</p>}
    </div>
  );
}
