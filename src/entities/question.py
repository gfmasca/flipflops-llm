"""
Entity representing a multiple-choice question.
"""
from typing import List, Dict, Any, Optional
import uuid


class Question:
    """
    Entity representing a multiple-choice question.
    
    A question contains the question text, a list of options (choices),
    the correct answer, an explanation, and the topic it belongs to.
    """
    
    def __init__(
        self,
        text: str,
        options: List[str],
        correct_answer: str,
        explanation: str,
        topic: str,
        id: Optional[str] = None
    ):
        """
        Initialize a Question.
        
        Args:
            text: The question text
            options: List of multiple-choice options (a through e)
            correct_answer: The letter of the correct option (a-e)
            explanation: Explanation of the correct answer
            topic: The topic this question is related to
            id: Optional ID (generated if not provided)
        """
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.options = options
        self.correct_answer = correct_answer.lower()  # Ensure lowercase
        self.explanation = explanation
        self.topic = topic
        
        # Validate correct answer is in range
        valid_answers = ['a', 'b', 'c', 'd', 'e']
        if self.correct_answer not in valid_answers:
            err = f"Correct answer must be one of {valid_answers}"
            err += f", got: {correct_answer}"
            raise ValueError(err)
        
        # Validate number of options
        if len(options) != 5:
            raise ValueError(
                f"Must provide exactly 5 options (a-e), got {len(options)}"
            )
    
    def get_id(self) -> str:
        """Get the question ID."""
        return self.id
    
    def get_text(self) -> str:
        """Get the question text."""
        return self.text
    
    def get_options(self) -> List[str]:
        """Get the list of options."""
        return self.options
    
    def get_correct_answer(self) -> str:
        """Get the correct answer letter (a-e)."""
        return self.correct_answer
    
    def get_explanation(self) -> str:
        """Get the explanation for the correct answer."""
        return self.explanation
    
    def get_topic(self) -> str:
        """Get the topic of the question."""
        return self.topic
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the question to a dictionary.
        
        Returns:
            Dictionary representation of the question
        """
        return {
            "id": self.id,
            "text": self.text,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "topic": self.topic
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """
        Create a Question from a dictionary.
        
        Args:
            data: Dictionary containing question data
            
        Returns:
            A new Question instance
        """
        return cls(
            id=data.get("id"),
            text=data["text"],
            options=data["options"],
            correct_answer=data["correct_answer"],
            explanation=data["explanation"],
            topic=data["topic"]
        )
    
    def format_for_display(self) -> str:
        """
        Format the question for display in a CLI.
        
        Returns:
            Formatted question text with options
        """
        option_letters = ['a', 'b', 'c', 'd', 'e']
        options_text = "\n".join(
            f"({letter}) {option}" 
            for letter, option in zip(option_letters, self.options)
        )
        
        return f"{self.text}\n\n{options_text}"
    
    def __str__(self) -> str:
        """String representation of the question."""
        return f"Question(id={self.id}, topic={self.topic})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the question."""
        return (
            f"Question(id={self.id}, topic={self.topic}, "
            f"correct_answer={self.correct_answer})"
        ) 
