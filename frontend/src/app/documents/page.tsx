"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listDocuments, deleteDocument, type Document } from "@/lib/api";
import { Card } from "@/components/Card";
import { Button } from "@/components/Button";
import toast from "react-hot-toast";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    try {
      setLoading(true);
      const res = await listDocuments();
      setDocuments(res.documents);
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "Failed to load documents";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(docId: string, filename: string) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      setDeletingId(docId);
      await deleteDocument(docId);
      toast.success("Document deleted successfully");
      setDocuments((docs) => docs.filter((d) => d.doc_id !== docId));
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "Failed to delete document";
      toast.error(errorMessage);
    } finally {
      setDeletingId(null);
    }
  }

  function formatDate(dateString: string) {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "Unknown date";
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Documents</h1>
        <p className="text-gray-600">Manage your uploaded documents</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : documents.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📄</span>
            </div>
            <p className="text-lg font-medium text-gray-900 mb-2">No documents yet</p>
            <p className="text-gray-500 mb-6">Upload your first document to get started</p>
            <Button onClick={() => router.push("/")}>Upload Document</Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <Card key={doc.doc_id} className="hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-xl">📄</span>
                </div>
                <button
                  onClick={() => handleDelete(doc.doc_id, doc.filename)}
                  disabled={deletingId === doc.doc_id}
                  className="text-red-500 hover:text-red-700 disabled:opacity-50"
                  title="Delete document"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>

              <h3 className="font-semibold text-gray-900 mb-2 truncate" title={doc.filename}>
                {doc.filename}
              </h3>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center gap-2">
                  <span>📅</span>
                  <span>{formatDate(doc.upload_date)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>📑</span>
                  <span>{doc.pages} pages</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>🔢</span>
                  <span>{doc.chunks} chunks</span>
                </div>
              </div>

              <Button
                onClick={() => router.push(`/doc/${doc.doc_id}?name=${encodeURIComponent(doc.filename)}`)}
                className="w-full"
                variant="primary"
              >
                Open Document
              </Button>
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}

