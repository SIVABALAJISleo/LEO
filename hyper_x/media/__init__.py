#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/media/__init__.py
========================
Total GPU Omega: Software-Defined Media Ecosystem.
"""

from .media_engine import MediaProcessingEngine
from .video_elimination import VideoComputationEliminator

__all__ = [
    "MediaProcessingEngine",
    "VideoComputationEliminator"
]
