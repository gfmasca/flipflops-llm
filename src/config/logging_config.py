"""
Configuração de logging para a aplicação.
"""
import os
import logging
import logging.handlers
from typing import Optional


def configure_logging(level_name: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure the logging for the application.
    
    Args:
        level_name: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (optional)
    """
    # Convert level name to logging level
    level = getattr(logging, level_name)
    
    # Basic configuration
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Create file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure the root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )
    
    # Set specific logger levels
    # For example, to reduce verbosity of third-party libraries:
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configurado com nível {level_name}")
    if log_file:
        logger.info(f"Logs sendo salvos em {log_file}") 
