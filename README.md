# 🚀 Antigravity — AI-Powered Knowledge Compiler

> Every podcast, lecture, YouTube video, article, PDF, or book becomes structured wisdom that compounds over time.

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Gemini](https://img.shields.io/badge/Gemini_2.5-Pro_%26_Flash-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

## What is Antigravity?

Antigravity is **not** a summarizer. It is **not** a note-taking app. It is a **knowledge compiler**.

It ingests content through a **12-agent AI pipeline** powered by Google Gemini, extracting:
- 🎯 **Core Insights** — What should I remember?
- ⚡ **Action Items** — What should I do?
- 🧠 **Mental Models** — How should I think?
- 💬 **Quotes** — What's worth repeating?
- 📖 **Vocabulary** — Words to master
- 🔄 **Contrarian Views** — What's the other side?
- 🕸️ **Knowledge Graph** — How does this connect to everything else?
- ✍️ **Content Drafts** — Ready-to-post tweets, LinkedIn posts, newsletters

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────┐
│   Next.js 16    │────▶│       FastAPI Backend         │
│   (Frontend)    │◀────│                               │
│  localhost:3000  │     │  ┌──────────────────────┐    │
└─────────────────┘     │  │  12 Gemini Agents     │    │
                        │  │  ├─ Ingestion          │    │
                        │  │  ├─ Signal Extraction  │    │
                        │  │  ├─ Mental Models      │    │
                        │  │  ├─ Vocabulary         │    │
                        │  │  ├─ Quote Intelligence  │    │
                        │  │  ├─ Contrarian          │    │
                        │  │  ├─ Content Creation    │    │
                        │  │  ├─ Knowledge Graph     │    │
                        │  │  └─ Personalization     │    │
                        │  └──────────────────────┘    │
                        │                               │
                        │  SQLite / PostgreSQL + pgvector│
                        │  Google Drive / Docs / Sheets  │
                        └──────────────────────────────┘
```

## Quick Start

### 1. Clone
```bash
git clone https://github.com/avisihvam-eng/antigravity.git
cd antigravity
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** and start compiling knowledge.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key ([Get one here](https://aistudio.google.com/apikey)) |
| `GOOGLE_CLIENT_ID` | Optional | For Google Drive/Docs/Sheets integration |
| `GOOGLE_CLIENT_SECRET` | Optional | For Google Workspace OAuth |

## Tech Stack

- **Frontend**: Next.js 16, TypeScript, Tailwind CSS v4, Lucide Icons
- **Backend**: FastAPI, SQLAlchemy (async), Pydantic
- **AI**: Google Gemini 2.5 Pro & Flash, text-embedding-004
- **Database**: SQLite (dev) / PostgreSQL + pgvector (prod)
- **Integrations**: Google Drive, Docs, Sheets

## License

MIT — Built with ❤️ by [Avinash Shukla](https://x.com/avinashivam)
