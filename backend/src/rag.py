from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


def rag_search(query, retrieved_docs, top_k = 3):
    
    if not retrieved_docs:
        return "I couldn't find that in the document."
    context = "\n\n".join(
        f"[Page {d['metadata'].get('page', 0) + 1}] {d['content']}"
        for d in retrieved_docs
    )

    
    prompt = f"""You are a helpful assistant that answers questions using ONLY the provided context from a PDF.

Rules:
- Use only the context below. Do not use outside knowledge.
- If the answer is not in the context, say: "I couldn't find that in the document."
- Be concise and accurate. Quote or paraphrase the relevant part.
- Mention the page number when available.
    
    Context:
    {context}
    
    Question: {query}
    
    Answer:
    
    
    """
    llm = ChatGroq(groq_api_key= groq_api_key, model_name= "openai/gpt-oss-120b", temperature=1, max_tokens=1024)

    response= llm.invoke([prompt.format(context=context, query=query)])
    return response.content



