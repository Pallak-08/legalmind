"use client";

import { useRef, useState } from "react";
import { uploadContract, UploadResponse } from "@/lib/api";

export function Upload({ onUploaded }: { onUploaded: (r: UploadResponse) => void }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3 items-center">
        <button
          onClick={() => inputRef.current?.click()}
          disabled={busy}
          className="inline-flex items-center gap-2 bg-ink text-parchment px-6 py-3 rounded-full hover:bg-ink/85 transition text-sm font-medium disabled:opacity-50"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-parchment" />
          {busy ? "Indexing your contract…" : "Upload contract"}
        </button>
        <a
          href="https://github.com/Pallak-08/legalmind"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center px-6 py-3 rounded-full border border-ink/30 hover:border-ink hover:bg-ink/5 transition text-sm font-medium"
        >
          View source
        </a>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          disabled={busy}
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </div>
      <p className="text-xs text-ink/50">
        PDF or DOCX, up to 20 MB. You can also drag a file anywhere on this page.
      </p>
      {err && <p className="text-sm text-accent">{err}</p>}
    </div>
  );
}

export function useUploader(onUploaded: (r: UploadResponse) => void) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const upload = async (file: File) => {
    setBusy(true);
    setErr(null);
    try {
      onUploaded(await uploadContract(file));
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };
  return { upload, busy, err };
}
