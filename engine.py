from hit_phase import HitPhase


class CombatEngine:
    def __init__(self, mode="auto"):
        self.mode = mode
        self.hit_phase = HitPhase(mode=mode)

    def resolve_hit_phase(self, context):
        self.hit_phase.execute(context)
        context.display_log()
