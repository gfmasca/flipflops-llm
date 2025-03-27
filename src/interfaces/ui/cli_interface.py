"""
Interface for command-line user interfaces.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class CLIInterface(ABC):
    """
    Interface for command-line user interfaces.
    
    This interface defines methods for displaying text, handling user input,
    and formatting different types of output for command-line interfaces.
    """
    
    @abstractmethod
    def display_welcome_message(self) -> None:
        """Display a welcome message to the user."""
        pass
    
    @abstractmethod
    def display_help(self) -> None:
        """Display help information showing available commands."""
        pass
    
    @abstractmethod
    def display_text(self, text: str) -> None:
        """
        Display text to the user.
        
        Args:
            text: The text to display
        """
        pass
    
    @abstractmethod
    def display_error(self, message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            message: The error message to display
        """
        pass
    
    @abstractmethod
    def display_success(self, message: str) -> None:
        """
        Display a success message to the user.
        
        Args:
            message: The success message to display
        """
        pass
    
    @abstractmethod
    def display_question(self, question_text: str, options: List[str]) -> None:
        """
        Display a multiple-choice question with options.
        
        Args:
            question_text: The question text
            options: The list of options (a through e)
        """
        pass
    
    @abstractmethod
    def display_exam_results(self, score: float, total_questions: int) -> None:
        """
        Display exam results to the user.
        
        Args:
            score: The score as a percentage (0.0 to 1.0)
            total_questions: The total number of questions
        """
        pass
    
    @abstractmethod
    def display_topics(self, topics: List[str]) -> None:
        """
        Display a list of available topics.
        
        Args:
            topics: The list of available topics
        """
        pass
    
    @abstractmethod
    def get_input(self, prompt: str = "> ") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: The prompt to display
            
        Returns:
            The user's input as a string
        """
        pass
    
    @abstractmethod
    def get_multiple_choice_answer(
        self, num_options: int = 5, prompt: str = "Sua resposta (a-e): "
    ) -> str:
        """
        Get a multiple-choice answer from the user.
        
        Args:
            num_options: The number of options (defaults to 5)
            prompt: The prompt to display
            
        Returns:
            The selected option letter (a-e)
        """
        pass
    
    @abstractmethod
    def get_yes_no_input(self, prompt: str = "Confirma? (s/n): ") -> bool:
        """
        Get a yes/no input from the user.
        
        Args:
            prompt: The prompt to display
            
        Returns:
            True if the user answered yes, False otherwise
        """
        pass
    
    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        pass
    
    @abstractmethod
    def start(self) -> None:
        """Start the CLI interface main loop."""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Exit the CLI interface."""
        pass 
