-- PostgreSQL + pgvector schema for RAG
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS ai;

CREATE TABLE IF NOT EXISTS ai.documents (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	doc_id TEXT,
	chunk_id INT,
	content TEXT NOT NULL,
	metadata JSONB,
	embedding vector(384),
	-- Add unique constraint for ON CONFLICT
	UNIQUE(doc_id, chunk_id)
);

-- ANN index; tune lists ~ sqrt(N)
CREATE INDEX IF NOT EXISTS documents_embedding_ivf
  ON ai.documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Tickets (mock)
CREATE TABLE IF NOT EXISTS ai.tickets (
	id TEXT PRIMARY KEY,
	description TEXT NOT NULL,
	priority TEXT NOT NULL CHECK (priority IN ('low','medium','high')),
	status TEXT NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);