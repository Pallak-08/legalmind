"use client";

import { useState } from "react";
import { Upload } from "@/components/Upload";
import { Chat } from "@/components/Chat";
import { Scale } from "@/components/Scale";
import type { UploadResponse } from "@/lib/api";

export default function Page() {
  const [contract, setContract] = useState<UploadResponse | null>(null);

  if (contract) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-10">
        <header className="mb-8">
          <button
            onClick={() => setContract(null)}
            className="text-sm text-ink/50 hover:text-accent"
          >
            ← Upload a different contract
          </button>
          <h1 className="font-serif text-3xl mt-3">LegalMind</h1>
        </header>
        <Chat contract={contract} />
        <footer className="mt-16 text-xs text-ink/40 text-center">
          Not legal advice. Verify all citations against the source document.
        </footer>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col">
      <div className="flex-1 max-w-6xl w-full mx-auto px-6 py-10 grid md:grid-cols-12 gap-10 items-center">
        {/* left: pitch */}
        <div className="md:col-span-6 lg:col-span-7">
          <Scale className="w-20 md:w-24 mb-6 -ml-2" />
          <h1 className="font-serif text-5xl md:text-6xl lg:text-7xl font-medium leading-[1.05] tracking-tight">
            Ask any contract,<br />
            <span className="italic">in plain English.</span>
          </h1>
          <p className="mt-5 text-base text-ink/70 max-w-md leading-relaxed">
            Upload a PDF or DOCX. Every answer cites the exact clause it came
            from, or refuses to answer if the contract does not address your
            question.
          </p>
          <ul className="mt-6 space-y-2 text-sm text-ink/75">
            <li className="flex items-baseline gap-3">
              <span className="text-rust">◆</span>
              Clause-aware parser knows real section numbers
            </li>
            <li className="flex items-baseline gap-3">
              <span className="text-rust">◆</span>
              Hybrid retrieval (dense + BM25) with cross-encoder rerank
            </li>
            <li className="flex items-baseline gap-3">
              <span className="text-rust">◆</span>
              Citations match the source, or the model refuses
            </li>
          </ul>
        </div>

        {/* right: big upload box */}
        <div className="md:col-span-6 lg:col-span-5">
          <Upload onUploaded={setContract} />
        </div>
      </div>

      <footer className="border-t border-ink/10 px-6 py-5 text-xs text-ink/45 flex flex-wrap gap-x-6 gap-y-2 justify-between max-w-6xl w-full mx-auto">
        <div>Not legal advice. Verify all citations against the source document.</div>
        <div className="flex gap-6">
          <a href="https://github.com/Pallak-08/legalmind" target="_blank" rel="noreferrer" className="hover:text-accent">
            GitHub
          </a>
          <a href="https://legalmind-production-b9a9.up.railway.app/docs" target="_blank" rel="noreferrer" className="hover:text-accent">
            API docs
          </a>
        </div>
      </footer>
    </main>
  );
}
