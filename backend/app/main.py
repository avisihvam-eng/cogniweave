import os
import uuid
import json
import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Startup event to create tables
@app.on_event("startup")
async def on_startup():
    print("Initializing database...")
    await init_db()
    print("Database tables initialized successfully!")

# 1. Auth Endpoint (Mock/Simple OAuth flow)
@app.post("/api/auth/google")
async def google_auth(payload: dict):
    # In a full production setup, this would exchange an authorization code for tokens.
    # For dev, we return mock credentials or store what the user provides.
    return {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "email": "user@domain.com",
        "name": "Avinash Shukla"
    }

# 2. Ingest URL (YouTube or Web)
@app.post("/api/ingest/url")
async def ingest_url(payload: dict, db: AsyncSession = Depends(get_db)):
    url = payload.get("url")
    user_profile = payload.get("user_profile", {"career": "Recruiter learning AI", "goals": "Understand AI agents", "interests": "AI, Systems thinking"})
    creds = payload.get("google_creds") # Optional OAuth credentials

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    video_id = get_youtube_video_id(url)
    if video_id:
        print(f"Detected YouTube URL. Video ID: {video_id}")
        transcript = fetch_youtube_transcript(video_id)
        metadata = fetch_youtube_metadata(video_id)
        source = "YouTube"
    else:
        # Generic URL Ingestion stub - In production, we'd scrape the page.
        transcript = "This is a placeholder transcript scraped from the provided URL: " + url
        metadata = {
            "title": "Article from " + url.split("/")[2] if len(url.split("/")) > 2 else url,
            "speaker": "Unknown Author",
            "source": "Article",
            "url": url
        }
        source = "Article"

    if not transcript:
        # Fallback transcript if fetch failed
        transcript = f"Mock transcript for content at {url}. Discussion about systems thinking, leverage, and compounding value in organizational development."

    # Run Multi-Agent Ingestion Pipeline
    pipeline_result = await run_compilation_pipeline(transcript, source_url=url, user_profile=user_profile)
    
    # Save compilation to Google Drive / local files
    gw_service = GoogleWorkspaceService(creds)
    doc_link = await gw_service.save_compilation(pipeline_result, category=source + "s")

    # Save to SQL Database
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=pipeline_result.get("title", metadata["title"]),
        speaker=pipeline_result.get("speaker", metadata["speaker"]),
        date=datetime.date.today(),
        duration=pipeline_result.get("duration", 0),
        source=source,
        url=url,
        google_doc_link=doc_link,
        status="processed"
    )
    db.add(doc)

    # Save Insights with Embeddings
    for ins in pipeline_result.get("insights", []):
        text_for_embedding = ins.get("insight", "")
        vector = await get_embedding(text_for_embedding)
        db_vector = json.dumps(vector) if IS_SQLITE else vector
        
        insight_obj = Insight(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            insight=ins.get("insight"),
            why_it_matters=ins.get("why_it_matters"),
            application=ins.get("application"),
            action=ins.get("action"),
            embedding=db_vector
        )
        db.add(insight_obj)

    # Save Mental Models
    for mm in pipeline_result.get("mental_models", []):
        mm_obj = MentalModel(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            name=mm.get("name"),
            definition=mm.get("definition"),
            explanation=mm.get("explanation"),
            example=mm.get("example"),
            application=mm.get("application")
        )
        db.add(mm_obj)

    # Save Vocabulary
    for v in pipeline_result.get("vocabulary", []):
        v_obj = Vocabulary(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            word=v.get("word"),
            meaning=v.get("meaning"),
            usage=v.get("usage"),
            origin=v.get("origin"),
            simpler_synonym=v.get("simpler_synonym")
        )
        db.add(v_obj)

    # Save Quotes
    for q in pipeline_result.get("quotes", []):
        q_obj = Quote(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            quote=q.get("quote"),
            meaning=q.get("meaning"),
            why_memorable=q.get("why_memorable"),
            counterargument=q.get("counterargument")
        )
        db.add(q_obj)

    # Save Knowledge Graph Nodes & Edges
    node_mapping = {}
    for node in pipeline_result.get("knowledge_graph", {}).get("nodes", []):
        node_id = str(uuid.uuid4())
        node_text = f"{node['title']}: {node['description']}"
        vector = await get_embedding(node_text)
        db_vector = json.dumps(vector) if IS_SQLITE else vector
        
        kn_obj = KnowledgeNode(
            id=node_id,
            document_id=doc_id,
            title=node["title"],
            description=node["description"],
            embedding=db_vector
        )
        db.add(kn_obj)
        node_mapping[node["title"]] = node_id

    # Add edges
    for edge in pipeline_result.get("knowledge_graph", {}).get("edges", []):
        source_id = node_mapping.get(edge["source"])
        target_id = node_mapping.get(edge["target"])
        if source_id and target_id:
            edge_obj = KnowledgeEdge(
                id=str(uuid.uuid4()),
                source_node_id=source_id,
                target_node_id=target_id,
                relationship_type=edge["relationship"]
            )
            db.add(edge_obj)

    await db.commit()

    return {
        "message": "Content successfully ingested",
        "document_id": doc_id,
        "title": doc.title,
        "doc_link": doc_link,
        "data": pipeline_result
    }

