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
      <header className="max-w-6xl w-full mx-auto px-6 pt-6 flex items-center gap-3">
        <Scale className="w-7" />
        <span className="font-serif text-xl font-medium tracking-tight">LegalMind</span>
      </header>

      <div className="flex-1 max-w-6xl w-full mx-auto px-6 py-10 grid md:grid-cols-12 gap-10 items-center">
        {/* left: pitch */}
        <div className="md:col-span-6 lg:col-span-7">
          <h1 className="font-serif text-5xl md:text-6xl lg:text-7xl font-medium leading-[1.05] tracking-tight">
            Ask any contract,<br />
            <span className="italic">in plain English.</span>
          </h1>
          <p className="mt-6 text-base text-ink/70 max-w-md leading-relaxed">
            Upload a PDF or DOCX. Every answer cites the exact clause it came
            from, or refuses to answer if the contract does not address your
            question.
          </p>
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
