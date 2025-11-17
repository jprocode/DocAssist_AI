# DocAssist AI

An intelligent document assistant that helps you understand and interact with PDF documents. Upload PDFs, get AI-powered summaries, and chat with Dr.Doc to answer questions about your documents.

## Features

- **Smart Document Upload**: Drag and drop or browse to upload PDF documents (up to 50MB)
- **AI-Powered Summaries**: Get instant, comprehensive summaries of your documents
- **Chat with Dr.Doc**: Ask questions and get answers based on your document content
- **Optional Web Search**: Enable web search for questions that need additional context
- **Hallucination Prevention**: Dr.Doc strictly uses only your document content, preventing AI hallucinations
- **Document Management**: View, manage, and organize all your uploaded documents
- **Streaming Responses**: Real-time streaming chat responses for better UX
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI API**: For embeddings and chat completions
- **FAISS**: Vector similarity search for document retrieval
- **Tavily API**: Web search integration (optional)
- **pdfplumber**: PDF text extraction

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **react-hot-toast**: Toast notifications

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API key
- Tavily API key (optional, for web search)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
VECTOR_DIR=./data/vector_store
```

5. Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file (optional, defaults to localhost:8000):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Upload a Document**: Go to the home page and upload a PDF document
2. **View Summary**: The AI will automatically generate a summary of your document
3. **Ask Questions**: Use the chat interface to ask Dr.Doc questions about your document
4. **Enable Web Search**: Toggle web search for questions that need additional context
5. **Manage Documents**: Visit the Documents page to view and manage all your uploaded documents

## API Endpoints

### Upload Document
```
POST /api/upload
Content-Type: multipart/form-data
Body: file (PDF)
```

### Get Summary
```
POST /api/summarize?doc_id={doc_id}
```

### Ask Question
```
POST /api/{doc_id}
Body: {
  "question": "string",
  "use_web_search": boolean,
  "stream": boolean
}
```

### List Documents
```
GET /api/documents
```

### Get Document
```
GET /api/documents/{doc_id}
```

### Delete Document
```
DELETE /api/documents/{doc_id}
```

## Project Structure

```
DocAssist_AI/
├── backend/
│   ├── routers/          # API route handlers
│   ├── services/          # Business logic (QA, summarization, web search)
│   ├── db/               # Vector store implementation
│   ├── utils/            # Configuration and utilities
│   └── main.py           # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js app router pages
│   │   ├── components/   # Reusable React components
│   │   └── lib/          # API client and utilities
│   └── package.json
└── README.md
```

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY`: Required. Your OpenAI API key
- `OPENAI_CHAT_MODEL`: Optional. Defaults to `gpt-4o-mini`
- `OPENAI_EMBEDDING_MODEL`: Optional. Defaults to `text-embedding-3-small`
- `TAVILY_API_KEY`: Optional. Required for web search functionality
- `VECTOR_DIR`: Optional. Defaults to `./data/vector_store`
- `ENVIRONMENT`: Optional. Set to `production` for production mode. Defaults to `development`
- `ALLOWED_ORIGINS`: Optional. Comma-separated list of allowed CORS origins for production. Defaults to `http://localhost:3000,http://localhost:3001`

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Optional. Backend API URL. Defaults to `http://localhost:8000/api`

## Development

### Running Tests

**Backend Tests:**
```bash
cd backend
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chunker.py
```

**Frontend Tests:**
```bash
cd frontend
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### Building for Production

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## Security Notes

- **CORS**: In development mode, CORS allows all origins. In production (set `ENVIRONMENT=production`), CORS is restricted to `ALLOWED_ORIGINS`.
- **File Uploads**: Limited to 50MB and PDF files only.
- **API Keys**: Should be kept secure and never committed to version control. Use environment variables.
- **Rate Limiting**: Consider implementing rate limiting for production use.
- **Input Validation**: All inputs are validated on both frontend and backend.

## License

This project is private and proprietary.

## Support

For issues or questions, please contact the development team.

