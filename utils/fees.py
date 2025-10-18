"""
Compute budget and priority fee utilities for Solana transactions.

This module provides helper functions to add compute budget instructions
to transactions with configurable limits and prices from environment variables.
"""

import os
from typing import List, Optional
from solders.instruction import Instruction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price


# Environment variable configuration with safe defaults and caps
DEFAULT_COMPUTE_UNIT_LIMIT = 400_000
MAX_COMPUTE_UNIT_LIMIT = 1_400_000
MIN_COMPUTE_UNIT_LIMIT = 200_000

DEFAULT_COMPUTE_UNIT_PRICE = 1_000  # micro-lamports per compute unit
MAX_COMPUTE_UNIT_PRICE = 100_000_000  # Cap at 0.1 SOL per 1M CU
MIN_COMPUTE_UNIT_PRICE = 0


def get_compute_unit_limit() -> int:
    """
    Get compute unit limit from environment variable or use default.
    
    Returns:
        int: Compute unit limit capped between MIN and MAX values
    """
    try:
        limit = int(os.getenv("COMPUTE_UNIT_LIMIT", str(DEFAULT_COMPUTE_UNIT_LIMIT)))
        # Apply caps for safety
        return max(MIN_COMPUTE_UNIT_LIMIT, min(MAX_COMPUTE_UNIT_LIMIT, limit))
    except (ValueError, TypeError):
        return DEFAULT_COMPUTE_UNIT_LIMIT


def get_compute_unit_price() -> int:
    """
    Get compute unit price from environment variable or use default.
    
    Returns:
        int: Compute unit price (micro-lamports) capped between MIN and MAX values
    """
    try:
        price = int(os.getenv("COMPUTE_UNIT_PRICE", str(DEFAULT_COMPUTE_UNIT_PRICE)))
        # Apply caps for safety
        return max(MIN_COMPUTE_UNIT_PRICE, min(MAX_COMPUTE_UNIT_PRICE, price))
    except (ValueError, TypeError):
        return DEFAULT_COMPUTE_UNIT_PRICE


def with_compute_budget(
    instructions: List[Instruction],
    compute_unit_limit: Optional[int] = None,
    compute_unit_price: Optional[int] = None
) -> List[Instruction]:
    """
    Prepend compute budget instructions to a list of instructions.
    
    This function adds compute budget instructions (set_compute_unit_limit and 
    set_compute_unit_price) to the beginning of the instruction list. If limit
    or price are not specified, they will be read from environment variables
    or use safe defaults.
    
    Args:
        instructions: List of instructions to prepend compute budget to
        compute_unit_limit: Optional compute unit limit override
        compute_unit_price: Optional compute unit price override (micro-lamports)
    
    Returns:
        List[Instruction]: New list with compute budget instructions prepended
    
    Example:
        >>> instructions = [swap_ix]
        >>> final_instructions = with_compute_budget(instructions)
        >>> # final_instructions now has compute budget instructions first
    """
    # Get values from parameters or environment/defaults
    if compute_unit_limit is None:
        compute_unit_limit = get_compute_unit_limit()
    else:
        # Apply safety caps even for explicit values
        compute_unit_limit = max(MIN_COMPUTE_UNIT_LIMIT, min(MAX_COMPUTE_UNIT_LIMIT, compute_unit_limit))
    
    if compute_unit_price is None:
        compute_unit_price = get_compute_unit_price()
    else:
        # Apply safety caps even for explicit values
        compute_unit_price = max(MIN_COMPUTE_UNIT_PRICE, min(MAX_COMPUTE_UNIT_PRICE, compute_unit_price))
    
    # Create compute budget instructions
    compute_budget_instructions = [
        set_compute_unit_limit(compute_unit_limit),
        set_compute_unit_price(compute_unit_price)
    ]
    
    # Prepend to instruction list
    return compute_budget_instructions + instructions


__all__ = [
    'with_compute_budget',
    'get_compute_unit_limit',
    'get_compute_unit_price',
    'set_compute_unit_limit',
    'set_compute_unit_price',
]
