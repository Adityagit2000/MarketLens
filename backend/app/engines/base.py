"""
Base Engine Class

Abstract base class defining the common interface for all engines.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import logging


class BaseEngine(ABC):
    """
    Abstract base class for all market intelligence engines.
    
    Each engine follows a consistent interface:
    - initialize(): Setup resources
    - process(): Main processing logic
    - get_status(): Current engine state
    - shutdown(): Cleanup resources
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"engine.{name}")
        self._initialized = False
        self._last_run: Optional[datetime] = None
        self._status = "idle"

    async def initialize(self) -> bool:
        """
        Initialize engine resources.
        
        Override this method to setup database connections,
        load models, or allocate resources.
        """
        self.logger.info(f"Initializing {self.name} engine")
        self._initialized = True
        self._status = "ready"
        return True

    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main processing logic for the engine.
        
        This method must be implemented by each specific engine.
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "name": self.name,
            "status": self._status,
            "initialized": self._initialized,
            "last_run": self._last_run.isoformat() if self._last_run else None,
        }

    async def shutdown(self) -> bool:
        """
        Cleanup engine resources.
        
        Override to release database connections, save state, etc.
        """
        self.logger.info(f"Shutting down {self.name} engine")
        self._initialized = False
        self._status = "stopped"
        return True

    def _update_run_time(self):
        """Update last run timestamp."""
        self._last_run = datetime.utcnow()

    def _set_status(self, status: str):
        """Update engine status."""
        self._status = status
        self.logger.debug(f"Engine status: {status}")
