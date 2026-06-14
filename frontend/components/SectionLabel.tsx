export function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="inline-block border-b border-rust pb-1 mb-6">
      <span className="text-xs font-semibold tracking-widest2 text-rust uppercase">
        {children}
      </span>
    </div>
  );
}
