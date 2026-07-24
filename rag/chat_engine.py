"""
RAG-based research assistant. Retrieves the most relevant already-summarized
news chunks from Chroma and asks the LLM to answer using only that context —
explaining mechanisms, never issuing buy/sell recommendations.
"""
from rag.build_index import get_embedder, get_collection
from utils.llm_client import call_llm

SYSTEM_PROMPT = (
    "You are a financial research assistant helping a student investor learn. "
    "You explain what happened and why it matters, using the context provided. "
    "You NEVER recommend buying, selling, or holding any security. "
    "If the context doesn't contain the answer, say so honestly instead of guessing. "
    "Cite sources by mentioning the outlet name inline."
)


def answer_question(question: str, n_results: int = 8) -> dict:
    embedder = get_embedder()
    collection = get_collection()

    if collection.count() == 0:
        return {
            "answer": "The research index is empty. Run the daily pipeline first "
                      "so there's summarized news to search over.",
            "sources": [],
        }

    query_vec = embedder.encode(question).tolist()
    results = collection.query(query_embeddings=[query_vec], n_results=min(n_results, collection.count()))

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context_blocks = []
    sources = []
    for doc, meta in zip(docs, metas):
        context_blocks.append(f"- {doc}\n  (source: {meta.get('source')}, {meta.get('published_at')})")
        sources.append({"url": meta.get("url"), "source": meta.get("source")})

    context = "\n\n".join(context_blocks)
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"

    answer = call_llm(prompt)
    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    result = answer_question("What happened in banking recently?")
    print(result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(" -", s["source"], s["url"])
