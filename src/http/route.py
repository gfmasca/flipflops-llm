"""
Router module for the Model-Context-Protocol pattern.
"""
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class Router:
    """Router for the Model-Context-Protocol pattern."""
    
    def __init__(self):
        """Initialize the router."""
        self.routes: Dict[str, Callable] = {}
        self.middlewares = []
    
    def register(self, command: str, handler: Callable):
        """
        Register a route handler.
        
        Args:
            command: Command name to route
            handler: Handler function for the command
        """
        self.routes[command] = handler
        logger.debug(f"Registered handler for command: {command}")
    
    def add_middleware(self, middleware: Callable):
        """
        Add middleware to the router.
        
        Args:
            middleware: Middleware function
        """
        self.middlewares.append(middleware)
    
    def route(self, command: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route a command to its handler.
        
        Args:
            command: Command to route
            context: Context dictionary for the command
            
        Returns:
            Handler response or None if no handler found
        """
        if command not in self.routes:
            logger.warning(f"No handler found for command: {command}")
            return None
        
        # Apply middlewares
        for middleware in self.middlewares:
            context = middleware(context)
        
        # Call handler
        handler = self.routes[command]
        return handler(context) 
