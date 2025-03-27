"""
Interface for exam generation and grading services.
"""
from abc import ABC, abstractmethod
from typing import List

from src.entities.question import Question


class ExamService(ABC):
    """
    Interface for services that generate and grade exams.
    """
    
    @abstractmethod
    def generate_exam(self, topic: str, num_questions: int) -> List[Question]:
        """
        Generate an exam with multiple-choice questions on a specified topic.
        
        Args:
            topic: The topic to generate questions about
            num_questions: The number of questions to generate
            
        Returns:
            A list of Question objects
        """
        pass
    
    @abstractmethod
    def grade_exam(
        self, answers: List[str], questions: List[Question]
    ) -> float:
        """
        Grade a completed exam.
        
        Args:
            answers: The answers provided by the student (a-e)
            questions: The questions in the exam
            
        Returns:
            The score as a percentage (0.0 to 1.0)
        """
        pass
    
    @abstractmethod
    def get_exam_topics(self) -> List[str]:
        """
        Get available topics for exams based on the document base.
        
        Returns:
            A list of topic strings
        """
        pass 
