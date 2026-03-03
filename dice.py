class DieRoll:
    def __init__(self, value):
        self.value = value
        self.modified = value
        self.is_success = False
        self.is_critical = False
        self.was_rerolled = False
        self.generated_extra_hits = 0
        self.auto_wound = False
