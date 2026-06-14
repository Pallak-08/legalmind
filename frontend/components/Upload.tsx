"use client";

import { useRef, useState } from "react";
import { uploadContract, UploadResponse } from "@/lib/api";

export function Upload({ onUploaded }: { onUploaded: (r: UploadResponse) => void }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
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
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const f = e.dataTransfer.files?.[0];
        if (f) handleFile(f);
      }}
      onClick={() => inputRef.current?.click()}
      className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition px-8 py-12 bg-cream/40 ${
        dragging
          ? "border-accent bg-cream/70"
          : "border-oak/50 hover:border-oak"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.doc"
        disabled={busy}
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />

      <div className="flex flex-col items-center text-center">
        <div className="w-14 h-14 rounded-full bg-ink/5 flex items-center justify-center mb-5">
          <svg viewBox="0 0 24 24" className="w-6 h-6 text-ink" fill="none" stroke="currentColor" strokeWidth="1.6">
            <path d="M12 16V4M12 4l-4 4M12 4l4 4" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <h3 className="font-serif text-2xl md:text-3xl font-medium text-ink">
          {busy ? "Indexing your contract…" : "Drop your contract here"}
        </h3>
        <p className="mt-2 text-sm text-ink/60">
          PDF or DOCX, up to 20 MB. Nothing leaves your browser tab.
        </p>

        <button
          type="button"
          disabled={busy}
          className="mt-6 inline-flex items-center gap-2 bg-ink text-parchment px-6 py-3 rounded-full hover:bg-ink/85 transition text-sm font-medium disabled:opacity-50"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-parchment" />
          {busy ? "Working…" : "Choose a file"}
        </button>

        {err && <p className="mt-4 text-sm text-accent">{err}</p>}
      </div>
    </div>
  );
}
