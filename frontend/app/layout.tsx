import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LegalMind: Ask any contract",
  description: "Upload a contract. Ask plain-english questions. Get answers with exact clause citations.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
