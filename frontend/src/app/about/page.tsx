import { Card } from "@/components/Card";

export default function AboutPage() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">About DocAssist AI</h1>
        <p className="text-gray-600">Your intelligent document assistant</p>
      </div>

      <div className="space-y-6">
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">What is DocAssist AI?</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            DocAssist AI is an intelligent document assistant that helps you understand and interact with your PDF documents. 
            Upload any PDF document, get instant AI-powered summaries, and chat with Dr.Doc to answer questions about your documents.
          </p>
          <p className="text-gray-700 leading-relaxed">
            Dr.Doc is designed to prevent hallucinations by strictly using only the content from your uploaded document. 
            When needed, you can enable web search to allow Dr.Doc to access additional information from the internet.
          </p>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Features</h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start gap-3">
              <span className="text-blue-600 mt-1">📄</span>
              <div>
                <strong className="text-gray-900">Smart Document Upload</strong>
                <p className="text-sm text-gray-600">Drag and drop or browse to upload PDF documents up to 50MB</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 mt-1">📝</span>
              <div>
                <strong className="text-gray-900">AI-Powered Summaries</strong>
                <p className="text-sm text-gray-600">Get instant, comprehensive summaries of your documents</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 mt-1">💬</span>
              <div>
                <strong className="text-gray-900">Chat with Dr.Doc</strong>
                <p className="text-sm text-gray-600">Ask questions and get answers based on your document content</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 mt-1">🌐</span>
              <div>
                <strong className="text-gray-900">Optional Web Search</strong>
                <p className="text-sm text-gray-600">Enable web search for questions that need additional context</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 mt-1">🔒</span>
              <div>
                <strong className="text-gray-900">Hallucination Prevention</strong>
                <p className="text-sm text-gray-600">Dr.Doc only uses your document content, preventing AI hallucinations</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 mt-1">📚</span>
              <div>
                <strong className="text-gray-900">Document Management</strong>
                <p className="text-sm text-gray-600">View, manage, and organize all your uploaded documents</p>
              </div>
            </li>
          </ul>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">How It Works</h2>
          <ol className="space-y-4 text-gray-700">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">1</span>
              <div>
                <strong className="text-gray-900">Upload Your PDF</strong>
                <p className="text-sm text-gray-600 mt-1">Upload a PDF document through our intuitive interface</p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">2</span>
              <div>
                <strong className="text-gray-900">Get Instant Summary</strong>
                <p className="text-sm text-gray-600 mt-1">Our AI analyzes your document and generates a comprehensive summary</p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">3</span>
              <div>
                <strong className="text-gray-900">Chat with Dr.Doc</strong>
                <p className="text-sm text-gray-600 mt-1">Ask questions about your document and get accurate answers</p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">4</span>
    <div>
                <strong className="text-gray-900">Enable Web Search (Optional)</strong>
                <p className="text-sm text-gray-600 mt-1">For complex questions, enable web search to get additional context</p>
              </div>
            </li>
          </ol>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Privacy & Security</h2>
          <p className="text-gray-700 leading-relaxed">
            Your documents are processed securely and stored locally. We use vector embeddings to enable 
            fast and accurate document search. Your data remains private and is not shared with third parties.
      </p>
        </Card>
    </div>
    </main>
  );
}
