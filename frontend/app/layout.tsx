import type { Metadata } from "next";
import Sidebar from "@/components/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "CogniWeave — AI-Powered Knowledge Compiler",
  description: "Transform podcasts, articles, books, and videos into structured, searchable wisdom that compounds over time in Google Workspace.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full flex text-gray-100 gradient-bg">
        <Sidebar />
        <main className="flex-1 flex flex-col h-screen overflow-y-auto relative">
          {children}
        </main>
      </body>
    </html>
  );
}
