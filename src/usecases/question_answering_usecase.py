"""
Question answering use case implementation.

This module provides the implementation for handling question answering,
coordinating between query processing, response generation and conversation management.
"""

import logging
from typing import Dict, Any

from src.usecases.query_processing_usecase import QueryProcessingUseCase
from src.usecases.response_generation_usecase import ResponseGenerationUseCase
from src.usecases.conversation_management_usecase import ConversationManagementUseCase

logger = logging.getLogger(__name__)

class QuestionAnsweringUseCase:
    """Coordinates the question answering process."""
    
    def __init__(
        self,
        query_processing: QueryProcessingUseCase,
        response_generation: ResponseGenerationUseCase,
        conversation_management: ConversationManagementUseCase
    ):
        """
        Initialize the use case.
        
        Args:
            query_processing: For processing and finding relevant content
            response_generation: For generating responses
            conversation_management: For managing conversation state
        """
        self.query_processing = query_processing
        self.response_generation = response_generation
        self.conversation_management = conversation_management
    
    async def answer_question(self, question: str, conversation_id: str) -> Dict[str, Any]:
        """
        Process a question and generate an answer.
        
        Args:
            question: The user's question
            conversation_id: ID of the current conversation
            
        Returns:
            Dictionary containing the answer and metadata
        """
        logger.info(f"Processing question for conversation {conversation_id}")
        
        # Process query to find relevant content
        context = await self.query_processing.process_query(question)
        
        # Generate response using context
        response = await self.response_generation.generate_response(question, context)
        
        # Update conversation state
        await self.conversation_management.add_interaction(
            conversation_id=conversation_id,
            question=question,
            answer=response["content"],
            context=context
        )
        
        return {
            "content": response["content"],
            "context": context,
            "conversation_id": conversation_id
        } 
