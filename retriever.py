"""
Retrieval module using TF-IDF for lightweight semantic search.
No heavy dependencies - uses scikit-learn.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

from knowledge_processor import get_all_chunks
from config import TOP_K_RESULTS


class Retriever:
    """TF-IDF based retriever for knowledge base chunks."""
    
    def __init__(self):
        self.chunks: List[Dict[str, str]] = []
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            max_features=5000
        )
        self.tfidf_matrix = None
        self._initialize()
    
    def _initialize(self):
        """Load chunks and create TF-IDF matrix."""
        self.chunks = get_all_chunks()
        texts = [chunk['text'] for chunk in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        print(f"Retriever initialized with {len(self.chunks)} chunks")
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[Dict[str, str], float]]:
        """
        Search for relevant chunks given a query.
        
        Args:
            query: User's question
            top_k: Number of results to return (default from config)
            
        Returns:
            List of tuples: (chunk_dict, similarity_score)
        """
        if top_k is None:
            top_k = TOP_K_RESULTS
        
        # Transform query to TF-IDF vector
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity with all chunks
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top-k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Return chunks with scores
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include if there's some match
                results.append((self.chunks[idx], float(similarities[idx])))
        
        return results
    
    def get_context(self, query: str, top_k: int = None) -> str:
        """
        Get formatted context string for the LLM prompt.
        
        Args:
            query: User's question
            top_k: Number of chunks to include
            
        Returns:
            Formatted context string
        """
        results = self.search(query, top_k)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, (chunk, score) in enumerate(results, 1):
            context_parts.append(f"[{chunk['category']}]: {chunk['text']}")
        
        return "\n\n".join(context_parts)


# Singleton instance for reuse
_retriever_instance = None


def get_retriever() -> Retriever:
    """Get or create the retriever singleton."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance


if __name__ == "__main__":
    # Test the retriever
    retriever = get_retriever()
    
    test_queries = [
        "What is NavShiksha?",
        "How do I register as a student?",
        "What tools are available on the whiteboard?",
        "How are certificates verified?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        results = retriever.search(query, top_k=3)
        for chunk, score in results:
            print(f"\n[Score: {score:.3f}] [{chunk['category']}]")
            print(chunk['text'][:150] + "...")
