import random


class CombatContext:
    def __init__(self, attacks, ballistic_skill):
        self.attacks = attacks
        self.ballistic_skill = ballistic_skill
        self.hit_rolls = []
        self.hits = []
        self.rules = []
        self.auto_wounds = 0

        self.log = []

    def add_log(self, message):
        self.log.append(message)

    def display_log(self):
        print(f"\n".join(self.log))
