import os
import tempfile
import pymupdf4llm
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from typing import List, Any
from sentence_transformers import SentenceTransformer
import uuid
import chromadb
from langchain_core.documents import Document
import pymupdf

class RAGSearch:
    
    def __init__(self, file):
        self.temp_file_path = None
        self.file = file
        self.docs = None
        self.chunks = None
        self.embeddings = None
        self.model = None
        self.collection = None
        self.pdf_bytes = None
        
    async def load_file(self):
        
        try:
            contents = await self.file.read()
            
        finally:
            await self.file.close()
        self.pdf_bytes = contents
        return contents

    
    def cleanup(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

        
    
    def read_pdf(self):
        doc = pymupdf.open(stream=self.pdf_bytes, filetype="pdf")

        try:
            self.docs = pymupdf4llm.to_markdown(doc, page_chunks=True)
        finally:
            doc.close()
        return self.docs
    
    def split_file(self) -> List[Document]:
        header_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
                
            )
        size_splitter = RecursiveCharacterTextSplitter(chunk_size =700,
            chunk_overlap = 100,)
        
        chunks = []
        
        for i, doc in enumerate(self.docs):
            text = doc['text'].strip()
            if not text:
                continue
            
            doc_no = doc["metadata"].get("page", i+1)
            
            for section in header_splitter.split_text(text):
                for c in size_splitter.split_documents([section]):
                    c.metadata["page"] = doc_no
                    
                    chunks.append(c)
                
        
        self.chunks = chunks
        return self.chunks
        
        
    
    
    def embed_chunks(self, model_name: str = "all-MiniLM-L6-v2" ):
        if(self.model == None):
                self.model = SentenceTransformer(model_name)


        
    
        texts = [c.page_content for c in self.chunks]
    
        self.embeddings = self.model.encode(texts)
        return self.embeddings, self.model
    
    def add_documents(self):
        ids, metadatas, texts, embs = [], [], [], []

        for i, (chunk, vec) in enumerate(zip(self.chunks, self.embeddings)):
            if not chunk.page_content.strip():
                continue
            meta = {k: v for k, v in chunk.metadata.items()
                    if isinstance(v, (str, int, float, bool))}
            meta["chunk_index"] = i
            meta["content_length"] = len(chunk.page_content)

            ids.append(f"chunk_{uuid.uuid4().hex[:8]}_{i}")
            metadatas.append(meta)
            texts.append(chunk.page_content)
            embs.append(vec.tolist())

        if ids:
            self.collection.add(ids=ids, embeddings=embs, metadatas=metadatas, documents=texts)
        return self.collection
    
    def vector_store(self):
        client = chromadb.PersistentClient(path="data/vector_store")
        try:
            client.delete_collection("pdf_documents")
        except Exception:
            pass
        self.collection = client.create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"},
)
        return self.add_documents()
    
    def search(self, query: str, k: int = 4):
        q = self.model.encode([query]).tolist()
        return self.collection.query(query_embeddings=q, n_results=k)