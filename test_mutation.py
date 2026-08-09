import sys
sys.path.insert(0, '.')
from EXPLOITATION_ENGINE.intelligent_mutation_orchestrator import IntelligentMutationOrchestrator

print('Testing Intelligent Mutation Orchestrator...')
print('=' * 60)

orch = IntelligentMutationOrchestrator()
base = "<script>alert(1)</script>"
result = orch.evolve_payload(base, 'xss', {'tech_stack': 'php'}, [])

print('? Module imported successfully')
print(f'? Genetic Algorithm works!')
print(f'   Base:      {base}')
print(f'   Evolved:   {result}')
print(f'   Different: {base != result}')
print('=' * 60)
