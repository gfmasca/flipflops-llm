"""
Main controller for routing user inputs to appropriate use cases using the MCP pattern.
"""
import logging
from typing import List

from src.entities.question import Question
from src.mcp.route import FlipflopsRoute


# Configure logger
logger = logging.getLogger(__name__)


class MainController:
    """
    Main controller for the application that routes user inputs to the MCP components.
    
    Acts as a bridge between the UI and the MCP architecture.
    """
    
    def __init__(self, route: FlipflopsRoute):
        """
        Initialize the controller with the MCP route component.
        
        Args:
            route: The MCP route component
        """
        self.route = route
        logger.info("MainController initialized with MCP pattern")
    
    def answer_question(self, question: str) -> str:
        """
        Process a general knowledge question and return the answer.
        
        Args:
            question: The question to answer
            
        Returns:
            The answer to the question
        """
        try:
            logger.info(f"Controller processing question: {question}")
            return self.route.answer_question(question)
        except Exception as e:
            logger.exception("Error answering question", exc_info=e)
            raise
    
    def explain_concept(self, concept: str) -> str:
        """
        Generate a Socratic explanation for a concept.
        
        Args:
            concept: The concept to explain
            
        Returns:
            The explanation of the concept
        """
        try:
            logger.info(f"Controller generating explanation for: {concept}")
            return self.route.explain_concept(concept)
        except Exception as e:
            logger.exception("Error explaining concept", exc_info=e)
            raise
    
    def generate_exam(self, topic: str, num_questions: int = 5) -> List[Question]:
        """
        Generate an exam with multiple-choice questions on a topic.
        
        Args:
            topic: The topic for the exam
            num_questions: The number of questions to generate
            
        Returns:
            A list of Question objects
        """
        try:
            logger.info(f"Controller generating exam on topic: {topic}")
            return self.route.generate_exam(topic, num_questions)
        except Exception as e:
            logger.exception("Error generating exam", exc_info=e)
            raise
    
    def grade_exam(self, answers: List[str], questions: List[Question]) -> float:
        """
        Grade an exam based on user answers.
        
        Args:
            answers: List of user answers (a, b, c, d, e)
            questions: List of Question objects
            
        Returns:
            Score as a percentage (0.0 to 1.0)
        """
        try:
            logger.info("Controller grading exam")
            return self.route.grade_exam(answers, questions)
        except Exception as e:
            logger.exception("Error grading exam", exc_info=e)
            raise
    
    def get_exam_topics(self) -> List[str]:
        """
        Get a list of available topics for exam generation.
        
        Returns:
            A list of topic strings
        """
        try:
            logger.info("Controller retrieving available exam topics")
            return self.route.get_exam_topics()
        except Exception as e:
            logger.exception("Error getting exam topics", exc_info=e)
            raise
    
    def clear_conversation_history(self) -> bool:
        """
        Clear the conversation history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Controller clearing conversation history")
            return self.route.clear_conversation_history()
        except Exception as e:
            logger.exception("Error clearing conversation history", exc_info=e)
            raise 
