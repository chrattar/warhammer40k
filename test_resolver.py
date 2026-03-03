from combat_context import CombatContext
from engine import CombatEngine
from rules import LethalHits

engine = CombatEngine(mode="step")

context = CombatContext(attacks=10, ballistic_skill=3)
context.rules.append(LethalHits())

engine.resolve_hit_phase(context)
