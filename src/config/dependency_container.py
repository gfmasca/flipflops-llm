"""
Dependency container for the application.

This module provides a centralized container for managing dependencies
and their initialization.
"""
import os
import logging
import configparser
from pathlib import Path
from typing import Dict, Any

from src.infrastructure.ui.command_line_interface import CommandLineInterface
from src.http.controllers.main_controller import MainController

from src.usecases.question_answering_usecase import QuestionAnsweringUseCase
from src.usecases.exam_generation_usecase import ExamGenerationUseCase
from src.usecases.conversation_management_usecase import ConversationManagementUseCase
from src.usecases.response_generation_usecase import ResponseGenerationUseCase
from src.usecases.query_processing_usecase import QueryProcessingUseCase

from src.interfaces.services.llm_service import LLMService
from src.interfaces.services.query_service import QueryService
from src.interfaces.services.embedding_service import EmbeddingService

from src.interfaces.repositories.document_repository import DocumentRepository
from src.interfaces.repositories.embedding_repository import EmbeddingRepository
from src.interfaces.repositories.conversation_repository import ConversationRepository
from src.interfaces.repositories.topic_repository import TopicRepository

from src.infrastructure.services.claude_llm_service import ClaudeLLMService
from src.infrastructure.services.claude_query_service import ClaudeQueryService
from src.infrastructure.services.faiss_embedding_service import FAISSEmbeddingService

from src.infrastructure.repositories.pdf_document_repository import PDFDocumentRepository
from src.infrastructure.repositories.faiss_embedding_repository import FAISSEmbeddingRepository
from src.infrastructure.repositories.file_conversation_repository import FileConversationRepository
from src.infrastructure.repositories.file_topic_repository import FileTopicRepository

# MCP components
from src.mcp.model import FlipflopsModel
from src.mcp.context import FlipflopsContext
from src.mcp.protocol import FlipflopsProtocol
from src.mcp.route import FlipflopsRoute

# Configure logger
logger = logging.getLogger(__name__)


