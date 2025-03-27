"""
Implementation of the general knowledge question answering use case.
"""
import logging
from typing import List, Optional, Any

from src.entities.document import Document
from src.interfaces.services.llm_service import LLMService
from src.interfaces.services.query_service import QueryService
from src.interfaces.services.embedding_service import EmbeddingService
from src.interfaces.services.question_answering_service import (
    QuestionAnsweringService
)
from src.interfaces.repositories.document_repository import (
    DocumentRepository
)
from src.usecases.conversation_management_usecase import (
    ConversationManagementUseCase
)


# Configure logger
logger = logging.getLogger(__name__)


class GeneralKnowledgeUseCase(QuestionAnsweringService):
    """
    Implementation of the general knowledge question answering use case.
    
    This class processes general knowledge questions and generates comprehensive
    answers using context from the document repository and LLM services.
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        query_service: QueryService,
        embedding_service: EmbeddingService,
        document_repository: DocumentRepository,
        conversation_management: ConversationManagementUseCase,
        max_context_docs: int = 5,
        min_similarity_score: float = 0.7
    ):
        """
        Initialize the general knowledge question answering use case.
        
        Args:
            llm_service: Service for generating text using LLMs
            query_service: Service for processing and retrieving relevant docs
            embedding_service: Service for generating and comparing embeddings
            document_repository: Repository for accessing documents
            conversation_management: Service for managing conversation context
            max_context_docs: Maximum number of documents to include in context
            min_similarity_score: Minimum similarity score for relevant docs
        """
        self.llm_service = llm_service
        self.query_service = query_service
        self.embedding_service = embedding_service
        self.document_repository = document_repository
        self.conversation_management = conversation_management
        self.max_context_docs = max_context_docs
        self.min_similarity_score = min_similarity_score
        
        logger.info("Initialized general knowledge question answering use case")
    
    def answer_general_question(
        self, query_text: str, conversation_id: str
    ) -> str:
        """
        Answer a general knowledge question.
        
        Args:
            query_text: The question to answer
            conversation_id: ID of the current conversation
            
        Returns:
            Answer to the question with citations when appropriate
        """
        logger.info(f"Processing general knowledge question: {query_text}")
        
        try:
            # Process the query
            processed_query = self.query_service.process_query(query_text)
            
            # Get conversation for context
            conversation = self._get_conversation(conversation_id)
            
            # Retrieve relevant documents
            relevant_docs = self._retrieve_relevant_documents(
                processed_query.query_text
            )
            
            if not relevant_docs:
                logger.warning(
                    f"No relevant documents found for query: {query_text}"
                )
                # Generate answer without context
                answer = self._generate_answer_without_context(
                    processed_query.query_text, 
                    conversation_id
                )
                
                # Add message to conversation
                if conversation:
                    self.conversation_management.add_user_message(
                        query_text, 
                        {"processed_query": processed_query.query_text}
                    )
                    self.conversation_management.add_assistant_message(
                        answer, 
                        {"source": "no_context"}
                    )
                
                return answer
            
            # Prepare context from relevant documents
            context = self._prepare_context_from_documents(relevant_docs)
            
            # Generate answer
            answer = self._generate_answer_with_context(
                processed_query.query_text,
                context,
                conversation_id
            )
            
            # Add citations if appropriate
            answer_with_citations = self._add_citations(answer, relevant_docs)
            
            # Add message to conversation
            if conversation:
                self.conversation_management.add_user_message(
                    query_text, 
                    {"processed_query": processed_query.query_text}
                )
                sources = [
                    doc.metadata.get("title", "Desconhecido")
                    for doc in relevant_docs
                ]
                self.conversation_management.add_assistant_message(
                    answer_with_citations, 
                    {"sources": sources}
                )
            
            logger.info(f"Generated answer for query: {query_text}")
            return answer_with_citations
        
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return (
                "Desculpe, tive um problema ao processar sua pergunta. "
                "Por favor, tente novamente mais tarde."
            )
    
    def explain_as_teacher(self, concept: str, conversation_id: str) -> str:
        """
        Explain a concept using Socratic teaching methods.
        
        This method is implemented in the SocraticTeachingUseCase class.
        This implementation returns a message directing to use that service.
        
        Args:
            concept: The concept to explain
            conversation_id: ID of the current conversation
            
        Returns:
            Message directing to use the SocraticTeachingUseCase
        """
        logger.info(
            f"Received request to explain concept in GeneralKnowledgeUseCase: "
            f"{concept}"
        )
        return (
            "Para explicações com abordagem socrática, por favor utilize o "
            "serviço SocraticTeachingUseCase específico para essa finalidade."
        )
    
    def _get_conversation(
        self, conversation_id: str
    ) -> Optional[Any]:
        """
        Get the conversation for context.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation object or None if not found/invalid
        """
        if not conversation_id:
            return None
            
        try:
            return self.conversation_management.get_conversation_by_id(
                conversation_id
            )
        except Exception as e:
            logger.warning(
                f"Error retrieving conversation {conversation_id}: {str(e)}"
            )
            return None
    
    def _retrieve_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve documents relevant to the query.
        
        Args:
            query: The processed query text
            
        Returns:
            List of relevant documents
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.create_embedding(query)
            
            # Search for similar documents
            docs = self.query_service.retrieve_relevant_documents(
                query, 
                query_embedding,
                max_results=self.max_context_docs,
                min_score=self.min_similarity_score
            )
            
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def _prepare_context_from_documents(
        self, documents: List[Document]
    ) -> str:
        """
        Prepare context text from relevant documents.
        
        Args:
            documents: List of relevant documents
            
        Returns:
            Formatted context text
        """
        context_parts = []
        
        for i, doc in enumerate(documents):
            # Extract title or use a placeholder
            title = doc.metadata.get("title", f"Documento {i+1}")
            
            # Extract and format content
            content = doc.content
            if len(content) > 1000:
                # Truncate long content
                content = content[:1000] + "..."
            
            # Format as a section
            section = f"--- {title} ---\n{content}\n"
            context_parts.append(section)
        
        return "\n".join(context_parts)
    
    def _generate_answer_with_context(
        self, query: str, context: str, conversation_id: str
    ) -> str:
        """
        Generate an answer using the query and context.
        
        Args:
            query: The processed query text
            context: The context from relevant documents
            conversation_id: ID of the current conversation
            
        Returns:
            Generated answer
        """
        # Prepare prompt with context
        prompt = (
            "Você é um assistente educacional especializado em ajudar "
            "estudantes brasileiros do ensino médio. "
            "Sua tarefa é responder à pergunta do estudante com base "
            "no contexto fornecido.\n\n"
            "Contexto:\n"
            f"{context}\n\n"
            "Pergunta do estudante:\n"
            f"{query}\n\n"
            "Responda de forma clara, precisa e educativa. Use linguagem "
            "adequada para estudantes do ensino médio. Se a resposta não "
            "estiver contida no contexto fornecido, diga que não tem "
            "informações suficientes para responder."
        )
        
        # Generate answer
        answer = self.llm_service.generate_text(prompt)
        
        return answer
    
    def _generate_answer_without_context(
        self, query: str, conversation_id: str
    ) -> str:
        """
        Generate an answer when no relevant documents are found.
        
        Args:
            query: The processed query text
            conversation_id: ID of the current conversation
            
        Returns:
            Generated answer
        """
        # Prepare prompt for no context
        prompt = (
            "Você é um assistente educacional especializado em ajudar "
            "estudantes brasileiros do ensino médio. "
            "Um estudante fez a seguinte pergunta, mas não temos documentos "
            "específicos em nossa base de conhecimento sobre esse tema.\n\n"
            "Pergunta do estudante:\n"
            f"{query}\n\n"
            "Forneça uma resposta útil, educativa e abrangente, adequada para "
            "um estudante do ensino médio brasileiro. Seja claro e preciso, "
            "e indique que esta resposta é baseada em conhecimento geral, "
            "não em documentos específicos da nossa base."
        )
        
        # Generate answer
        answer = self.llm_service.generate_text(prompt)
        
        return answer
    
    def _add_citations(
        self, answer: str, documents: List[Document]
    ) -> str:
        """
        Add citations to the answer when appropriate.
        
        Args:
            answer: The generated answer
            documents: List of documents used for context
            
        Returns:
            Answer with citations appended
        """
        if not documents:
            return answer
        
        # Prepare citations section
        citations = []
        for i, doc in enumerate(documents):
            title = doc.metadata.get("title", f"Documento {i+1}")
            author = doc.metadata.get("author", "Autor desconhecido")
            date = doc.metadata.get("date", "Data desconhecida")
            
            citation = f"{i+1}. {title} - {author}, {date}"
            citations.append(citation)
        
        # Append citations section
        answer_with_citations = (
            f"{answer}\n\n"
            "Fontes consultadas:\n"
            f"{chr(10).join(citations)}"
        )
        
        return answer_with_citations 
