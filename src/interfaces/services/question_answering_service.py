"""
Interface for question answering services.
"""
from abc import ABC, abstractmethod


class QuestionAnsweringService(ABC):
    """
    Interface for services that answer questions and provide explanations.
    """

    @abstractmethod
    def answer_general_question(
        self, query_text: str, conversation_id: str
    ) -> str:
        """
        Answer a general knowledge question.
        
        Args:
            query_text: The question to answer
            conversation_id: ID of the current conversation
            
        Returns:
            Answer to the question
        """
        pass
    
    @abstractmethod
    def explain_as_teacher(self, concept: str, conversation_id: str) -> str:
        """
        Explain a concept using Socratic teaching methods.
        
        Args:
            concept: The concept to explain
            conversation_id: ID of the current conversation
            
        Returns:
            Socratic explanation of the concept
        """
        pass 
