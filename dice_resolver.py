import random


def roll_d6(n):
    return [random.randint(1, 6) for _ in range(n)]


def cutoff(rolls, target):
    return [r for r in rolls if r >= target]


def wound_target(strength, toughness):
    if strength >= toughness * 2:
        return 2
    if strength > toughness:
        return 3
    if strength == toughness:
        return 4
    if strength * 2 <= toughness:
        return 6
    return 5


def resolve_attack(weapon, defender):
    # Hits
    hit_rolls = roll_d6(weapon["attacks"])
    hits = cutoff(hit_rolls, weapon["skill"])

    # Wounds
    wound_rolls = roll_d6(len(hits))
    wound_on = wound_target(weapon["strength"], defender["toughness"])
    wounds = cutoff(wound_rolls, wound_on)

    # Saves
    save_target = max(2, defender["save"] - weapon["ap"])
    save_rolls = roll_d6(len(wounds))
    failed_saves = [r for r in save_rolls if r < save_target]

    damage = len(failed_saves) * weapon["damage"]

    return {
        "hits": len(hits),
        "wounds": len(wounds),
        "failed_saves": len(failed_saves),
        "damage": damage,
    }
