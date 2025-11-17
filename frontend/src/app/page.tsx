"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { uploadPdf } from "@/lib/api";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import toast from "react-hot-toast";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    try {
      const res = await uploadPdf(file);
      toast.success("Document uploaded successfully!");
      router.push(`/doc/${res.doc_id}?name=${encodeURIComponent(res.filename)}`);
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "Upload failed. Please try again.";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
      } else {
        alert("Please upload a PDF file");
      }
    }
  };

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          DocAssist AI
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          Upload your PDF document and get instant AI-powered insights
        </p>
        <p className="text-gray-500">
          Get smart summaries and chat with Dr.Doc about your documents
        </p>
      </div>

      <Card className="max-w-2xl mx-auto">
        <div
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
            dragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          role="region"
          aria-label="File upload area"
        >
          {file ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500 mt-1">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={() => setFile(null)}
                  variant="outline"
                  disabled={loading}
                >
                  Change File
                </Button>
                <Button onClick={handleUpload} isLoading={loading}>
                  {loading ? "Processing..." : "Upload & Process"}
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </div>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Drag and drop your PDF here
                </p>
                <p className="text-sm text-gray-500 mt-2">or</p>
              </div>
      <input
                ref={fileInputRef}
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                aria-label="Select PDF file to upload"
      />
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
              >
                Browse Files
              </Button>
            </div>
          )}
        </div>
      </Card>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          Supported format: PDF • Max file size: 50MB
        </p>
      </div>
    </main>
  );
}
