from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base, IS_SQLITE
import datetime

EmbeddingType = Text

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    speaker = Column(String(255))
    date = Column(Date)
    duration = Column(Integer)
    source = Column(String(50))
    url = Column(String(555))
    google_doc_link = Column(String(555))
    status = Column(String(50), default="processed")
    personal_rating = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    
    # Store extended PRD features as JSON strings
    communication_patterns = Column(Text)
    content_assets = Column(Text)

    insights = relationship("Insight", back_populates="document", cascade="all, delete-orphan")
    mental_models = relationship("MentalModel", back_populates="document", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="document", cascade="all, delete-orphan")
    vocabulary = relationship("Vocabulary", back_populates="document", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="document", cascade="all, delete-orphan")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"))
    insight = Column(Text, nullable=False)
    why_it_matters = Column(Text)
    application = Column(Text)
    action = Column(Text)
    embedding = Column(EmbeddingType)

    document = relationship("Document", back_populates="insights")


class MentalModel(Base):
    __tablename__ = "mental_models"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    definition = Column(Text)
    explanation = Column(Text)
    example = Column(Text)
    application = Column(Text)

    document = relationship("Document", back_populates="mental_models")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"))
    quote = Column(Text, nullable=False)
    meaning = Column(Text)
    why_memorable = Column(Text)
    counterargument = Column(Text)

    document = relationship("Document", back_populates="quotes")


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"))
    word = Column(String(100), nullable=False)
    meaning = Column(Text)
    usage = Column(Text)
    origin = Column(Text)
    simpler_synonym = Column(String(100))

    document = relationship("Document", back_populates="vocabulary")


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    embedding = Column(EmbeddingType)

    document = relationship("Document", back_populates="knowledge_nodes")


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = Column(String(50), primary_key=True)
    source_node_id = Column(String(50), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"))
    target_node_id = Column(String(50), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"))
    relationship_type = Column(String(50), nullable=False)
