"""
Dependency Injection Container para a aplicação FLIPFLOPS.

Este módulo fornece um contêiner centralizado para gerenciar todas as dependências
da aplicação, seguindo os princípios de inversão de dependência da Clean Architecture.
"""
import os
import logging
import configparser
from typing import Dict, Any, Optional

# MCP components
from src.mcp.model import FlipflopsModel
from src.mcp.context import FlipflopsContext
from src.mcp.protocol import FlipflopsProtocol
from src.mcp.route import FlipflopsRoute

# Controllers
from src.http.controllers.main_controller import MainController

# UI
from src.infrastructure.ui.command_line_interface import CommandLineInterface

# Use cases
from src.usecases.question_answering_usecase import QuestionAnsweringUseCase
from src.usecases.exam_generation_usecase import ExamGenerationUseCase
from src.usecases.conversation_management_usecase import ConversationManagementUseCase
from src.usecases.response_generation_usecase import ResponseGenerationUseCase
from src.usecases.query_processing_usecase import QueryProcessingUseCase

# Services
from src.infrastructure.services.claude_llm_service import ClaudeLLMService
from src.infrastructure.services.claude_query_service import ClaudeQueryService
from src.infrastructure.services.faiss_embedding_service import FAISSEmbeddingService

# Repositories
from src.infrastructure.repositories.pdf_document_repository import PDFDocumentRepository
from src.infrastructure.repositories.faiss_embedding_repository import FAISSEmbeddingRepository
from src.infrastructure.repositories.file_conversation_repository import FileConversationRepository
from src.infrastructure.repositories.file_topic_repository import FileTopicRepository

# Setup logger
logger = logging.getLogger(__name__)


