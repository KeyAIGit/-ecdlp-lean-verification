"""Dependency-light Python reference methods for synthetic toy ECDLP fixtures."""

from .reference_dlog import (
    BSGS_METHOD_ID,
    RHO_METHOD_ID,
    MethodBudget,
    ReferenceResult,
    solve_bsgs,
    solve_method_request,
    solve_ordinary_rho,
    solve_reference,
)
from .validation import validate_candidate_independently

__all__ = [
    "BSGS_METHOD_ID",
    "RHO_METHOD_ID",
    "MethodBudget",
    "ReferenceResult",
    "solve_bsgs",
    "solve_method_request",
    "solve_ordinary_rho",
    "solve_reference",
    "validate_candidate_independently",
]
