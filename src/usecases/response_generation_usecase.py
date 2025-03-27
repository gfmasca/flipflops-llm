"""
Implementation of LLM response generation using Claude.
"""
import os
import logging
from typing import List, Optional, Dict, Any

from src.entities.topic import Topic
from src.interfaces.services.llm_service import LLMService
from src.infrastructure.external.claude_client import ClaudeClient


# Configure logger
logger = logging.getLogger(__name__)


class ResponseGenerationUseCase(LLMService):
    """Implementation of LLM service using Claude."""
    
    # Template for system prompts in Portuguese
    SYSTEM_PROMPT_TEMPLATE = """
    Você é um assistente educacional especializado em fornecer explicações claras e didáticas.
    Suas respostas devem ser em português, com linguagem acessível e apropriada para estudantes.
    
    Ao responder:
    - Use exemplos práticos para ilustrar conceitos
    - Explique termos técnicos de forma simples
    - Mantenha um tom amigável e encorajador
    - Adapte a complexidade ao nível do aluno
    - Forneça informações precisas baseadas no contexto
    
    {additional_instructions}
    """
    
    # Question generation template
    QUESTION_TEMPLATE = """
    Crie uma pergunta educativa sobre o tópico: {topic_name}
    
    Descrição do tópico: {topic_description}
    
    Nível de dificuldade: {difficulty}
    
    A pergunta deve ser bem estruturada, estimular o pensamento crítico e testar 
    o conhecimento do aluno sobre este assunto específico.
    """
    
    # Concept explanation template
    EXPLANATION_TEMPLATE = """
    Explique o seguinte conceito: {concept}
    
    Forneça uma explicação {detail_level} com exemplos práticos.
    Use uma linguagem clara e didática, adequada para estudantes.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = ClaudeClient.CLAUDE_3_SONNET,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ):
        """
        Initialize the response generation use case.
        
        Args:
            api_key: Anthropic API key (defaults to env variable)
            model: Claude model to use
            max_tokens: Default maximum tokens for responses
            temperature: Default temperature for generation
        """
        # Initialize system prompt with default template
        self.system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            additional_instructions=""
        )
        
        # Initialize Claude client
        try:
            self.client = ClaudeClient(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=self.system_prompt
            )
            logger.info(f"Initialized response generation with model {model}")
        except ValueError as e:
            logger.error(f"Failed to initialize Claude client: {str(e)}")
            raise

    def generate_response(
        self, 
        prompt: str, 
        context: List[str] = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate a response from Claude using the provided prompt and context.
        
        Args:
            prompt: The main prompt to send to Claude
            context: List of context passages to include
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            The generated response text
            
        Raises:
            ValueError: If the prompt is invalid
            RuntimeError: If the Claude API call fails
        """
        try:
            logger.info("Generating response with Claude")
            
            # Use client to generate response
            response_text = self.client.generate_text(
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            logger.info("Successfully generated response")
            return response_text
            
        except ValueError as e:
            logger.error(f"Invalid input for response generation: {str(e)}")
            raise ValueError(f"Failed to generate response: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")

    def generate_question(
        self, 
        topic: Topic, 
        difficulty: str,
        additional_context: List[str] = None
    ) -> str:
        """
        Generate an educational question about the given topic.
        
        Args:
            topic: The topic to generate a question about
            difficulty: The difficulty level (e.g., "easy", "medium", "hard")
            additional_context: Additional context to include
            
        Returns:
            The generated question
            
        Raises:
            ValueError: If the topic or difficulty is invalid
            RuntimeError: If the Claude API call fails
        """
        # Validate inputs
        if not topic:
            raise ValueError("Topic is required")
        if not difficulty:
            raise ValueError("Difficulty level is required")
            
        # Map difficulty level to Portuguese
        difficulty_map = {
            "easy": "fácil",
            "medium": "médio",
            "hard": "difícil",
            "fácil": "fácil",
            "médio": "médio",
            "difícil": "difícil"
        }
        
        pt_difficulty = difficulty_map.get(difficulty.lower(), "médio")
        
        try:
            logger.info(f"Generating question about topic: {topic.name}")
            
            # Prepare the prompt
            prompt = self.QUESTION_TEMPLATE.format(
                topic_name=topic.name,
                topic_description=topic.description or topic.name,
                difficulty=pt_difficulty
            )
            
            # Generate the question
            return self.generate_response(
                prompt=prompt,
                context=additional_context
            )
            
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            raise RuntimeError(f"Failed to generate question: {str(e)}")

    def explain_concept(
        self, 
        concept: str, 
        context: List[str] = None,
        detail_level: str = "medium"
    ) -> str:
        """
        Generate an explanation of a concept.
        
        Args:
            concept: The concept to explain
            context: List of context passages to include
            detail_level: Level of detail for the explanation
                         (e.g., "brief", "medium", "detailed")
            
        Returns:
            The generated explanation
            
        Raises:
            ValueError: If the concept is invalid
            RuntimeError: If the Claude API call fails
        """
        # Validate inputs
        if not concept or not concept.strip():
            raise ValueError("Concept is required")
            
        # Map detail level to Portuguese
        detail_map = {
            "brief": "breve",
            "medium": "detalhada",
            "detailed": "muito detalhada",
            "breve": "breve",
            "detalhada": "detalhada",
            "muito detalhada": "muito detalhada"
        }
        
        pt_detail = detail_map.get(detail_level.lower(), "detalhada")
        
        try:
            logger.info(f"Generating explanation for concept: {concept}")
            
            # Prepare the prompt
            prompt = self.EXPLANATION_TEMPLATE.format(
                concept=concept,
                detail_level=pt_detail
            )
            
            # Generate the explanation
            return self.generate_response(
                prompt=prompt,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            raise RuntimeError(f"Failed to generate explanation: {str(e)}")
            
    def set_custom_system_prompt(self, system_prompt: str, append: bool = False) -> None:
        """
        Update the system prompt used by the client.
        
        Args:
            system_prompt: New system prompt
            append: If True, append to the default prompt; if False, replace it
        """
        if append:
            # Append to the default template
            new_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
                additional_instructions=system_prompt
            )
        else:
            # Replace completely
            new_prompt = system_prompt
            
        # Update client's system prompt
        self.system_prompt = new_prompt
        self.client.system_prompt = new_prompt
        logger.info("Updated system prompt") 
