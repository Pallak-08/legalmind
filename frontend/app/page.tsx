"use client";

import { useEffect, useState } from "react";
import { Upload } from "@/components/Upload";
import { Chat } from "@/components/Chat";
import { Scale } from "@/components/Scale";
import { uploadContract, UploadResponse } from "@/lib/api";

export default function Page() {
  const [contract, setContract] = useState<UploadResponse | null>(null);
  const [pageDragging, setPageDragging] = useState(false);
  const [pageBusy, setPageBusy] = useState(false);
  const [pageErr, setPageErr] = useState<string | null>(null);

  // page-wide drag-and-drop
  useEffect(() => {
    const onDragOver = (e: DragEvent) => {
      if (e.dataTransfer?.types.includes("Files")) {
        e.preventDefault();
        setPageDragging(true);
      }
    };
    const onDragLeave = (e: DragEvent) => {
      if ((e.target as HTMLElement)?.tagName === "HTML") setPageDragging(false);
    };
    const onDrop = async (e: DragEvent) => {
      e.preventDefault();
      setPageDragging(false);
      const file = e.dataTransfer?.files?.[0];
      if (!file) return;
      setPageBusy(true);
      setPageErr(null);
      try {
        setContract(await uploadContract(file));
      } catch (err: any) {
        setPageErr(err.message);
      } finally {
        setPageBusy(false);
      }
    };
    window.addEventListener("dragover", onDragOver);
    window.addEventListener("dragleave", onDragLeave);
    window.addEventListener("drop", onDrop);
    return () => {
      window.removeEventListener("dragover", onDragOver);
      window.removeEventListener("dragleave", onDragLeave);
      window.removeEventListener("drop", onDrop);
    };
  }, []);

  if (contract) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-10">
        <header className="mb-8 flex items-center gap-3">
          <Scale className="w-7" />
          <span className="font-serif text-xl font-medium">LegalMind</span>
          <button
            onClick={() => setContract(null)}
            className="ml-auto text-sm text-ink/50 hover:text-accent"
          >
            ← Upload a different contract
          </button>
        </header>
        <Chat contract={contract} />
        <footer className="mt-16 text-xs text-ink/40 text-center">
          Not legal advice. Verify all citations against the source document.
        </footer>
      </main>
    );
  }

  return (
    <main className="relative min-h-screen flex flex-col overflow-hidden">
      {/* page-wide drop overlay */}
      {pageDragging && (
        <div className="fixed inset-0 z-50 bg-ink/40 flex items-center justify-center pointer-events-none">
          <div className="bg-parchment border-2 border-dashed border-accent rounded-2xl px-10 py-8 text-center">
            <p className="font-serif text-2xl text-ink">Drop your contract</p>
            <p className="text-sm text-ink/60 mt-1">PDF or DOCX</p>
          </div>
        </div>
      )}

      <header className="max-w-7xl w-full mx-auto px-6 pt-6 flex items-center gap-3 relative z-10">
        <Scale className="w-7" />
        <span className="font-serif text-xl font-medium tracking-tight">LegalMind</span>
      </header>

      <div className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 grid md:grid-cols-12 gap-6 items-center relative">
        {/* left: text + CTAs */}
        <div className="md:col-span-5 lg:col-span-5 z-10">
          <h1 className="font-serif text-5xl md:text-6xl lg:text-7xl font-medium leading-[1.04] tracking-tight">
            We weigh<br />
            your contract,<br />
            <span className="italic">clause by clause.</span>
          </h1>
          <p className="mt-6 text-base text-ink/70 max-w-md leading-relaxed">
            Upload a contract. Ask anything in plain English. Every answer cites
            the exact clause, or refuses to answer when the contract is silent.
          </p>
          <div className="mt-8">
            <Upload onUploaded={setContract} />
            {pageBusy && (
              <p className="mt-3 text-sm text-ink/60">Indexing your contract…</p>
            )}
            {pageErr && <p className="mt-3 text-sm text-accent">{pageErr}</p>}
          </div>
        </div>

        {/* right: the scale */}
        <div className="md:col-span-7 lg:col-span-7 flex justify-center md:justify-end">
          <Scale className="w-full max-w-xl md:max-w-2xl" />
        </div>
      </div>

      <footer className="border-t border-ink/10 px-6 py-5 text-xs text-ink/45 flex flex-wrap gap-x-6 gap-y-2 justify-between max-w-7xl w-full mx-auto">
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
