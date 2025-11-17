"use client";

import React, { useState } from "react";
import toast from "react-hot-toast";

interface ChatMessageProps {
  question: string;
  answer: string;
  sources?: {
    document: boolean;
    web: boolean;
    web_results?: Array<{ title: string; url: string; content: string }>;
  };
  pageNumbers?: number[];
}

export function ChatMessage({ question, answer, sources, pageNumbers }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(answer);
      setCopied(true);
      toast.success("Answer copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  return (
    <div className="mb-6 pb-6 border-b border-gray-200 last:border-b-0">
      <div className="mb-3">
        <div className="flex items-start gap-2">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            <span className="text-blue-600 text-sm font-semibold">You</span>
          </div>
          <div className="flex-1">
            <p className="text-gray-900 whitespace-pre-wrap">{question}</p>
          </div>
        </div>
      </div>
      
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
          <span className="text-purple-600 text-sm font-semibold">Dr</span>
        </div>
        <div className="flex-1">
          <div className="mb-2 group">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <span className="font-semibold text-gray-900">Dr.Doc: </span>
                <span className="text-gray-700 whitespace-pre-wrap">
                  {answer || <span className="text-gray-400 italic">Thinking...</span>}
                </span>
              </div>
              {answer && (
                <button
                  onClick={handleCopy}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-100 rounded focus:opacity-100"
                  title="Copy answer"
                  aria-label={copied ? "Answer copied" : "Copy answer to clipboard"}
                >
                  {copied ? (
                    <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  )}
                </button>
              )}
            </div>
          </div>
          {sources && (
            <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
              {sources.document && (
                <span className="flex items-center gap-1">
                  <span>📄</span>
                  <span>Document</span>
                  {pageNumbers && pageNumbers.length > 0 && (
                    <span className="ml-1 text-blue-600 font-medium">
                      (Pages {pageNumbers.join(", ")})
                    </span>
                  )}
                </span>
              )}
              {sources.web && (
                <span className="flex items-center gap-1">
                  <span>🌐</span>
                  <span>Web Search</span>
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

