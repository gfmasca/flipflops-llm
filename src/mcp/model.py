"""
Model component for the MCP pattern.

The Model encapsulates the core domain logic of the application.
It delegates to use cases while remaining agnostic to infrastructure details.
"""
import logging
from typing import List, Dict, Any, Optional

from src.entities.question import Question
from src.usecases.question_answering_usecase import QuestionAnsweringUseCase
from src.usecases.exam_generation_usecase import ExamGenerationUseCase
from src.usecases.conversation_management_usecase import ConversationManagementUseCase

# Configure logger
logger = logging.getLogger(__name__)


class FlipflopsModel:
    """
    Model component that encapsulates core domain logic.
    
    Responsibilities:
    - Process user inputs and generate appropriate responses
    - Delegate complex tasks to specialized use cases
    - Remain isolated from infrastructure concerns
    """
    
    def __init__(
        self,
        question_answering_usecase: QuestionAnsweringUseCase,
        exam_generation_usecase: ExamGenerationUseCase,
        conversation_management_usecase: ConversationManagementUseCase,
    ):
        """
        Initialize the model with required use cases.
        
        Args:
            question_answering_usecase: For answering general questions
            exam_generation_usecase: For generating and grading exams
            conversation_management_usecase: For managing conversation state
        """
        self._question_answering = question_answering_usecase
        self._exam_generation = exam_generation_usecase
        self._conversation_management = conversation_management_usecase
    
    def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """
        Answer a general knowledge question.
        
        Args:
            question: The question to answer
            context: The current conversation context
            
        Returns:
            The answer to the question
        """
        logger.info(f"Model processing question: {question}")
        
        # Use context to enhance answer if relevant
        related_topics = context.get("related_topics", [])
        if related_topics:
            logger.info(f"Found related topics in context: {related_topics}")
        
        # Delegate to question answering use case
        return self._question_answering.answer_question(question)
    
    def explain_concept(self, concept: str, context: Dict[str, Any]) -> str:
        """
        Generate a Socratic explanation for a concept.
        
        Args:
            concept: The concept to explain
            context: The current conversation context
            
        Returns:
            The explanation of the concept
        """
        logger.info(f"Model generating explanation for: {concept}")
        
        # Use context to enhance explanation if available
        user_level = context.get("user_level", "high_school")
        previous_topics = context.get("previous_topics", [])
        
        if previous_topics:
            logger.info(f"Using previous topics from context: {previous_topics}")
        
        # Delegate to question answering use case
        return self._question_answering.explain_concept(concept)
    
    def generate_exam(
        self, topic: str, num_questions: int, context: Dict[str, Any]
    ) -> List[Question]:
        """
        Generate an exam with multiple-choice questions.
        
        Args:
            topic: The topic for the exam
            num_questions: The number of questions to generate
            context: The current conversation context
            
        Returns:
            A list of Question objects
        """
        logger.info(f"Model generating exam on: {topic} with {num_questions} questions")
        
        # Use context to enhance exam generation
        previous_topics = context.get("previous_topics", [])
        user_performance = context.get("user_performance", {})
        
        if topic in user_performance:
            logger.info(f"User has previous performance on topic: {topic}")
        
        # Delegate to exam generation use case
        return self._exam_generation.generate_exam(topic, num_questions)
    
    def grade_exam(
        self, answers: List[str], questions: List[Question], context: Dict[str, Any]
    ) -> float:
        """
        Grade an exam based on user answers.
        
        Args:
            answers: List of user answers (a, b, c, d, e)
            questions: List of Question objects
            context: The current conversation context
            
        Returns:
            Score as a percentage (0.0 to 1.0)
        """
        logger.info("Model grading exam")
        
        # Calculate the score
        score = self._exam_generation.grade_exam(answers, questions)
        
        # Update context with performance data
        if questions and questions[0].topic:
            topic = questions[0].topic
            
            # Store performance data for this topic
            topic_performance = context.get("user_performance", {})
            if topic not in topic_performance:
                topic_performance[topic] = []
            
            # Add this score to performance history
            topic_performance[topic].append(score)
            
            logger.info(f"Updated user performance for topic: {topic}")
        
        return score
    
    def get_exam_topics(self, context: Dict[str, Any]) -> List[str]:
        """
        Get a list of available topics for exam generation.
        
        Args:
            context: The current conversation context
            
        Returns:
            A list of topic strings
        """
        logger.info("Model retrieving available exam topics")
        
        # Get the topics
        topics = self._exam_generation.get_exam_topics()
        
        # Update context with available topics
        context["available_topics"] = topics
        
        return topics 
