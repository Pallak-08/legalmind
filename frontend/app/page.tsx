"use client";

import { useState } from "react";
import { Upload } from "@/components/Upload";
import { Chat } from "@/components/Chat";
import { Scale } from "@/components/Scale";
import { SectionLabel } from "@/components/SectionLabel";
import type { UploadResponse } from "@/lib/api";

export default function Page() {
  const [contract, setContract] = useState<UploadResponse | null>(null);

  return (
    <main className="max-w-6xl mx-auto px-6 py-8">
      {/* hero */}
      <section className="grid md:grid-cols-12 gap-6 items-center min-h-[70vh]">
        <div className="md:col-span-7 lg:col-span-6">
          <h1 className="font-serif text-5xl md:text-6xl lg:text-7xl font-medium leading-[1.05] tracking-tight">
            We weigh your<br />contract,<br />clause by clause.
          </h1>
          <p className="mt-6 text-base text-ink/70 max-w-md leading-relaxed">
            Upload a contract. Ask anything in plain English. Every answer cites
            the exact clause it came from, or refuses to answer at all.
          </p>
          <div className="mt-8">
            {!contract ? (
              <Upload onUploaded={setContract} />
            ) : (
              <button
                onClick={() => setContract(null)}
                className="inline-flex items-center gap-2 text-sm text-ink/60 hover:text-accent"
              >
                ← Upload a different contract
              </button>
            )}
          </div>
        </div>
        <div className="md:col-span-5 lg:col-span-6 flex justify-center md:justify-end">
          <Scale className="w-full max-w-md" />
        </div>
      </section>

      {/* chat appears here once contract is uploaded */}
      {contract && (
        <section className="mt-4 mb-24">
          <Chat contract={contract} />
        </section>
      )}

      {/* "how it works" section only on the landing state */}
      {!contract && (
        <section className="mt-24 mb-24">
          <div className="grid md:grid-cols-12 gap-6 mb-12">
            <div className="md:col-span-4">
              <SectionLabel>About</SectionLabel>
              <h2 className="font-serif text-3xl md:text-4xl leading-tight font-medium">
                Built for people who actually read the fine print.
              </h2>
            </div>
            <div className="md:col-span-7 md:col-start-6 self-end">
              <p className="text-ink/70 leading-relaxed">
                Most "ask a PDF" tools chunk by character count, which destroys
                the document's structure. When the model cites Section 5, you
                cannot tell which clause it actually used or whether the citation
                exists. LegalMind parses contracts along their real clause
                boundaries, so every citation points to a section that is in
                the document.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* feature cards: how it works */}
      {!contract && (
        <section className="mb-24">
          <SectionLabel>How it works</SectionLabel>
          <div className="rounded-md border-2 border-oak/60 grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-oak/40">
            <Feature
              title="Clause-aware parsing"
              body="Detects Articles, Sections, decimal numbering, and lettered subclauses. Each chunk knows its real section number and page."
            />
            <Feature
              title="Hybrid retrieval"
              body="Dense embeddings find paraphrases. BM25 catches legal terms-of-art. A cross-encoder reranks the top candidates before answering."
            />
            <Feature
              title="Grounded answers"
              body="The model must cite the exact clause it used. If the contract does not address your question, it refuses instead of making something up."
            />
          </div>
        </section>
      )}

      {/* stack section */}
      {!contract && (
        <section className="mb-24">
          <SectionLabel>Under the hood</SectionLabel>
          <div className="grid md:grid-cols-12 gap-6">
            <div className="md:col-span-5">
              <h2 className="font-serif text-3xl md:text-4xl leading-tight font-medium">
                A small, opinionated stack.
              </h2>
            </div>
            <ul className="md:col-span-6 md:col-start-7 text-ink/70 leading-relaxed space-y-2">
              <li><span className="text-ink font-medium">FastAPI</span> backend with a clause-level parser for PDF and DOCX.</li>
              <li><span className="text-ink font-medium">BAAI/bge-large-en-v1.5</span> embeddings (1024-dim, runs locally).</li>
              <li><span className="text-ink font-medium">ChromaDB</span> vector store behind a Protocol, swappable for Pinecone.</li>
              <li><span className="text-ink font-medium">rank-bm25 + RRF + bge-reranker-base</span> for hybrid retrieval.</li>
              <li><span className="text-ink font-medium">Groq llama-3.3-70b</span> for grounded generation.</li>
              <li><span className="text-ink font-medium">Next.js 14 + Tailwind</span> frontend, deployed on Railway.</li>
            </ul>
          </div>
        </section>
      )}

      {/* footer */}
      <footer className="border-t border-ink/15 pt-8 pb-12 text-sm text-ink/50 flex flex-wrap gap-x-6 gap-y-2 justify-between">
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

function Feature({ title, body }: { title: string; body: string }) {
  return (
    <div className="p-8">
      <h3 className="font-serif text-2xl font-medium leading-tight">{title}</h3>
      <p className="mt-3 text-sm text-ink/65 leading-relaxed">{body}</p>
    </div>
  );
}
