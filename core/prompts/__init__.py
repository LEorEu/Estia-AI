#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
提示词管理模块
集中管理所有LLM提示词模板
"""

from .memory_evaluation import MemoryEvaluationPrompts
from .dialogue_generation import DialogueGenerationPrompts

__all__ = [
    'MemoryEvaluationPrompts',
    'DialogueGenerationPrompts'
] 