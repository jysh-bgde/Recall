from src.RAGSearch import RAGSearch
def pdf_processor(rag: RAGSearch):
    rag.read_pdf()
    rag.split_file()
    rag.embed_chunks()
    rag.vector_store()