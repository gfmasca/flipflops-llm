"""
Protocol component for the MCP pattern.

The Protocol defines interaction patterns for different question types,
ensuring consistent handling of user requests.
"""
import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Tuple

from src.mcp.model import FlipflopsModel
from src.mcp.context import FlipflopsContext
from src.entities.question import Question

# Configure logger
logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Enumeration of request types supported by the protocol."""
    
    GENERAL_QUESTION = "general_question"
    EXPLANATION = "explanation"
    GENERATE_EXAM = "generate_exam"
    GRADE_EXAM = "grade_exam"
    GET_TOPICS = "get_topics"
    CLEAR_HISTORY = "clear_history"
    UNKNOWN = "unknown"


class FlipflopsProtocol:
    """
    Protocol component that defines interaction patterns.
    
    Responsibilities:
    - Define interaction patterns for different request types
    - Handle the flow of data between Model and Context
    - Ensure consistent processing of requests
    - Update Context based on request type and model output
    """
    
    def __init__(self, model: FlipflopsModel, context: FlipflopsContext):
        """
        Initialize the protocol with required components.
        
        Args:
            model: The model component for domain logic
            context: The context component for state management
        """
        self._model = model
        self._context = context
        
        # Define handlers for different request types
        self._handlers = {
            RequestType.GENERAL_QUESTION: self._handle_general_question,
            RequestType.EXPLANATION: self._handle_explanation,
            RequestType.GENERATE_EXAM: self._handle_generate_exam,
            RequestType.GRADE_EXAM: self._handle_grade_exam,
            RequestType.GET_TOPICS: self._handle_get_topics,
            RequestType.CLEAR_HISTORY: self._handle_clear_history,
        }
    
    def process_request(
        self, request_type: RequestType, **kwargs
    ) -> Dict[str, Any]:
        """
        Process a request according to its type.
        
        Args:
            request_type: The type of request to process
            **kwargs: Request parameters
            
        Returns:
            A dictionary with the response data
        """
        logger.info(f"Processing request of type: {request_type.value}")
        
        # Get the appropriate handler for this request type
        handler = self._handlers.get(request_type, self._handle_unknown)
        
        # Process the request and get the response
        response = handler(**kwargs)
        
        # Update the FLIPFLOP.md file after processing
        self._context.update_flipflop_file()
        
        return response
    
    def _handle_general_question(self, question: str, **kwargs) -> Dict[str, Any]:
        """
        Handle a general knowledge question.
        
        Args:
            question: The question to answer
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with answer
        """
        # Add the question to the conversation history
        self._context.add_user_message(question)
        
        # Get the current state for context-aware processing
        state = self._context.get_current_state()
        
        # Process the question using the model
        answer = self._model.answer_question(question, state)
        
        # Add the answer to the conversation history
        self._context.add_system_message(answer)
        
        return {
            "type": RequestType.GENERAL_QUESTION.value,
            "question": question,
            "answer": answer,
            "success": True
        }
    
    def _handle_explanation(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Handle a request for concept explanation.
        
        Args:
            concept: The concept to explain
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with explanation
        """
        # Add the explanation request to the conversation history
        self._context.add_user_message(f"Explique {concept}")
        
        # Get the current state for context-aware processing
        state = self._context.get_current_state()
        
        # Add this concept to previous topics
        self._context.add_previous_topic(concept)
        
        # Process the explanation using the model
        explanation = self._model.explain_concept(concept, state)
        
        # Add the explanation to the conversation history
        self._context.add_system_message(explanation)
        
        return {
            "type": RequestType.EXPLANATION.value,
            "concept": concept,
            "explanation": explanation,
            "success": True
        }
    
    def _handle_generate_exam(
        self, topic: str, num_questions: int = 5, **kwargs
    ) -> Dict[str, Any]:
        """
        Handle a request to generate an exam.
        
        Args:
            topic: The topic for the exam
            num_questions: The number of questions to generate
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with questions
        """
        # Add the exam generation request to the conversation history
        request_message = f"Gerando prova sobre {topic} com {num_questions} questões."
        self._context.add_user_message(request_message)
        
        # Get the current state for context-aware processing
        state = self._context.get_current_state()
        
        # Add this topic to previous topics
        self._context.add_previous_topic(topic)
        
        # Generate the exam using the model
        questions = self._model.generate_exam(topic, num_questions, state)
        
        # Add a summary to the conversation history
        summary = f"Prova gerada com {len(questions)} questões sobre {topic}."
        self._context.add_system_message(summary)
        
        # Convert questions to serializable format
        serialized_questions = [
            {
                "id": q.id,
                "text": q.text,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "topic": q.topic
            }
            for q in questions
        ]
        
        return {
            "type": RequestType.GENERATE_EXAM.value,
            "topic": topic,
            "num_questions": len(questions),
            "questions": serialized_questions,
            "success": True
        }
    
    def _handle_grade_exam(
        self, answers: List[str], questions: List[Question], **kwargs
    ) -> Dict[str, Any]:
        """
        Handle a request to grade an exam.
        
        Args:
            answers: List of user answers (a, b, c, d, e)
            questions: List of Question objects
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with score
        """
        # Get the current state for context-aware processing
        state = self._context.get_current_state()
        
        # Grade the exam using the model
        score = self._model.grade_exam(answers, questions, state)
        
        # Extract the topic if available
        topic = questions[0].topic if questions else "unknown"
        
        # Update user performance in the context
        self._context.update_user_performance(topic, score)
        
        # Add the result to the conversation history
        correct_count = int(score * len(questions))
        total = len(questions)
        percentage = score * 100
        result_message = (
            f"Resultado da prova de {topic}: "
            f"{correct_count}/{total} ({percentage:.1f}%)"
        )
        self._context.add_system_message(result_message)
        
        return {
            "type": RequestType.GRADE_EXAM.value,
            "topic": topic,
            "score": score,
            "correct_count": correct_count,
            "total_questions": total,
            "success": True
        }
    
    def _handle_get_topics(self, **kwargs) -> Dict[str, Any]:
        """
        Handle a request to get available topics.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with topics
        """
        # Get the current state for context-aware processing
        state = self._context.get_current_state()
        
        # Get the topics using the model
        topics = self._model.get_exam_topics(state)
        
        return {
            "type": RequestType.GET_TOPICS.value,
            "topics": topics,
            "success": True
        }
    
    def _handle_clear_history(self, **kwargs) -> Dict[str, Any]:
        """
        Handle a request to clear conversation history.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with success status
        """
        # Clear the conversation history
        success = self._context.clear_conversation()
        
        return {
            "type": RequestType.CLEAR_HISTORY.value,
            "success": success
        }
    
    def _handle_unknown(self, **kwargs) -> Dict[str, Any]:
        """
        Handle an unknown request type.
        
        Args:
            **kwargs: Request parameters
            
        Returns:
            Error response dictionary
        """
        logger.warning(f"Unknown request type with params: {kwargs}")
        
        return {
            "type": RequestType.UNKNOWN.value,
            "error": "Tipo de requisição desconhecido",
            "success": False
        } 
