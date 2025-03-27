"""
Route component for the MCP pattern.

The Route handles the routing of requests between different components,
ensuring the correct flow of data and control.
"""
import logging
from typing import Dict, Any, List

from src.mcp.model import FlipflopsModel
from src.mcp.context import FlipflopsContext
from src.mcp.protocol import FlipflopsProtocol, RequestType
from src.entities.question import Question

# Configure logger
logger = logging.getLogger(__name__)


class FlipflopsRoute:
    """
    Route component that handles routing between MCP components.
    
    Responsibilities:
    - Route requests to the appropriate protocol handlers
    - Convert between different data formats as needed
    - Provide a unified interface for controllers
    """
    
    def __init__(
        self, model: FlipflopsModel, context: FlipflopsContext, protocol: FlipflopsProtocol
    ):
        """
        Initialize the route with required components.
        
        Args:
            model: The model component for domain logic
            context: The context component for state management
            protocol: The protocol component for interaction patterns
        """
        self._model = model
        self._context = context
        self._protocol = protocol
    
    def answer_question(self, question: str) -> str:
        """
        Process a general knowledge question and return the answer.
        
        Args:
            question: The question to answer
            
        Returns:
            The answer to the question
        """
        logger.info(f"Route handling question: {question}")
        
        # Process the request through the protocol
        response = self._protocol.process_request(
            RequestType.GENERAL_QUESTION, question=question
        )
        
        # Check if the request was successful
        if response["success"]:
            return response["answer"]
        else:
            error_msg = response.get("error", "Erro ao processar a pergunta")
            logger.error(f"Error processing question: {error_msg}")
            return f"Não foi possível responder à pergunta. {error_msg}"
    
    def explain_concept(self, concept: str) -> str:
        """
        Generate a Socratic explanation for a concept.
        
        Args:
            concept: The concept to explain
            
        Returns:
            The explanation of the concept
        """
        logger.info(f"Route handling explanation request for: {concept}")
        
        # Process the request through the protocol
        response = self._protocol.process_request(
            RequestType.EXPLANATION, concept=concept
        )
        
        # Check if the request was successful
        if response["success"]:
            return response["explanation"]
        else:
            error_msg = response.get("error", "Erro ao gerar explicação")
            logger.error(f"Error generating explanation: {error_msg}")
            return f"Não foi possível explicar o conceito. {error_msg}"
    
    def generate_exam(self, topic: str, num_questions: int = 5) -> List[Question]:
        """
        Generate an exam with multiple-choice questions.
        
        Args:
            topic: The topic for the exam
            num_questions: The number of questions to generate
            
        Returns:
            A list of Question objects
        """
        logger.info(f"Route handling exam generation for topic: {topic}")
        
        # Process the request through the protocol
        response = self._protocol.process_request(
            RequestType.GENERATE_EXAM, topic=topic, num_questions=num_questions
        )
        
        # Check if the request was successful
        if response["success"]:
            # Convert serialized questions back to Question objects
            questions = []
            for q_data in response["questions"]:
                question = Question(
                    id=q_data["id"],
                    text=q_data["text"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    topic=q_data["topic"]
                )
                questions.append(question)
            return questions
        else:
            logger.error(f"Error generating exam: {response.get('error')}")
            return []
    
    def grade_exam(self, answers: List[str], questions: List[Question]) -> float:
        """
        Grade an exam based on user answers.
        
        Args:
            answers: List of user answers (a, b, c, d, e)
            questions: List of Question objects
            
        Returns:
            Score as a percentage (0.0 to 1.0)
        """
        logger.info("Route handling exam grading")
        
        # Process the request through the protocol
        response = self._protocol.process_request(
            RequestType.GRADE_EXAM, answers=answers, questions=questions
        )
        
        # Check if the request was successful
        if response["success"]:
            return response["score"]
        else:
            logger.error(f"Error grading exam: {response.get('error')}")
            return 0.0
    
    def get_exam_topics(self) -> List[str]:
        """
        Get a list of available topics for exam generation.
        
        Returns:
            A list of topic strings
        """
        logger.info("Route handling request for exam topics")
        
        # Process the request through the protocol
        response = self._protocol.process_request(RequestType.GET_TOPICS)
        
        # Check if the request was successful
        if response["success"]:
            return response["topics"]
        else:
            logger.error(f"Error getting topics: {response.get('error')}")
            return []
    
    def clear_conversation_history(self) -> bool:
        """
        Clear the conversation history.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Route handling request to clear conversation history")
        
        # Process the request through the protocol
        response = self._protocol.process_request(RequestType.CLEAR_HISTORY)
        
        return response["success"] 
