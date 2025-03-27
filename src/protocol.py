"""
Protocol handling for the Model-Context-Protocol pattern.
"""
from typing import Dict, Any, Callable, Protocol, Optional
import logging

from src.context import Context

logger = logging.getLogger(__name__)


class ProtocolHandler(Protocol):
    """Protocol for protocol handlers."""
    
    def handle(self, context: Context) -> Dict[str, Any]:
        """Handle a protocol request."""
        ...


class ProtocolRegistry:
    """Registry for protocol handlers."""
    
    def __init__(self):
        """Initialize the protocol registry."""
        self.handlers: Dict[str, ProtocolHandler] = {}
    
    def register(self, protocol_name: str, handler: ProtocolHandler) -> None:
        """
        Register a protocol handler.
        
        Args:
            protocol_name: Name of the protocol
            handler: Protocol handler
        """
        self.handlers[protocol_name] = handler
        logger.debug(f"Registered handler for protocol: {protocol_name}")
    
    def get_handler(self, protocol_name: str) -> Optional[ProtocolHandler]:
        """
        Get a protocol handler by name.
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            Protocol handler or None if not found
        """
        return self.handlers.get(protocol_name)
    
    def handle(self, protocol_name: str, context: Context) -> Dict[str, Any]:
        """
        Handle a protocol request.
        
        Args:
            protocol_name: Name of the protocol
            context: Request context
            
        Returns:
            Handler response
            
        Raises:
            ValueError: If handler not found
        """
        handler = self.get_handler(protocol_name)
        if not handler:
            raise ValueError(f"No handler found for protocol: {protocol_name}")
        
        return handler.handle(context) 
