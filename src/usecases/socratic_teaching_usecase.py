"""
Implementation of the Socratic teaching use case.
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


class SocraticTeachingUseCase(QuestionAnsweringService):
    """
    Implementation of the Socratic teaching use case.
    
    This class processes requests for concept explanations using
    a Socratic questioning approach to encourage critical thinking.
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
        Initialize the Socratic teaching use case.
        
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
        
        logger.info("Initialized Socratic teaching use case")
    
    def explain_as_teacher(self, concept: str, conversation_id: str) -> str:
        """
        Explain a concept using Socratic teaching methods.
        
        Args:
            concept: The concept to explain
            conversation_id: ID of the current conversation
            
        Returns:
            Socratic explanation of the concept
        """
        logger.info(f"Processing Socratic explanation request: {concept}")
        
        try:
            # Process the query to identify the concept fully
            processed_query = self.query_service.process_query(concept)
            
            # Get conversation for context
            conversation = self._get_conversation(conversation_id)
            
            # Retrieve relevant documents
            relevant_docs = self._retrieve_relevant_documents(
                processed_query.query_text
            )
            
            # Prepare explanation based on available information
            if not relevant_docs:
                logger.warning(
                    f"No relevant documents found for concept: {concept}"
                )
                # Generate explanation without specific context
                explanation = self._generate_explanation_without_context(
                    processed_query.query_text,
                    conversation_id
                )
            else:
                # Prepare context from relevant documents
                context = self._prepare_context_from_documents(relevant_docs)
                
                # Generate explanation with context
                explanation = self._generate_explanation_with_context(
                    processed_query.query_text,
                    context,
                    conversation_id
                )
            
            # Add conversation messages if a conversation exists
            if conversation:
                self.conversation_management.add_user_message(
                    f"Explique o conceito: {concept}", 
                    {"processed_concept": processed_query.query_text}
                )
                self.conversation_management.add_assistant_message(
                    explanation,
                    {"explanation_type": "socratic"}
                )
            
            logger.info(f"Generated Socratic explanation for: {concept}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating Socratic explanation: {str(e)}")
            return (
                "Desculpe, tive um problema ao elaborar a explicação. "
                "Por favor, tente novamente mais tarde."
            )
    
    def answer_general_question(
        self, query_text: str, conversation_id: str
    ) -> str:
        """
        Answer a general knowledge question.
        
        This method is implemented in the GeneralKnowledgeUseCase class.
        This implementation returns a message directing to use that service.
        
        Args:
            query_text: The question to answer
            conversation_id: ID of the current conversation
            
        Returns:
            Message directing to use the GeneralKnowledgeUseCase
        """
        logger.info(
            f"Received general question in SocraticTeachingUseCase: "
            f"{query_text}"
        )
        return (
            "Para respostas a perguntas gerais, por favor utilize o "
            "serviço GeneralKnowledgeUseCase específico para essa finalidade."
        )
    
    def _get_conversation(self, conversation_id: str) -> Optional[Any]:
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
    
    def _retrieve_relevant_documents(self, concept: str) -> List[Document]:
        """
        Retrieve documents relevant to the concept.
        
        Args:
            concept: The processed concept text
            
        Returns:
            List of relevant documents
        """
        try:
            # Generate embedding for the concept
            concept_embedding = self.embedding_service.create_embedding(
                concept
            )
            
            # Search for similar documents
            docs = self.query_service.retrieve_relevant_documents(
                concept, 
                concept_embedding,
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
    
    def _generate_explanation_with_context(
        self, concept: str, context: str, conversation_id: str
    ) -> str:
        """
        Generate a Socratic explanation using context from documents.
        
        Args:
            concept: The processed concept
            context: The context from relevant documents
            conversation_id: ID of the current conversation
            
        Returns:
            Generated explanation using Socratic method
        """
        # Prepare prompt with Socratic approach
        prompt = (
            "Você é um tutor especializado no método socrático, ajudando "
            "estudantes brasileiros do ensino médio a compreenderem conceitos "
            "através de questionamentos que estimulam o pensamento crítico.\n\n"
            "Conceito a ser explicado:\n"
            f"{concept}\n\n"
            "Contexto informativo sobre o conceito:\n"
            f"{context}\n\n"
            "Elabore uma explicação utilizando o método socrático, seguindo "
            "estas diretrizes:\n"
            "1. Comece com uma breve introdução ao conceito\n"
            "2. Faça perguntas que guiem o estudante a descobrir o "
            "conhecimento por si mesmo\n"
            "3. Apresente exemplos relacionados à realidade brasileira e "
            "relevantes para o vestibular FUVEST\n"
            "4. Desenvolva um raciocínio passo a passo\n"
            "5. Conclua conectando o conceito a aplicações práticas\n\n"
            "Use linguagem clara e adequada para estudantes do ensino médio "
            "brasileiro. Seu objetivo é estimular o pensamento crítico, não "
            "apenas fornecer respostas prontas."
        )
        
        # Generate explanation
        explanation = self.llm_service.generate_text(prompt)
        
        return explanation
    
    def _generate_explanation_without_context(
        self, concept: str, conversation_id: str
    ) -> str:
        """
        Generate a Socratic explanation without specific document context.
        
        Args:
            concept: The processed concept
            conversation_id: ID of the current conversation
            
        Returns:
            Generated explanation using Socratic method
        """
        # Prepare prompt with Socratic approach but without specific context
        prompt = (
            "Você é um tutor especializado no método socrático, ajudando "
            "estudantes brasileiros do ensino médio a compreenderem conceitos "
            "através de questionamentos que estimulam o pensamento crítico.\n\n"
            "Um estudante pediu para você explicar o seguinte conceito, mas "
            "não temos documentos específicos em nossa base de "
            "conhecimento sobre este tema:\n\n"
            f"{concept}\n\n"
            "Elabore uma explicação utilizando o método socrático, seguindo "
            "estas diretrizes:\n"
            "1. Comece com uma breve introdução ao conceito\n"
            "2. Faça perguntas que guiem o estudante a descobrir o "
            "conhecimento por si mesmo\n"
            "3. Apresente exemplos relacionados à realidade brasileira e "
            "relevantes para o vestibular FUVEST\n"
            "4. Desenvolva um raciocínio passo a passo\n"
            "5. Conclua conectando o conceito a aplicações práticas\n\n"
            "Use linguagem clara e adequada para estudantes do ensino médio "
            "brasileiro. Seu objetivo é estimular o pensamento crítico, não "
            "apenas fornecer respostas prontas. "
            "Indique que esta explicação é baseada em conhecimento geral, "
            "não em documentos específicos da nossa base."
        )
        
        # Generate explanation
        explanation = self.llm_service.generate_text(prompt)
        
        return explanation 
