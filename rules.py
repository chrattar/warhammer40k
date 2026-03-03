class Rule:
    def apply(self, context, phase):
        pass


class LethalHits(Rule):
    def apply(self, context, phase):
        if phase != "hit":
            return

        for roll in context.hit_rolls:
            if roll.is_critical:
                roll.auto_wound = True

        auto_wounds = [r for r in context.hit_rolls if r.auto_wound]
        context.auto_wounds = len(auto_wounds)

        if auto_wounds:
            context.add_log(f"Lethal Hits: {len(auto_wounds)} wounds")