class Container:
    """
    Contêiner de Injeção de Dependência para o FLIPFLOPS.
    
    Responsável por inicializar, configurar e fornecer acesso a todos os
    componentes da aplicação. Centraliza a criação de objetos e 
    gerencia suas dependências.
    """
    
    def __init__(
        self, 
        config_path: Optional[str] = None, 
        data_dir: Optional[str] = None
    ):
        """
        Inicializa o contêiner com as configurações fornecidas.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            data_dir: Diretório para armazenamento de dados
        """
        # Inicializar valores de configuração
        self.config_path = config_path or os.getenv('CONFIG_PATH', 'config.ini')
        self.data_dir = data_dir or os.getenv('DATA_DIR', 'data')
        
        # Carregar configurações
        self.config = self._load_config()
        
        # Criar diretórios de dados
        self._create_data_dirs()
        
        # Inicializar componentes
        self._init_repositories()
        self._init_services()
        self._init_usecases()
        self._init_mcp_components()
        self._init_controllers()
        self._init_ui()
        
        logger.info("Contêiner de dependências inicializado com sucesso")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração do arquivo config.ini ou cria uma configuração padrão.
        
        Returns:
            Dicionário com configurações
        """
        config = {}
        
        # Verificar se o arquivo de configuração existe
        if os.path.exists(self.config_path):
            logger.info(f"Carregando configurações de {self.config_path}")
            parser = configparser.ConfigParser()
            parser.read(self.config_path)
            
            # Configurações da API
            if 'API' in parser:
                config['api_key'] = parser.get('API', 'api_key', fallback='')
                config['api_url'] = parser.get(
                    'API', 'api_url', 
                    fallback='https://api.anthropic.com/v1/messages'
                )
                config['api_model'] = parser.get(
                    'API', 'api_model', 
                    fallback='claude-3-sonnet-20240229'
                )
            
            # Configurações da aplicação
            if 'APP' in parser:
                config['max_tokens'] = parser.getint('APP', 'max_tokens', fallback=4096)
                config['temperature'] = parser.getfloat('APP', 'temperature', fallback=0.7)
            
            # Configurações de dados
            if 'DATA' in parser:
                config['context_file'] = parser.get(
                    'DATA', 'context_file', 
                    fallback=os.path.join(self.data_dir, 'FLIPFLOP.md')
                )
                config['documents_dir'] = parser.get(
                    'DATA', 'documents_dir',
                    fallback=os.path.join(self.data_dir, 'documents')
                )
        else:
            logger.warning(f"Arquivo de configuração {self.config_path} não encontrado")
            config = self._create_default_config()
            
        # Sobrescrever configurações com variáveis de ambiente
        config['api_key'] = os.getenv('CLAUDE_API_KEY', config.get('api_key', ''))
        config['api_model'] = os.getenv(
            'MODEL_NAME', 
            config.get('api_model', 'claude-3-sonnet-20240229')
        )
        config['max_tokens'] = int(
            os.getenv('MAX_TOKENS', config.get('max_tokens', 4096))
        )
        
        return config
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Cria uma configuração padrão quando o arquivo config.ini não existe.
        
        Returns:
            Dicionário com configurações padrão
        """
        logger.info("Criando configuração padrão")
        return {
            'api_key': '',
            'api_url': 'https://api.anthropic.com/v1/messages',
            'api_model': 'claude-3-sonnet-20240229',
            'max_tokens': 4096,
            'temperature': 0.7,
            'context_file': os.path.join(self.data_dir, 'FLIPFLOP.md'),
            'documents_dir': os.path.join(self.data_dir, 'documents'),
        }
    
    def _create_data_dirs(self) -> None:
        """Cria os diretórios necessários para os dados da aplicação."""
        # Diretórios principais
        self.documents_dir = os.path.join(self.data_dir, 'documents')
        self.embeddings_dir = os.path.join(self.data_dir, 'embeddings')
        self.conversations_dir = os.path.join(self.data_dir, 'conversations')
        self.topics_dir = os.path.join(self.data_dir, 'topics')
        
        # Criar diretórios se não existirem
        for directory in [
            self.data_dir,
            self.documents_dir, 
            self.embeddings_dir,
            self.conversations_dir,
            self.topics_dir
        ]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Diretório criado: {directory}")
    
    def _init_repositories(self) -> None:
        """Inicializa os repositórios da aplicação."""
        logger.info("Inicializando repositórios")
        
        # Repositório de documentos
        self.document_repository = PDFDocumentRepository(
            storage_dir=self.documents_dir
        )
        
        # Repositório de embeddings
        self.embedding_repository = FAISSEmbeddingRepository(
            storage_dir=self.embeddings_dir
        )
        
        # Repositório de conversas
        self.conversation_repository = FileConversationRepository(
            storage_dir=self.conversations_dir,
            context_file_path=self.config['context_file']
        )
        
        # Repositório de tópicos
        self.topic_repository = FileTopicRepository(
            storage_dir=self.topics_dir
        )
    
    def _init_services(self) -> None:
        """Inicializa os serviços da aplicação."""
        logger.info("Inicializando serviços")
        
        # Verificar API key
        if not self.config.get('api_key'):
            logger.warning(
                "Chave API não configurada. Os serviços LLM não funcionarão corretamente."
            )
        
        # Serviço LLM
        self.llm_service = ClaudeLLMService(
            api_key=self.config.get('api_key', ''),
            api_url=self.config.get('api_url', ''),
            model=self.config.get('api_model', ''),
            max_tokens=self.config.get('max_tokens', 4096),
            temperature=self.config.get('temperature', 0.7)
        )
        
        # Serviço de consulta
        self.query_service = ClaudeQueryService(
            api_key=self.config.get('api_key', ''),
            api_url=self.config.get('api_url', ''),
            model=self.config.get('api_model', ''),
            max_tokens=self.config.get('max_tokens', 4096),
            temperature=self.config.get('temperature', 0.7)
        )
        
        # Serviço de embeddings
        self.embedding_service = FAISSEmbeddingService(
            model_name="sentence-transformers/distiluse-base-multilingual-cased-v1"
        )
    
    def _init_usecases(self) -> None:
        """Inicializa os casos de uso da aplicação."""
        logger.info("Inicializando casos de uso")
        
        # Geração de respostas
        self.response_generation_usecase = ResponseGenerationUseCase(
            llm_service=self.llm_service
        )
        
        # Processamento de consultas
        self.query_processing_usecase = QueryProcessingUseCase(
            query_service=self.query_service,
            embedding_service=self.embedding_service,
            document_repository=self.document_repository,
            embedding_repository=self.embedding_repository
        )
        
        # Gerenciamento de conversas
        self.conversation_management_usecase = ConversationManagementUseCase(
            conversation_repository=self.conversation_repository
        )
        
        # Resposta a perguntas
        self.question_answering_usecase = QuestionAnsweringUseCase(
            query_processing=self.query_processing_usecase,
            response_generation=self.response_generation_usecase,
            conversation_management=self.conversation_management_usecase
        )
        
        # Geração de exames
        self.exam_generation_usecase = ExamGenerationUseCase(
            llm_service=self.llm_service,
            query_service=self.query_service,
            embedding_service=self.embedding_service,
            document_repository=self.document_repository,
            topic_repository=self.topic_repository
        )
    
    def _init_mcp_components(self) -> None:
        """Inicializa os componentes do padrão MCP."""
        logger.info("Inicializando componentes MCP")
        
        # Modelo
        self.model = FlipflopsModel(
            question_answering_usecase=self.question_answering_usecase,
            exam_generation_usecase=self.exam_generation_usecase,
            conversation_management_usecase=self.conversation_management_usecase
        )
        
        # Contexto
        self.context = FlipflopsContext(
            conversation_repository=self.conversation_repository
        )
        
        # Protocolo
        self.protocol = FlipflopsProtocol(
            model=self.model,
            context=self.context
        )
        
        # Rota
        self.route = FlipflopsRoute(
            model=self.model,
            context=self.context,
            protocol=self.protocol
        )
    
    def _init_controllers(self) -> None:
        """Inicializa os controladores da aplicação."""
        logger.info("Inicializando controladores")
        
        # Controlador principal
        self.main_controller = MainController(
            route=self.route
        )
    
    def _init_ui(self) -> None:
        """Inicializa as interfaces de usuário."""
        logger.info("Inicializando interfaces de usuário")
        
        # Interface de linha de comando
        self.cli = CommandLineInterface(
            controller=self.main_controller
        )
    
    def get_cli(self) -> CommandLineInterface:
        """
        Obtém a interface de linha de comando.
        
        Returns:
            Interface de linha de comando configurada
        """
        return self.cli 
