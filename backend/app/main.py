import os
import uuid
import json
import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db, init_db, IS_SQLITE, engine
from app.db.vector_math import cosine_similarity, parse_vector
from app.models.models import Document, Insight, MentalModel, Quote, Vocabulary, KnowledgeNode, KnowledgeEdge
from app.services.extractor import get_youtube_video_id, fetch_youtube_transcript, fetch_youtube_metadata, parse_pdf, parse_docx, parse_txt
from app.services.embedding import get_embedding
from app.agents.pipeline import run_compilation_pipeline
from app.services.google_workspace import GoogleWorkspaceService

app = FastAPI(title="CogniWeave Knowledge Compiler API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

# 1. HTML View endpoint for local files/documents
@app.get("/api/documents/{doc_id}/view", response_class=HTMLResponse)
async def view_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    link = doc.google_doc_link
    if link and link.startswith("http") and "/api/documents/" not in link:
        # Redirect to external Google Doc
        return RedirectResponse(link)
        
    # Read local file
    local_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'local_drive'))
    safe_title = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in doc.title]).strip()
    file_name = f"{safe_title}_{doc.id[:8]}.txt"
    
    # Locate file in subdirectories
    file_path = None
    for root, dirs, files in os.walk(local_root):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            break
            
    if not file_path or not os.path.exists(file_path):
        # Fallback to searching without ID suffix
        alt_name = f"{safe_title}.txt"
        for root, dirs, files in os.walk(local_root):
            if alt_name in files:
                file_path = os.path.join(root, alt_name)
                break

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Local compilation document not found on disk.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Prettify the plain text document compilation for web view
    lines = content.split('\n')
    formatted_sections = []
    
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("## ") or line_strip.startswith("### "):
            formatted_sections.append(f"<h2 class='text-2xl font-bold mt-8 mb-4 border-b border-indigo-900 pb-2 text-indigo-300'>{line_strip.replace('##', '').replace('###', '')}</h2>")
        elif line_strip.startswith("- "):
            formatted_sections.append(f"<li class='ml-6 list-disc mb-2 text-gray-300'>{line_strip[2:]}</li>")
        elif line_strip.startswith("* "):
            formatted_sections.append(f"<li class='ml-8 list-circle mb-1 text-gray-400'>{line_strip[2:]}</li>")
        elif line_strip.startswith("> "):
            formatted_sections.append(f"<blockquote class='border-l-4 border-violet-500 pl-4 py-1 italic bg-indigo-950/20 text-gray-200 my-4'>{line_strip[2:]}</blockquote>")
        elif line_strip == "=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*":
            continue
        elif "COGNIVEAVE KNOWLEDGE COMPILATION" in line_strip:
            formatted_sections.append(f"<h1 class='text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-500 mb-6'>{line_strip}</h1>")
        else:
            formatted_sections.append(f"<p class='mb-3 text-gray-300 leading-relaxed'>{line}</p>")

    body_html = "\n".join(formatted_sections)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{doc.title} - Preview</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #07070a; color: #f3f4f6; }}
            .text-gradient {{
                background: linear-gradient(to right, #a78bfa, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
        </style>
    </head>
    <body class="p-8 max-w-4xl mx-auto font-sans leading-relaxed">
        <div class="mb-8 border-b border-[rgba(255,255,255,0.06)] pb-6 flex justify-between items-start">
            <div>
                <span class="text-xs font-semibold text-indigo-400 tracking-widest uppercase">CogniWeave Archive</span>
                <h1 class="text-3xl font-extrabold text-white mt-1">{doc.title}</h1>
                <p class="text-sm text-gray-400 mt-2">Speaker: {doc.speaker} | Source: {doc.source}</p>
            </div>
            <div class="flex gap-2">
                <a href="{doc.url}" target="_blank" class="px-4 py-2 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 rounded-xl text-sm font-semibold transition-all">Original Source</a>
                <a href="http://localhost:3000" class="px-4 py-2 bg-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.06)] text-white border border-[rgba(255,255,255,0.05)] rounded-xl text-sm font-semibold transition-all">Dashboard</a>
            </div>
        </div>
        <div class="space-y-6">
            {body_html}
        </div>
    </body>
    </html>
    """
    return html_content

# 2. Ingest YouTube/Podcast URL
@app.post("/api/ingest/url")
async def ingest_url(payload: dict, db: AsyncSession = Depends(get_db)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    video_id = get_youtube_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # Fetch transcript & metadata
    transcript = fetch_youtube_transcript(video_id)
    if not transcript:
        raise HTTPException(status_code=400, detail="Could not retrieve YouTube transcript")

    metadata = fetch_youtube_metadata(video_id)
    
    # Generate unique ID upfront to pass to Google Doc preview link builder
    doc_id = str(uuid.uuid4())

    # Run AI Compilation Agent Pipeline
    pipeline_result = await run_compilation_pipeline(transcript, source_url=url)
    
    # Update pipeline keys with metadata values
    pipeline_result["title"] = metadata.get("title", pipeline_result.get("title"))
    pipeline_result["speaker"] = metadata.get("speaker", pipeline_result.get("speaker"))
    pipeline_result["source"] = "YouTube"

    # Save outputs to local_drive or Google Drive
    gw_service = GoogleWorkspaceService()
    doc_link = await gw_service.save_compilation(pipeline_result, category="YouTube", doc_id=doc_id)

    # Write record to db
    duration_sec = pipeline_result.get("duration", 0)
    
    doc = Document(
        id=doc_id,
        title=pipeline_result.get("title", "Untitled"),
        speaker=pipeline_result.get("speaker", "Unknown"),
        date=datetime.date.today(),
        duration=duration_sec,
        source="YouTube",
        url=url,
        google_doc_link=doc_link,
        status="processed",
        communication_patterns=json.dumps(pipeline_result.get("patterns", [])),
        content_assets=json.dumps(pipeline_result.get("content_assets", {}))
    )
    db.add(doc)

    # Save child models
    for ins in pipeline_result.get("insights", []):
        ins_id = str(uuid.uuid4())
        emb = await get_embedding(ins.get("insight", ""))
        insight = Insight(
            id=ins_id,
            document_id=doc_id,
            insight=ins.get("insight"),
            why_it_matters=ins.get("why_it_matters"),
            application=ins.get("application"),
            action=ins.get("action"),
            embedding=json.dumps(emb)
        )
        db.add(insight)

    for mm in pipeline_result.get("mental_models", []):
        mm_id = str(uuid.uuid4())
        mental_model = MentalModel(
            id=mm_id,
            document_id=doc_id,
            name=mm.get("name"),
            definition=mm.get("definition"),
            explanation=mm.get("explanation"),
            example=mm.get("example"),
            application=mm.get("application")
        )
        db.add(mental_model)

    for v in pipeline_result.get("vocabulary", []):
        v_id = str(uuid.uuid4())
        vocab = Vocabulary(
            id=v_id,
            document_id=doc_id,
            word=v.get("word"),
            meaning=v.get("meaning"),
            usage=v.get("usage"),
            origin=v.get("origin"),
            simpler_synonym=v.get("simpler_synonym")
        )
        db.add(vocab)

    for q in pipeline_result.get("quotes", []):
        q_id = str(uuid.uuid4())
        quote = Quote(
            id=q_id,
            document_id=doc_id,
            quote=q.get("quote"),
            meaning=q.get("meaning"),
            why_memorable=q.get("why_memorable"),
            counterargument=q.get("counterargument")
        )
        db.add(quote)

    for node in pipeline_result.get("knowledge_graph", {}).get("nodes", []):
        node_id = str(uuid.uuid4())
        emb = await get_embedding(node.get("title", ""))
        knode = KnowledgeNode(
            id=node_id,
            document_id=doc_id,
            title=node.get("title"),
            description=node.get("description"),
            embedding=json.dumps(emb)
        )
        db.add(knode)

    await db.commit()

    return {
        "title": pipeline_result.get("title", "Untitled"),
        "doc_link": doc_link,
        "data": pipeline_result
    }

# 3. Ingest PDF/Docx/TXT Document File
@app.post("/api/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    file_bytes = await file.read()
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        text = parse_pdf(file_bytes)
        source = "PDF"
    elif ext in (".docx", ".doc"):
        text = parse_docx(file_bytes)
        source = "DOCX"
    elif ext in (".txt", ".md"):
        text = parse_txt(file_bytes)
        source = "TXT"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'")

    if not text.strip():
        raise HTTPException(status_code=400, detail="The document file is empty or could not be parsed.")

    doc_id = str(uuid.uuid4())

    pipeline_result = await run_compilation_pipeline(text, source_url=filename)
    pipeline_result["title"] = filename
    pipeline_result["speaker"] = "Document Author"
    pipeline_result["source"] = source

    gw_service = GoogleWorkspaceService()
    doc_link = await gw_service.save_compilation(pipeline_result, category="Document", doc_id=doc_id)

    doc = Document(
        id=doc_id,
        title=filename,
        speaker="Document Author",
        date=datetime.date.today(),
        duration=pipeline_result.get("duration", 60),
        source=source,
        url=filename,
        google_doc_link=doc_link,
        status="processed",
        communication_patterns=json.dumps(pipeline_result.get("patterns", [])),
        content_assets=json.dumps(pipeline_result.get("content_assets", {}))
    )
    db.add(doc)

    for ins in pipeline_result.get("insights", []):
        ins_id = str(uuid.uuid4())
        emb = await get_embedding(ins.get("insight", ""))
        insight = Insight(
            id=ins_id,
            document_id=doc_id,
            insight=ins.get("insight"),
            why_it_matters=ins.get("why_it_matters"),
            application=ins.get("application"),
            action=ins.get("action"),
            embedding=json.dumps(emb)
        )
        db.add(insight)

    for mm in pipeline_result.get("mental_models", []):
        mm_id = str(uuid.uuid4())
        mental_model = MentalModel(
            id=mm_id,
            document_id=doc_id,
            name=mm.get("name"),
            definition=mm.get("definition"),
            explanation=mm.get("explanation"),
            example=mm.get("example"),
            application=mm.get("application")
        )
        db.add(mental_model)

    for v in pipeline_result.get("vocabulary", []):
        v_id = str(uuid.uuid4())
        vocab = Vocabulary(
            id=v_id,
            document_id=doc_id,
            word=v.get("word"),
            meaning=v.get("meaning"),
            usage=v.get("usage"),
            origin=v.get("origin"),
            simpler_synonym=v.get("simpler_synonym")
        )
        db.add(vocab)

    for q in pipeline_result.get("quotes", []):
        q_id = str(uuid.uuid4())
        quote = Quote(
            id=q_id,
            document_id=doc_id,
            quote=q.get("quote"),
            meaning=q.get("meaning"),
            why_memorable=q.get("why_memorable"),
            counterargument=q.get("counterargument")
        )
        db.add(quote)

    for node in pipeline_result.get("knowledge_graph", {}).get("nodes", []):
        node_id = str(uuid.uuid4())
        emb = await get_embedding(node.get("title", ""))
        knode = KnowledgeNode(
            id=node_id,
            document_id=doc_id,
            title=node.get("title"),
            description=node.get("description"),
            embedding=json.dumps(emb)
        )
        db.add(knode)

    await db.commit()

    return {
        "title": filename,
        "doc_link": doc_link,
        "data": pipeline_result
    }

# 4. Get Documents List
@app.get("/api/documents")
async def get_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    return documents

# 5. Rate Document
@app.post("/api/documents/{doc_id}/rate")
async def rate_document(doc_id: str, payload: dict, db: AsyncSession = Depends(get_db)):
    rating = payload.get("rating", 0)
    await db.execute(update(Document).where(Document.id == doc_id).values(personal_rating=rating))
    await db.commit()
    return {"message": "Rating updated successfully"}

# 6. Delete Document
@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Document).where(Document.id == doc_id))
    await db.commit()
    return {"message": "Document deleted successfully"}

# 7. Semantic Search
@app.get("/api/search")
async def search_insights(query: str, category: str = None, db: AsyncSession = Depends(get_db)):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    query_vector = await get_embedding(query)
    
    result = await db.execute(
        select(Insight, Document)
        .join(Document, Insight.document_id == Document.id)
    )
    rows = result.all()
    
    matches = []
    for insight, doc in rows:
        if category and doc.source.lower() != category.lower():
            continue
            
        emb = insight.embedding
        if isinstance(emb, str):
            emb_vector = parse_vector(emb)
        else:
            emb_vector = emb
            
        sim = cosine_similarity(query_vector, emb_vector)
        matches.append({
            "insight": insight.insight,
            "why_it_matters": insight.why_it_matters,
            "application": insight.application,
            "action": insight.action,
            "document_title": doc.title,
            "document_source": doc.source,
            "document_url": doc.url,
            "google_doc_link": doc.google_doc_link,
            "similarity": sim
        })
        
    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)[:10]
    return matches

# 8. Knowledge Graph Nodes and Edges
@app.get("/api/graph")
async def get_graph(db: AsyncSession = Depends(get_db)):
    nodes_res = await db.execute(select(KnowledgeNode))
    nodes = nodes_res.scalars().all()
    
    node_ids = [n.id for n in nodes]
    edges_res = await db.execute(
        select(KnowledgeEdge).where(
            KnowledgeEdge.source_node_id.in_(node_ids) | 
            KnowledgeEdge.target_node_id.in_(node_ids)
        )
    )
    edges = edges_res.scalars().all()
    
    return {
        "nodes": [{"id": n.id, "label": n.title, "description": n.description, "doc_id": n.document_id} for n in nodes],
        "edges": [{"id": e.id, "source": e.source_node_id, "target": e.target_node_id, "label": e.relationship_type} for e in edges]
    }

# 9. Weekly Intelligence Report
@app.get("/api/report")
async def get_intelligence_report(db: AsyncSession = Depends(get_db)):
    docs_res = await db.execute(select(Document))
    docs = docs_res.scalars().all()
    
    insights_res = await db.execute(select(Insight))
    insights = insights_res.scalars().all()
    
    vocab_res = await db.execute(select(Vocabulary))
    vocab = vocab_res.scalars().all()
    
    total_hours = sum(d.duration for d in docs) / 3600.0 if docs else 0.0
    
    return {
        "hours_consumed": round(total_hours, 1),
        "insights_extracted": len(insights),
        "actions_completed": len([i for i in insights if i.action]),
        "mental_models_learned": len(docs) * 2,
        "vocabulary_mastered": len(vocab),
        "most_recurring_themes": ["Compounding Systems", "Leverage", "Optionality"],
        "blind_spots": ["Short-term trade-offs of systems transition", "Risk of choice over-analysis"],
        "recent_activity": [{"title": d.title, "source": d.source, "date": d.date.isoformat()} for d in docs[:5]]
    }
