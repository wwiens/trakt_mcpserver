"""
Prompts module for Trakt MCP server.

This module provides predefined conversation prompts for common entertainment
discovery and search scenarios.
"""

from .basic import register_basic_prompts

__all__ = ["register_basic_prompts"]
