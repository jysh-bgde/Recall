from sentence_transformers import SentenceTransformer

def retrieve_docs(model, collection, query):
   
    query_embedding = model.encode([query])[0]
    
    
    results = collection.query(
        query_embeddings = [query_embedding.tolist()],
        n_results = 5
    )
    
    retrieved_docs = []
    
    if results['documents'] and results['documents'][0]:
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        ids = results['ids'][0]
        
        for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):
            similarity_score = 1 - distance
                    
            if similarity_score >= 0.0:
                retrieved_docs.append({
                            'id': doc_id,
                            'content': document,
                            'metadata': metadata,
                            'similarity_score': similarity_score,
                            'distance': distance,
                            'rank': i + 1
                })
                
                
    return retrieved_docs