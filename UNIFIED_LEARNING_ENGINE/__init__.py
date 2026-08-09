"""
UNIFIED_LEARNING_ENGINE - Advanced Self-Learning System dengan AI Enhancement
Sistem pembelajaran mandiri yang sudah di-upgrade dengan AI untuk membuat ARC semakin pintar
"""

# Core components (existing)
from .experience_collector import ExperienceCollector, ExperienceType, OutcomeType
from .feedback_loop import FeedbackLoop
from .unified_model_trainer import UnifiedModelTrainer, ModelTrainer, AIModelTrainer, EnhancedMLTrainer
from .dynamic_knowledge_base import DynamicKnowledgeBase
from .self_learning_orchestrator import SelfLearningOrchestrator
from .learning_bridge import LearningBridge

# Security validation
from .security_validator import SecurityValidator, VulnerabilityPatternValidator

# AI-Enhanced components (new)
from .ai_feature_extractor import AIFeatureExtractor
from .ai_fine_tuning_pipeline import AIFineTuningPipeline
from .ai_lesson_generator import AILessonGenerator
from .closed_loop_feedback import ClosedLoopFeedback
from .reinforcement_learning import ReinforcementLearner
from .advanced_self_learning_integration import AdvancedSelfLearningIntegration

# Backward compatibility imports (deprecated, will be removed in v3.0)
import warnings
warnings.warn(
    "ModelTrainer, AIModelTrainer, and EnhancedMLTrainer are deprecated. Use UnifiedModelTrainer instead.",
    DeprecationWarning,
    stacklevel=2
)

# Supporting components
from .technique_knowledge_graph import TechniqueKnowledgeGraph
from .playbook_integrator import PlaybookIntegrator
from .ctf_challenge_analyzer import CTFChallengeAnalyzer
from .vulnerability_pattern_unifier import VulnerabilityPatternUnifier

# Writeup scrapers
from .hackerone_writeup_scraper import HackerOneWriteupScraper
from .bugcrowd_writeup_scraper import BugCrowdWriteupScraper
from .intigriti_writeup_scraper import IntigritiWriteupScraper
from .yeswehack_writeup_scraper import YesWeHackWriteupScraper
from .immunefi_writeup_scraper import ImmunefiWriteupScraper
from .platform_writeup_scraper import PlatformWriteupScraper

# CTF analyzers
from .hackthebox_challenge_analyzer import HackTheBoxChallengeAnalyzer
from .tryhackme_challenge_analyzer import TryHackMeChallengeAnalyzer

__version__ = "2.0.0"
__author__ = "ARC Team"

# Version info
VERSION_INFO = {
    'major': 2,
    'minor': 0,
    'patch': 0,
    'release': 'AI-Enhanced',
    'features': [
        'AI Feature Extraction',
        'ML-based Success Prediction',
        'Reinforcement Learning',
        'AI Lesson Generation',
        'Closed-Loop Feedback',
        'Fine-Tuning Pipeline',
        'Advanced Integration'
    ]
}

def get_version():
    """Get current version string"""
    return f"{__version__} ({VERSION_INFO['release']})"

def list_available_components():
    """List all available components"""
    return {
        'core': [
            'ExperienceCollector',
            'FeedbackLoop',
            'ModelTrainer',
            'DynamicKnowledgeBase',
            'SelfLearningOrchestrator',
            'LearningBridge'
        ],
        'ai_enhanced': [
            'AIFeatureExtractor',
            'AIFineTuningPipeline',
            'AILessonGenerator',
            'ClosedLoopFeedback',
            'EnhancedMLTrainer',
            'ReinforcementLearner',
            'AdvancedSelfLearningIntegration'
        ],
        'supporting': [
            'TechniqueKnowledgeGraph',
            'PlaybookIntegrator',
            'CTFChallengeAnalyzer',
            'VulnerabilityPatternUnifier',
            'WriteupScrapers',
            'CTFAnalyzers'
        ]
    }

def create_advanced_integration(base_dir="~/.arc/self_learning"):
    """
    Quick factory function untuk create AdvancedSelfLearningIntegration
    
    Args:
        base_dir: Base directory untuk self-learning data
        
    Returns:
        AdvancedSelfLearningIntegration instance
    """
    return AdvancedSelfLearningIntegration(base_dir)


def create_security_validator() -> SecurityValidator:
    """
    Quick factory function untuk create SecurityValidator
    
    Returns:
        SecurityValidator instance
    """
    return SecurityValidator()
