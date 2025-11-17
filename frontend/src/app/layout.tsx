import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { Toaster } from "@/components/Toaster";

export const metadata: Metadata = {
  title: "DocAssist AI",
  description: "AI-powered document assistant with summaries and Q&A",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-gray-900 text-white flex flex-col p-6 gap-4">
            <div className="mb-6">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <span className="text-2xl">📄</span>
                DocAssist AI
            </h2>
            </div>

            <nav className="flex flex-col gap-3" role="navigation" aria-label="Main navigation">
              <Link 
                href="/" 
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Home page"
              >
                <span aria-hidden="true">🏠</span>
                <span>Home</span>
              </Link>
              <Link 
                href="/documents" 
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Documents page"
              >
                <span aria-hidden="true">📚</span>
                <span>Documents</span>
              </Link>
              <Link 
                href="/about" 
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="About page"
              >
                <span aria-hidden="true">ℹ️</span>
                <span>About</span>
              </Link>
              <Link 
                href="/api/auth/logout" 
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 mt-auto"
                aria-label="Logout"
              >
                <span aria-hidden="true">🚪</span>
                <span>Logout</span>
              </Link>
            </nav>

            <footer className="mt-auto text-xs text-gray-400">
              © {new Date().getFullYear()} DocAssist AI
            </footer>
          </aside>

          {/* Main content */}
          <div className="flex-1 bg-gray-50">{children}</div>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
