from combat_context import CombatContext
from engine import CombatEngine

engine = CombatEngine(mode="step")

context = CombatContext(attacks=10, ballistic_skill=3)

engine.resolve_hit_phase(context)
