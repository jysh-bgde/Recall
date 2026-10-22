from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import os
from pydantic import BaseModel
from src.process_pdf import pdf_processor
from src.retriever import retrieve_docs
from sentence_transformers import SentenceTransformer
from src.RAGSearch import RAGSearch
from src.rag import rag_search
import uvicorn

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["*"],
)

app.state.model = None
app.state.collection = None

class ChatRequest(BaseModel):
    query: str


    
        

@app.on_event("startup")
def load_model():
    app.state.model = SentenceTransformer("all-MiniLM-L6-v2")

    


    
@app.get("/")
def home():

    return {"message": "hello world"}
        

@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    rag = RAGSearch(file)
    rag.model = app.state.model
    
        
    
    await rag.load_file()
                
    if not rag.pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    await run_in_threadpool(pdf_processor, rag)
    
    if not rag.chunks:
            raise HTTPException(status_code=400, detail="No extractable text (scanned PDF?)")
    
    app.state.collection = rag.collection    
        

    
        
    return {"message": "file uploaded", "chunks": len(rag.chunks)}



    
    
    
        
        
@app.post("/query")
async def query(req: ChatRequest):
    if not app.state.collection:

        raise HTTPException(status_code=400, detail="Upload a PDF first")

    docs = await run_in_threadpool(
        retrieve_docs, app.state.model, app.state.collection, req.query
    )
    answer = await run_in_threadpool(rag_search, req.query, docs)
    return {"answer": answer, "sources": [d["metadata"].get("page", 0) + 1 for d in docs]}
        
        
