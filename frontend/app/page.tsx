"use client";

import { useState } from "react";
import { Upload } from "@/components/Upload";
import { Chat } from "@/components/Chat";
import type { UploadResponse } from "@/lib/api";

export default function Page() {
  const [contract, setContract] = useState<UploadResponse | null>(null);

  return (
    <main className="max-w-3xl mx-auto px-6 py-10">
      <header className="mb-10">
        <h1 className="font-serif text-4xl">LegalMind</h1>
        <p className="text-ink/60 mt-1">
          Upload a contract. Ask plain-english questions. Every answer cites exact clause numbers.
        </p>
      </header>

      {!contract ? (
        <Upload onUploaded={setContract} />
      ) : (
        <>
          <button
            onClick={() => setContract(null)}
            className="text-sm text-ink/50 hover:text-accent mb-6"
          >
            ← Upload a different contract
          </button>
          <Chat contract={contract} />
        </>
      )}

      <footer className="mt-16 text-xs text-ink/40 text-center">
        Not legal advice. Verify all citations against the source document.
      </footer>
    </main>
  );
}
