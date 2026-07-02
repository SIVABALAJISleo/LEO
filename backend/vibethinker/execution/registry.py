import inspect
from typing import Callable, Dict, Any, Awaitable
import logging

logger = logging.getLogger(__name__)

ActionHandler = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[Dict[str, Any]]]

class ActionRegistry:
    """
    Registry for execution handlers.
    Maps an action string (e.g., 'retrieve', 'execute_python') to an asynchronous handler function.
    """
    _handlers: Dict[str, ActionHandler] = {}
    
    @classmethod
    def register(cls, action_name: str) -> Callable[[ActionHandler], ActionHandler]:
        """
        Decorator to register a function as an action handler.
        """
        def decorator(func: ActionHandler) -> ActionHandler:
            if not inspect.iscoroutinefunction(func):
                raise ValueError(f"Action handler '{action_name}' must be an async function.")
            cls._handlers[action_name] = func
            logger.info(f"Registered action handler for: {action_name}")
            return func
        return decorator

    @classmethod
    def get_handler(cls, action_name: str) -> ActionHandler:
        """
        Retrieves the handler for a specific action.
        Raises ValueError if not found.
        """
        if action_name not in cls._handlers:
            raise ValueError(f"No action handler registered for action: '{action_name}'")
        return cls._handlers[action_name]
    
    @classmethod
    def clear(cls):
        """Clears all registered handlers (mostly for testing)."""
        cls._handlers.clear()
