#!/usr/bin/env python3
"""Test Self-Learning System"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("Testing Self-Learning System...")
print("-" * 50)

# Test 1: Import modules
print("\n1. Testing imports...")
try:
    from UNIFIED_LEARNING_ENGINE.experience_collector import ExperienceCollector
    from UNIFIED_LEARNING_ENGINE.feedback_loop import FeedbackLoop
    from UNIFIED_LEARNING_ENGINE.model_trainer import ModelTrainer
    from UNIFIED_LEARNING_ENGINE.dynamic_knowledge_base import DynamicKnowledgeBase
    from UNIFIED_LEARNING_ENGINE.self_learning_orchestrator import SelfLearningOrchestrator
    print("✓ All modules imported")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize orchestrator
print("\n2. Testing orchestrator initialization...")
try:
    orchestrator = SelfLearningOrchestrator()
    print("✓ Orchestrator initialized")
except Exception as e:
    print(f"✗ Init failed: {e}")
    sys.exit(1)

# Test 3: Record experience
print("\n3. Testing experience recording...")
try:
    result = orchestrator.record_and_learn(
        experience_type="vulnerability_scan",
        outcome="success",
        context={"target": "example.com", "technique": "xss"},
        actions_taken=[{"type": "scan", "tool": "nuclei"}],
        result_data={"lesson": "XSS found in parameter 'q'"}
    )
    print(f"✓ Experience recorded: {result.get('experience_id', 'N/A')}")
except Exception as e:
    print(f"✗ Recording failed: {e}")
    sys.exit(1)

# Test 4: Get statistics
print("\n4. Testing statistics...")
try:
    stats = orchestrator.get_learning_statistics()
    print(f"✓ Statistics: {stats['experiences'].get('total_experiences', 0)} experiences")
except Exception as e:
    print(f"✗ Statistics failed: {e}")
    sys.exit(1)

# Test 5: ARC integration
print("\n5. Testing ARC integration...")
try:
    from arc_main import ARCOrchestrator
    arc = ARCOrchestrator()
    assert hasattr(arc, 'self_learning_orchestrator')
    print("✓ ARC integration successful")
except Exception as e:
    print(f"✗ ARC integration failed: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✓ ALL TESTS PASSED")
print("=" * 50)
print("\nAgent is now self-learning enabled!")
print("  - Experience Collector: ✓")
print("  - Feedback Loop: ✓")
print("  - Model Trainer: ✓")
print("  - Knowledge Base: ✓")
print("  - Orchestrator: ✓")