class DependencyContainer:
    """
    Container for managing application dependencies.
    
    This class is responsible for:
    1. Loading configuration
    2. Initializing services and repositories
    3. Providing access to initialized components
    """
    
    def __init__(self, config_file: str, data_dir: str):
        """
        Initialize the dependency container.
        
        Args:
            config_file: Path to the configuration file
            data_dir: Path to the data directory
        """
        self.config_file = config_file
        self.data_dir = data_dir
        self.config = self._load_config()
        
        # Create subdirectories
        self.docs_dir = os.path.join(data_dir, "documents")
        self.embeddings_dir = os.path.join(data_dir, "embeddings")
        self.conversations_dir = os.path.join(data_dir, "conversations")
        self.topics_dir = os.path.join(data_dir, "topics")
        
        for directory in [self.docs_dir, self.embeddings_dir, 
                         self.conversations_dir, self.topics_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize components
        self._init_repositories()
        self._init_services()
        self._init_usecases()
        self._init_mcp_components()
        self._init_controllers()
        self._init_ui()
        
        logger.info("Dependency container initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the config file.
        
        Returns:
            A dictionary with configuration values
        """
        config = {}
        
        # Check if config file exists
        if not os.path.exists(self.config_file):
            logger.warning(
                f"Config file not found: {self.config_file}. Using default values."
            )
            return self._create_default_config()
        
        # Load config from file
        try:
            parser = configparser.ConfigParser()
            parser.read(self.config_file)
            
            # API settings
            if "API" in parser:
                config["api_key"] = parser.get("API", "api_key", fallback="")
                config["api_url"] = parser.get(
                    "API", "api_url", 
                    fallback="https://api.anthropic.com/v1/messages"
                )
                config["api_model"] = parser.get(
                    "API", "api_model", fallback="claude-3-haiku-20240307"
                )
            
            # Application settings
            if "APP" in parser:
                config["max_tokens"] = parser.getint("APP", "max_tokens", fallback=1000)
                config["temperature"] = parser.getfloat("APP", "temperature", fallback=0.7)
                config["context_file"] = parser.get(
                    "APP", "context_file", 
                    fallback=os.path.join(self.data_dir, "FLIPFLOP.md")
                )
            
            logger.info(f"Loaded configuration from {self.config_file}")
            return config
        except Exception as e:
            logger.exception(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create default configuration.
        
        Returns:
            A dictionary with default configuration values
        """
        config = {
            "api_key": os.environ.get("CLAUDE_API_KEY", ""),
            "api_url": "https://api.anthropic.com/v1/messages",
            "api_model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "temperature": 0.7,
            "context_file": os.path.join(self.data_dir, "FLIPFLOP.md")
        }
        
        # Try to save default config
        try:
            self._save_default_config(config)
        except Exception as e:
            logger.exception(f"Error saving default config: {e}")
        
        return config
    
    def _save_default_config(self, config: Dict[str, Any]) -> None:
        """
        Save default configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        parser = configparser.ConfigParser()
        
        # API section
        parser["API"] = {
            "api_key": config["api_key"],
            "api_url": config["api_url"],
            "api_model": config["api_model"]
        }
        
        # APP section
        parser["APP"] = {
            "max_tokens": str(config["max_tokens"]),
            "temperature": str(config["temperature"]),
            "context_file": config["context_file"]
        }
        
        # Save to file
        with open(self.config_file, 'w') as f:
            parser.write(f)
        
        logger.info(f"Saved default configuration to {self.config_file}")
    
    def _init_repositories(self) -> None:
        """Initialize all repositories."""
        # Document repository
        self.document_repository = PDFDocumentRepository(self.docs_dir)
        
        # Embedding repository
        self.embedding_repository = FAISSEmbeddingRepository(self.embeddings_dir)
        
        # Conversation repository
        self.conversation_repository = FileConversationRepository(
            self.conversations_dir, 
            self.config["context_file"]
        )
        
        # Topic repository
        self.topic_repository = FileTopicRepository(self.topics_dir)
    
    def _init_services(self) -> None:
        """Initialize all services."""
        # Check if API key is set
        api_key = self.config.get("api_key", "")
        if not api_key:
            api_key = os.environ.get("CLAUDE_API_KEY", "")
            if not api_key:
                logger.warning(
                    "CLAUDE_API_KEY not found in config or environment variables. "
                    "LLM services will not work properly."
                )
        
        # LLM service
        self.llm_service = ClaudeLLMService(
            api_key=api_key,
            api_url=self.config.get("api_url"),
            model=self.config.get("api_model"),
            max_tokens=self.config.get("max_tokens", 1000),
            temperature=self.config.get("temperature", 0.7)
        )
        
        # Query service
        self.query_service = ClaudeQueryService(
            api_key=api_key,
            api_url=self.config.get("api_url"),
            model=self.config.get("api_model"),
            max_tokens=self.config.get("max_tokens", 1000),
            temperature=self.config.get("temperature", 0.7)
        )
        
        # Embedding service
        self.embedding_service = FAISSEmbeddingService(
            model_name="sentence-transformers/distiluse-base-multilingual-cased-v1"
        )
    
    def _init_usecases(self) -> None:
        """Initialize all use cases."""
        # Response generation use case
        self.response_generation_usecase = ResponseGenerationUseCase(
            llm_service=self.llm_service
        )
        
        # Query processing use case
        self.query_processing_usecase = QueryProcessingUseCase(
            query_service=self.query_service,
            embedding_service=self.embedding_service,
            document_repository=self.document_repository,
            embedding_repository=self.embedding_repository
        )
        
        # Conversation management use case
        self.conversation_management_usecase = ConversationManagementUseCase(
            conversation_repository=self.conversation_repository
        )
        
        # Question answering use case
        self.question_answering_usecase = QuestionAnsweringUseCase(
            query_processing=self.query_processing_usecase,
            response_generation=self.response_generation_usecase,
            conversation_management=self.conversation_management_usecase
        )
        
        # Exam generation use case
        self.exam_generation_usecase = ExamGenerationUseCase(
            llm_service=self.llm_service,
            query_service=self.query_service,
            embedding_service=self.embedding_service,
            document_repository=self.document_repository,
            topic_repository=self.topic_repository
        )
    
    def _init_mcp_components(self) -> None:
        """Initialize MCP components."""
        # Model component
        self.mcp_model = FlipflopsModel(
            question_answering_usecase=self.question_answering_usecase,
            exam_generation_usecase=self.exam_generation_usecase,
            conversation_management_usecase=self.conversation_management_usecase
        )
        
        # Context component
        self.mcp_context = FlipflopsContext(
            conversation_repository=self.conversation_repository
        )
        
        # Protocol component
        self.mcp_protocol = FlipflopsProtocol(
            model=self.mcp_model,
            context=self.mcp_context
        )
        
        # Route component
        self.mcp_route = FlipflopsRoute(
            model=self.mcp_model,
            context=self.mcp_context,
            protocol=self.mcp_protocol
        )
        
        logger.info("MCP components initialized")
    
    def _init_controllers(self) -> None:
        """Initialize all controllers."""
        # Now using MCP route component
        self.main_controller = MainController(
            route=self.mcp_route
        )
        
        logger.info("Controllers initialized with MCP pattern")
    
    def _init_ui(self) -> None:
        """Initialize the UI components."""
        self.cli_interface = CommandLineInterface(
            controller=self.main_controller
        )
    
    def get_cli_interface(self) -> CommandLineInterface:
        """
        Get the CLI interface.
        
        Returns:
            The initialized CLI interface
        """
        return self.cli_interface


def initialize_container(config_file: str, data_dir: str) -> DependencyContainer:
    """
    Initialize the dependency container.
    
    Args:
        config_file: Path to the configuration file
        data_dir: Path to the data directory
        
    Returns:
        Initialized dependency container
    """
    return DependencyContainer(config_file, data_dir) 
