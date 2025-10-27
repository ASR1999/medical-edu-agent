"""
EHR Provider Factory

This module provides a factory pattern to instantiate the appropriate EHR provider
based on configuration. It allows seamless switching between mock and FHIR data sources.
"""

import logging
from typing import Optional

from app.config import EHR_PROVIDER
from .ehr_provider import EHRProvider
from .ehr_mock_provider import MockEHRProvider
from .ehr_fhir_provider import FHIRProvider

logger = logging.getLogger(__name__)

# Singleton instance
_provider_instance: Optional[EHRProvider] = None


def get_ehr_provider(force_recreate: bool = False) -> EHRProvider:
    """
    Get the configured EHR provider instance (singleton pattern).
    
    Args:
        force_recreate: If True, creates a new instance even if one exists
        
    Returns:
        Configured EHR provider instance
    """
    global _provider_instance
    
    if _provider_instance is None or force_recreate:
        provider_type = EHR_PROVIDER.lower()
        
        if provider_type == "fhir":
            logger.info("Initializing FHIR EHR Provider")
            _provider_instance = FHIRProvider()
            
        elif provider_type == "hybrid":
            # Hybrid mode: Try FHIR first, fall back to mock on error
            logger.info("Initializing Hybrid EHR Provider (FHIR with mock fallback)")
            try:
                _provider_instance = FHIRProvider()
                logger.info("FHIR provider initialized successfully in hybrid mode")
            except Exception as e:
                logger.warning(f"FHIR provider failed in hybrid mode, falling back to mock: {e}")
                _provider_instance = MockEHRProvider()
                
        else:  # Default to mock
            logger.info("Initializing Mock EHR Provider")
            _provider_instance = MockEHRProvider()
        
        logger.info(f"EHR Provider active: {type(_provider_instance).__name__}")
    
    return _provider_instance


def get_provider_type() -> str:
    """
    Get the type of the active provider.
    
    Returns:
        Provider type name (e.g., "MockEHRProvider", "FHIRProvider")
    """
    provider = get_ehr_provider()
    return type(provider).__name__


def reload_provider() -> EHRProvider:
    """
    Force reload of the provider (useful for config changes).
    
    Returns:
        Newly created provider instance
    """
    logger.info("Reloading EHR provider")
    return get_ehr_provider(force_recreate=True)

