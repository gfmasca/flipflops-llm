"""
RAG (Retrieval Augmented Generation) service for answering student questions.
"""
from typing import List, Dict, Any, Optional

from src.entities.query import Query
from src.entities.conversation import Conversation


class RAGService:
    """
    Handles retrieval and generation of answers based on student questions
    and available documents.
    """
    
    def __init__(self, vector_store, llm_service, conversation_repository):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.conversation_repository = conversation_repository
    
    def answer_question(
        self, 
        query_text: str, 
        conversation_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG approach.
        
        Args:
            query_text: The question text
            conversation_id: Optional ID of an ongoing conversation
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dict containing answer and relevant context
        """
        # Get or create conversation
        conversation = None
        if conversation_id:
            conversation = self.conversation_repository.get_by_id(conversation_id)
        
        # Create query object
        query = Query.from_text(query_text, conversation_id)
        
        # Retrieve relevant documents
        relevant_docs = self.vector_store.similarity_search(query_text, k=top_k)
        
        # Prepare context from relevant documents
        context = self._prepare_context(relevant_docs)
        
        # Generate answer using LLM
        answer = self.llm_service.generate_answer(query_text, context, conversation)
        
        # Update conversation if it exists
        if conversation:
            conversation.add_message("user", query_text)
            conversation.add_message("assistant", answer)
            self.conversation_repository.save(conversation)
        
        return {
            "answer": answer,
            "relevant_docs": [doc.metadata for doc in relevant_docs],
            "conversation_id": conversation.id if conversation else None
        }
    
    def _prepare_context(self, documents: List[Any]) -> str:
        """Prepare context from retrieved documents."""
        context_parts = []
        
        for doc in documents:
            context_parts.append(f"Document: {doc.metadata.get('name', 'Unknown')}")
            context_parts.append(f"Content: {doc.page_content}")
            context_parts.append("---")
        
        return "\n".join(context_parts) 
