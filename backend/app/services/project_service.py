"""Deprecated — superseded by brand_service + product_service.

Re-exports ``_load`` from product_service for any lingering imports.
"""
from app.services.product_service import _load  # noqa: F401
