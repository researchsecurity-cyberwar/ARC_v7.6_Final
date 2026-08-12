#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Uji runtime: normalisasi success_probability dan jalur perkalian di arc_main.
Membuktikan TypeError "dict * int" TIDAK lagi muncul untuk semua bentuk input.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'c:/Projects/ARC_v7.6_Final')

print("=" * 76)
print("UJI: TypeError dict * int pada success_probability (dengan fix baru)")
print("=" * 76)

# --- 1. Uji _normalize_probability langsung ---
from UNIFIED_LEARNING_ENGINE.self_learning_orchestrator import SelfLearningOrchestrator
norm = SelfLearningOrchestrator._normalize_probability

test_cases = [
    ("float 0.7",                    0.7,                      0.7),
    ("dict {'probability':0.7}",     {'probability': 0.7},     0.7),
    ("dict {'probabilit', lain}",    {'probability': 0.85},    0.85),
    ("default (missing)",            None,                     0.5),
    ("dict {'success_probability'}", {'success_probability': 0.5}, 0.5),
    ("int 1",                        1,                        1.0),
    ("str non-numeric",              "hello",                  0.5),
    ("dict bersarang",               {'success_probability': {'probability': 0.4}}, 0.4),
    ("dict tidak dikenal",           {'foo': 1},               0.5),
    ("bool True",                    True,                     1.0),
    ("negatif",                      -0.3,                     0.0),
    (">1",                           1.9,                      1.0),
]

all_ok = True
for desc, inp, expected in test_cases:
    try:
        got = norm(inp)
        ok = (abs(got - expected) < 1e-9)
        all_ok = all_ok and ok
        print(f"  {'PASS' if ok else 'FAIL'}  {desc:30s} -> {got}  (expected {expected})")
    except Exception as e:
        all_ok = False
        print(f"  FAIL  {desc:30s} -> EXCEPTION {e}")

# --- 2. Simulasi jalur perkalian di arc_main (baris 992-1000) ---
print("\n[2] SIMULASI jalur arc_main: success_prob * 100")
def arc_style(success_prob):
    if isinstance(success_prob, dict):
        success_prob = success_prob.get('probability',
                                        success_prob.get('success_probability', 0.5))
    try:
        success_prob = float(success_prob)
    except (TypeError, ValueError):
        success_prob = 0.5
    return success_prob * 100

inputs = [
    {'probability': 0.7},          # kasus awal -> 70.0
    {'success_probability': 0.5},  # -> 50.0
    0.85,                           # -> 85.0
    None,                           # default -> 50.0
]
expected_pct = [70.0, 50.0, 85.0, 50.0]
for i, (inp, exp) in enumerate(zip(inputs, expected_pct)):
    try:
        got = arc_style(inp)
        ok = abs(got - exp) < 1e-9
        all_ok = all_ok and ok
        print(f"  {'PASS' if ok else 'FAIL'}  input={inp} -> {got}%  (expected {exp}%)")
    except Exception as e:
        all_ok = False
        print(f"  FAIL  input={inp} -> EXCEPTION {e}")

# --- 3. Uji get_learning_recommendations end-to-end (mock trainer return dict) ---
print("\n[3] UJI get_learning_recommendations (mock model_trainer mengembalikan dict)")
import types
orch = SelfLearningOrchestrator.__new__(SelfLearningOrchestrator)
# stub model_trainer yang selalu mengembalikan dict {'probability': 0.66}
class FakeTrainer:
    def predict_success_probability(self, context, exp=None):
        return {'probability': 0.66}
orch.model_trainer = FakeTrainer()
# stub knowledge_base minimal
class FakeKB:
    knowledge = {}
    def get_relevant_lessons(self, ctx):
        return []
orch.knowledge_base = FakeKB()
try:
    recs = SelfLearningOrchestrator.get_learning_recommendations(orch, {}, "vuln")
    sp = recs['success_probability']
    ok = isinstance(sp, float) and abs(sp - 0.66) < 1e-9
    all_ok = all_ok and ok
    print(f"  {'PASS' if ok else 'FAIL'}  success_probability = {sp} ({type(sp).__name__}), perkalian-> {sp*100:.1f}%")
except Exception as e:
    all_ok = False
    import traceback; traceback.print_exc()
    print(f"  FAIL  EXCEPTION {e}")

# --- 4. Uji end-to-end dengan return dict {'success_probability': {'probability': 0.55}} ---
print("[4] UJI dengan dict bersarang sebagai return trainer")
class FakeTrainer2:
    def predict_success_probability(self, context, exp=None):
        return {'success_probability': {'probability': 0.55}}
orch.model_trainer = FakeTrainer2()
try:
    recs = SelfLearningOrchestrator.get_learning_recommendations(orch, {}, "vuln")
    sp = recs['success_probability']
    ok = isinstance(sp, float) and abs(sp - 0.55) < 1e-9
    all_ok = all_ok and ok
    print(f"  {'PASS' if ok else 'FAIL'}  success_probability = {sp} ({type(sp).__name__})")
except Exception as e:
    all_ok = False
    import traceback; traceback.print_exc()

print("\n" + "=" * 76)
print("HASIL: ", "SEMUA LULUS ✅" if all_ok else "ADA GAGAL ❌")
print("=" * 76)
sys.exit(0 if all_ok else 1)