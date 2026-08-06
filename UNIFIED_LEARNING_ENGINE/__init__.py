"""
UNIFIED_LEARNING_ENGINE - Self-Learning System for ARC v7.6 Final

Modul ini menyediakan sistem pembelajaran mandiri yang lengkap:
- Experience Collector: Mengumpulkan data dari eksekusi nyata
- Feedback Loop: Belajar dari kesalahan dan keberhasilan
- Model Trainer: Training ML model dari collected data
- Dynamic Knowledge Base: Knowledge base yang berkembang
- Self-Learning Orchestrator: Koordinator utama sistem pembelajaran
"""

from .experience_collector import ExperienceCollector
from .feedback_loop import FeedbackLoop
from .model_trainer import ModelTrainer
from .dynamic_knowledge_base import DynamicKnowledgeBase
from .self_learning_orchestrator import SelfLearningOrchestrator
from .learning_bridge import LearningBridge

__version__ = "1.1.0"
__all__ = [
    'ExperienceCollector',
    'FeedbackLoop',
    'ModelTrainer',
    'DynamicKnowledgeBase',
    'SelfLearningOrchestrator',
    'LearningBridge'
]
