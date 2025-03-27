"""
Main entry point for the FUVEST exam study CLI tool.
"""
import os
import sys
import argparse
import logging
from typing import Dict, Any, List, Optional

from http.route import Router
from src.context import Context
from src.protocol import ProtocolRegistry
from src.usecases.document_manager import DocumentManager
from src.usecases.rag_service import RAGService
from src.infrastructure.claude_llm import ClaudeLLMService


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='FUVEST exam study CLI tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Upload document command
    upload_parser = subparsers.add_parser('upload', help='Upload a document')
    upload_parser.add_argument('file', help='Path to the document file')
    upload_parser.add_argument(
        '--topics', 
        nargs='+', 
        help='List of topics for the document'
    )
    
    # Ask question command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument(
        '--conversation', 
        help='ID of an existing conversation'
    )
    
    # List documents command
    list_parser = subparsers.add_parser('list', help='List documents')
    list_parser.add_argument(
        '--topic', 
        help='Filter by topic'
    )
    
    return parser.parse_args()


def setup_dependencies() -> Dict[str, Any]:
    """Set up application dependencies."""
    # Check API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logging.error("ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize services
    llm_service = ClaudeLLMService(api_key)
    
    # Initialize repositories (placeholder - would be real implementations)
    file_repository = {}  # Placeholder
    embedding_repository = {}  # Placeholder
    conversation_repository = {}  # Placeholder
    
    # Initialize use cases
    document_manager = DocumentManager(file_repository, None)  # Placeholder
    rag_service = RAGService(None, llm_service, conversation_repository)  # Placeholder
    
    # Initialize router
    router = Router()
    
    # Initialize protocol registry
    protocol_registry = ProtocolRegistry()
    
    return {
        'llm_service': llm_service,
        'document_manager': document_manager,
        'rag_service': rag_service,
        'router': router,
        'protocol_registry': protocol_registry
    }


def main():
    """Main entry point for the application."""
    # Set up logging
    setup_logging()
    
    # Parse arguments
    args = parse_args()
    
    # Set up dependencies
    dependencies = setup_dependencies()
    
    # Create context
    context = Context({
        'args': vars(args),
        'command': args.command,
        'dependencies': dependencies
    })
    
    # Get router
    router = dependencies['router']
    
    # Route command
    result = router.route(args.command, context.to_dict())
    
    # Print result
    if result:
        print(result.get('message', 'Command executed successfully'))
    else:
        print(f"Unknown command: {args.command}")


if __name__ == '__main__':
    main() 
