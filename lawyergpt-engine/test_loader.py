from ingestion.loader import load_from_uploads
from ingestion.chunker import chunk_documents
from ingestion.embedder import embed_texts
from ingestion.vector_store_loader import load_chunks
from core.vector_store import get_collection

# Step 1 - Load
print("=== STEP 1: LOADING ===")
docs = load_from_uploads("legal_fundamentals.pdf")
print(f"Loaded {len(docs)} pages")

# Step 2 - Chunk
print("\n=== STEP 2: CHUNKING ===")
chunks = chunk_documents(docs)
print(f"Produced {len(chunks)} chunks")
for i, chunk in enumerate(chunks[:3]):
    print(f"\nChunk {i+1} — {chunk.metadata['chunk_id']}")
    print(chunk.page_content[:300])

# Step 3 - Embed
print("\n=== STEP 3: EMBEDDING ===")
texts = [c.page_content for c in chunks[:3]]
vectors = embed_texts(texts)
print(f"Embedded {len(vectors)} chunks")
print(f"Vector dimensions: {len(vectors[0])}")
print("Embedding successful!")

# Step 4 - Load into ChromaDB
print("\n=== STEP 4: LOADING INTO CHROMADB ===")
load_chunks(chunks)
collection = get_collection()
count = collection.count()
print(f"ChromaDB now contains {count} vectors")
print("Ingestion complete!")
