"use client";

import { useState } from "react";
import { askQuestion, Citation, UploadResponse } from "@/lib/api";
import { CitationCard } from "./CitationCard";

type Turn = {
  question: string;
  answer?: string;
  citations?: Citation[];
  error?: string;
};

const SUGGESTED: Record<string, string[]> = {
  NDA: [
    "How long does this agreement last?",
    "What if I have to disclose information due to a court order?",
    "Are there exceptions to the confidentiality obligation?",
    "Where will disputes be resolved?",
  ],
  Employment: [
    "What is the notice period?",
    "Is there a non-compete clause?",
    "How is salary defined?",
  ],
};

export function Chat({ contract }: { contract: UploadResponse }) {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);

  const ask = async (q: string) => {
    if (!q.trim()) return;
    setBusy(true);
    const turn: Turn = { question: q };
    setTurns((t) => [...t, turn]);
    setQuestion("");
    try {
      const res = await askQuestion(contract.contract_id, q);
      setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, answer: res.answer, citations: res.citations } : x)));
    } catch (e: any) {
      setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, error: e.message } : x)));
    } finally {
      setBusy(false);
    }
  };

  const suggested = SUGGESTED[contract.detected_doc_type] || [
    "What is the duration of this agreement?",
    "What are the key obligations of each party?",
    "How can either party terminate this agreement?",
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white/60 rounded-lg p-4 border border-ink/10">
        <div className="text-xs uppercase tracking-wider text-ink/40">Indexed</div>
        <div className="font-serif text-lg">{contract.filename}</div>
        <div className="text-sm text-ink/60 mt-1">
          {contract.detected_doc_type} · {contract.num_clauses} clauses
          {contract.num_pages ? ` · ${contract.num_pages} pages` : ""}
        </div>
      </div>

      {turns.length === 0 && (
        <div>
          <p className="text-sm text-ink/60 mb-3">Try one of these:</p>
          <div className="flex flex-wrap gap-2">
            {suggested.map((q) => (
              <button
                key={q}
                onClick={() => ask(q)}
                disabled={busy}
                className="text-sm border border-ink/15 px-3 py-1.5 rounded hover:border-accent hover:text-accent transition"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-8">
        {turns.map((t, i) => (
          <div key={i} className="space-y-3">
            <div className="font-serif text-lg italic text-ink/70">— {t.question}</div>
            {t.error && <p className="text-red-700 text-sm">{t.error}</p>}
            {t.answer && (
              <div className="bg-white rounded-lg p-4 border border-ink/10 font-serif leading-relaxed whitespace-pre-wrap">
                {t.answer}
              </div>
            )}
            {t.citations && t.citations.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs uppercase tracking-wider text-ink/40">Cited clauses</div>
                {t.citations.map((c) => (
                  <CitationCard key={c.section + c.excerpt.slice(0, 20)} c={c} />
                ))}
              </div>
            )}
            {!t.answer && !t.error && (
              <div className="text-sm text-ink/40 italic">Reading the contract…</div>
            )}
          </div>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(question);
        }}
        className="sticky bottom-4 flex gap-2 bg-parchment pt-2"
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about this contract…"
          disabled={busy}
          className="flex-1 border border-ink/20 rounded px-4 py-3 bg-white focus:border-accent outline-none"
        />
        <button
          type="submit"
          disabled={busy || !question.trim()}
          className="bg-accent text-parchment px-5 rounded hover:bg-accent/90 disabled:opacity-40 transition"
        >
          Ask
        </button>
      </form>
    </div>
  );
}
