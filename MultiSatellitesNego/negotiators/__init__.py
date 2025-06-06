"""
Title: Negotiator registry module

This module provides easy access to all negotiator implementations.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date: 14/04/2025
"""
from .base import BaseNegotiator
from .v02 import NegotiatorV02
from .v03 import NegotiatorV03
from .v03_1 import NegotiatorV03_1
from .v04 import NegotiatorV04
from .v04_1 import NegotiatorV04_1
from .v05 import NegotiatorV05
from .random import RandomNegotiator

# Registry of all available negotiators
NEGOTIATOR_REGISTRY = {
    "v02": NegotiatorV02,
    "v03": NegotiatorV03,
    "v031": NegotiatorV03_1,
    "v04": NegotiatorV04,
    "v041": NegotiatorV04_1,
    "v05": NegotiatorV05,
    "random": RandomNegotiator
}

def get_negotiator(version: str) -> type[BaseNegotiator]:
    """
    Get a negotiator class by version name.

    Args:
        version: The version name of the negotiator (e.g., "v02", "v03", "random")

    Returns:
        The negotiator class

    Raises:
        ValueError: If the version is not found in the registry
    """
    if version not in NEGOTIATOR_REGISTRY:
        raise ValueError(f"Unknown negotiator version: {version}. Available versions: {list(NEGOTIATOR_REGISTRY.keys())}")
    return NEGOTIATOR_REGISTRY[version]

__all__ = ['BaseNegotiator', 'get_negotiator', 'NEGOTIATOR_REGISTRY']