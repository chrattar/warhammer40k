import random

from dice import DieRoll


class HitPhase:
    def __init__(self, mode="auto"):
        self.mode = mode

    def roll_d6(self):
        return random.randint(1, 6)

    def execute(self, context):
        context.add_log("===HIT PHASE===")
        context.add_log(f"Attacks: {context.attacks}")
        context.add_log(f"Ballistic Skill: {context.ballistic_skill}")

        if self.mode == "manual":
            hits = int(input("Enter Hits: "))
            context.hits = hits
            context.add_log(f"Manual Input Hits: {hits}")
            return

        ### CRETDIE ROL
        rolls = [DieRoll(self.roll_d6()) for _ in range(context.attacks)]
        context.hit_rolls = rolls

        ### EVALUATE ROLLS
        for roll in rolls:
            if roll.value > context.ballistic_skill:
                roll.is_success = True
            if roll.value == 6:
                roll.is_critical = True
        successes = [r for r in rolls if r.is_success]
        failures = [r for r in rolls if not r.is_success]
        criticals = [r for r in rolls if r.is_critical]

        context.hits = len(successes)

        # LOG GROUPS
        context.add_log(f"ROLLED: {[r.value for r in rolls]}")
        context.add_log(f"Successful Hits: {[r.value for r in successes]}")
        context.add_log(f"Failures: {[r.value for r in failures]}")
        context.add_log(f"Critical Hits (6s): {[r.value for r in criticals]}")
        context.add_log(f"Total Successful Hits: {context.hits}")

        if self.mode == "step":
            input("Press Enter to Continue...")
