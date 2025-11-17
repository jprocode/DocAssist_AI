"use client";

import { use } from "react";
import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { summarize, ask } from "@/lib/api";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { ChatMessage } from "@/components/ChatMessage";
import toast from "react-hot-toast";

export default function DocPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const searchParams = useSearchParams();
  const name = searchParams.get("name") || undefined;
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [summary, setSummary] = useState<string>("");
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandingSummary, setExpandingSummary] = useState(false);
  const [q, setQ] = useState("");
  const [chat, setChat] = useState<{ 
    q: string; 
    a: string; 
    sources?: { document: boolean; web: boolean; web_results?: Array<{ title: string; url: string; content: string }> };
    pageNumbers?: number[];
  }[]>([]);
  const [busy, setBusy] = useState(false);
  const [useWebSearch, setUseWebSearch] = useState(false);

  useEffect(() => {
    if (!id) return;
    setSummaryLoading(true);
    setIsExpanded(false);
    summarize(id, false)
      .then((res) => {
        setSummary(res.summary);
        setIsExpanded(res.expanded || false);
      })
      .catch((e: unknown) => {
        const errorMessage = e instanceof Error ? e.message : "Failed to generate summary";
        toast.error(errorMessage);
      })
      .finally(() => setSummaryLoading(false));
  }, [id]);

  async function handleExpandSummary() {
    if (!id || isExpanded || expandingSummary) return;
    setExpandingSummary(true);
    try {
      const res = await summarize(id, true);
      setSummary(res.summary);
      setIsExpanded(true);
      toast.success("Summary expanded successfully!");
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "Failed to expand summary";
      toast.error(errorMessage);
    } finally {
      setExpandingSummary(false);
    }
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  async function handleAsk() {
    if (!q.trim()) return;
    setBusy(true);
    const question = q;
    setQ("");
    
    // Add question to chat immediately
    const newChatEntry = { 
      q: question, 
      a: "",
      sources: undefined as { document: boolean; web: boolean } | undefined,
      pageNumbers: undefined as number[] | undefined
    };
    setChat((c) => [...c, newChatEntry]);
    const chatIndex = chat.length;
    
    try {
      const { askStream } = await import("@/lib/api");
      let fullAnswer = "";
      let sources: { document: boolean; web: boolean } | undefined = undefined;
      let pageNumbers: number[] | undefined = undefined;
      
      await askStream(
        id,
        question,
        useWebSearch,
        (chunk: string) => {
          fullAnswer += chunk;
          setChat((c) => {
            const updated = [...c];
            updated[chatIndex] = { ...updated[chatIndex], a: fullAnswer, sources, pageNumbers };
            return updated;
          });
        },
        (src: { document: boolean; web: boolean }, contexts?: Array<{ page_numbers?: number[] }>) => {
          sources = src;
          // Extract page numbers from contexts (use first context's page numbers)
          if (contexts && contexts.length > 0 && contexts[0].page_numbers) {
            pageNumbers = contexts[0].page_numbers;
          }
          setChat((c) => {
            const updated = [...c];
            updated[chatIndex] = { ...updated[chatIndex], sources, pageNumbers };
            return updated;
          });
        }
      );
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "Failed to get answer. Please try again.";
      toast.error(errorMessage);
      // Remove failed entry
      setChat((c) => c.filter((_, i) => i !== chatIndex));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {name || `Document ${id.slice(0, 8)}`}
        </h1>
        <p className="text-gray-600">Chat with Dr.Doc about your document</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card title="AI Summary" className="lg:sticky lg:top-8 lg:self-start">
          {summaryLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed mb-4">
                {summary || "No summary available"}
              </div>
              {!isExpanded && summary && (
                <div className="pt-4 border-t border-gray-200">
                  <Button
                    onClick={handleExpandSummary}
                    isLoading={expandingSummary}
                    disabled={expandingSummary}
                    variant="outline"
                    className="w-full"
                  >
                    {expandingSummary ? "Expanding..." : "Expand Summary"}
                  </Button>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    Get a more detailed, in-depth summary
                  </p>
                </div>
              )}
            </>
          )}
        </Card>

        <Card title="Chat with Dr.Doc" className="flex flex-col" padding="lg">
          <div
            className="flex-1 min-h-[400px] max-h-[600px] overflow-y-auto mb-6"
            role="log"
            aria-label="Chat conversation with Dr.Doc"
            aria-live="polite"
            aria-atomic="false"
          >
            {chat.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">💬</span>
                </div>
                  <p className="text-lg font-medium">Ask a question about this document</p>
                  <p className="text-sm mt-2">Dr.Doc is ready to help you understand your document</p>
                </div>
              </div>
            ) : (
              <div>
                {chat.map((row, i) => (
                  <ChatMessage
                    key={i}
                    question={row.q}
                    answer={row.a}
                    sources={row.sources}
                    pageNumbers={row.pageNumbers}
                  />
                ))}
                {busy && (
                  <div className="flex items-start gap-2 mb-6">
                    <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-purple-600 text-sm font-semibold">Dr</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 text-gray-500">
                        <div className="animate-pulse">●</div>
                        <div className="animate-pulse delay-75">●</div>
                        <div className="animate-pulse delay-150">●</div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
            )}
          </div>

          <div className="border-t border-gray-200 pt-4 space-y-4">
            <label className="flex items-center gap-3 cursor-pointer group">
            <input
                type="checkbox"
                checked={useWebSearch}
                onChange={(e) => setUseWebSearch(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                aria-label="Enable web search"
                aria-describedby="web-search-help"
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
                  Enable web search
                </span>
                <p id="web-search-help" className="text-xs text-gray-500 mt-0.5">
                  Allow Dr.Doc to search the internet for additional information
                </p>
              </div>
              {useWebSearch && (
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                  Active
                </span>
              )}
            </label>

            <div className="flex gap-3" role="form" aria-label="Question input form">
              <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !busy && q.trim()) {
                    e.preventDefault();
                    handleAsk();
                  }
                }}
                placeholder="Ask Dr.Doc a question..."
                disabled={busy}
                className="flex-1"
                aria-label="Question input"
                aria-describedby="question-help"
            />
              <Button 
                onClick={handleAsk} 
                isLoading={busy} 
                disabled={!q.trim()}
                aria-label={busy ? "Processing question" : "Submit question"}
              >
                Ask
              </Button>
            </div>
            <p id="question-help" className="sr-only">
              Type your question and press Enter or click Ask to submit
            </p>
          </div>
        </Card>
        </div>
    </main>
  );
}
