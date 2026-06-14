"use client";

import { useState } from "react";
import type { Citation } from "@/lib/api";

export function CitationCard({ c }: { c: Citation }) {
  const [open, setOpen] = useState(false);
  return (
    <button
      onClick={() => setOpen(!open)}
      className="block w-full text-left border border-ink/10 rounded p-3 bg-white hover:border-accent/40 transition"
    >
      <div className="flex items-baseline justify-between gap-3">
        <div>
          <span className="font-mono text-xs font-bold text-accent">{c.section}</span>
          {c.title && <span className="ml-2 text-sm text-ink/80">{c.title}</span>}
        </div>
        <span className="text-xs text-ink/40">
          {c.page ? `p. ${c.page}` : ""}
          {c.page ? " · " : ""}
          {(c.score * 100).toFixed(0)}%
        </span>
      </div>
      {open && (
        <p className="mt-2 text-sm text-ink/70 whitespace-pre-wrap font-serif leading-relaxed">
          {c.excerpt}
        </p>
      )}
      {!open && <p className="mt-1 text-xs text-ink/40">Click to expand source text</p>}
    </button>
  );
}