# 3. Ingest Uploaded File
@app.post("/api/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    user_profile: str = Form("{}"),
    google_creds: str = Form("null"),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    if ext == "pdf":
        text = parse_pdf(contents)
        source = "Research Paper"
    elif ext in ("docx", "doc"):
        text = parse_docx(contents)
        source = "Book"
    else:
        text = parse_txt(contents)
        source = "Article"

    if not text:
        raise HTTPException(status_code=400, detail="Failed to parse text from the uploaded file")

    profile_dict = json.loads(user_profile)
    creds_dict = json.loads(google_creds)

    pipeline_result = await run_compilation_pipeline(text[:15000], source_url=filename, user_profile=profile_dict)
    pipeline_result["title"] = filename.rsplit(".", 1)[0]
    pipeline_result["source"] = source

    gw_service = GoogleWorkspaceService(creds_dict)
    doc_link = await gw_service.save_compilation(pipeline_result, category=source + "s")

    # Save to SQL
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=filename.rsplit(".", 1)[0],
        speaker="Author",
        date=datetime.date.today(),
        duration=0,
        source=source,
        url=filename,
        google_doc_link=doc_link,
        status="processed"
    )
    db.add(doc)
    
    # Save Insights, Models, Vocab, Quotes, Graph (similar to URL flow)
    for ins in pipeline_result.get("insights", []):
        vector = await get_embedding(ins.get("insight", ""))
        db_vector = json.dumps(vector) if IS_SQLITE else vector
        db.add(Insight(
            id=str(uuid.uuid4()), document_id=doc_id,
            insight=ins.get("insight"), why_it_matters=ins.get("why_it_matters"),
            application=ins.get("application"), action=ins.get("action"),
            embedding=db_vector
        ))
        
    for mm in pipeline_result.get("mental_models", []):
        db.add(MentalModel(
            id=str(uuid.uuid4()), document_id=doc_id,
            name=mm.get("name"), definition=mm.get("definition"),
            explanation=mm.get("explanation"), example=mm.get("example"),
            application=mm.get("application")
        ))
        
    for v in pipeline_result.get("vocabulary", []):
        db.add(Vocabulary(
            id=str(uuid.uuid4()), document_id=doc_id,
            word=v.get("word"), meaning=v.get("meaning"),
            usage=v.get("usage"), origin=v.get("origin"),
            simpler_synonym=v.get("simpler_synonym")
        ))

    for q in pipeline_result.get("quotes", []):
        db.add(Quote(
            id=str(uuid.uuid4()), document_id=doc_id,
            quote=q.get("quote"), meaning=q.get("meaning"),
            why_memorable=q.get("why_memorable"), counterargument=q.get("counterargument")
        ))

    await db.commit()

    return {
        "message": "File successfully ingested",
        "document_id": doc_id,
        "title": doc.title,
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
    
    # Fetch all insights and their documents to calculate similarity
    result = await db.execute(
        select(Insight, Document)
        .join(Document, Insight.document_id == Document.id)
    )
    rows = result.all()
    
    matches = []
    for insight, doc in rows:
        # Check source category filter
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
        
    # Sort by similarity desc
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
    # Aggregates key data for the intelligence dashboard
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
        "mental_models_learned": len(docs) * 2, # Stub indicator
        "vocabulary_mastered": len(vocab),
        "most_recurring_themes": ["Compounding Systems", "Leverage", "Optionality"],
        "blind_spots": ["Short-term trade-offs of systems transition", "Risk of choice over-analysis"],
        "recent_activity": [{"title": d.title, "source": d.source, "date": d.date.isoformat()} for d in docs[:5]]
    }
