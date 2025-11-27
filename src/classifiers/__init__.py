"""
Classifier backends for query routing, tool selection, and entity extraction.

This module provides both LLM-based and local model-based classifiers
that can be used interchangeably via the ClassifierBackend protocol.
"""

from .base import ClassifierBackend, ClassificationResult
from .local_classifier import LocalClassifier

__all__ = [
    'ClassifierBackend',
    'ClassificationResult', 
    'LocalClassifier',
]
