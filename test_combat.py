from db import get_unit_defense, get_weapon, list_units, list_weapons_for_unit
from dice_resolver import resolve_attack

# 1. Pick attacker
units = list_units(20)
for i, u in enumerate(units):
    print(i, u)

attacker_idx = int(input("Select attacker unit: "))
attacker_id = units[attacker_idx][0]

# 2. Pick weapon
weapons = list_weapons_for_unit(attacker_id)
for i, w in enumerate(weapons):
    print(i, w)

weapon_idx = int(input("Select weapon: "))
weapon_id = weapons[weapon_idx][0]

# 3. Pick defender
for i, u in enumerate(units):
    print(i, u)

defender_idx = int(input("Select defender unit: "))
defender_id = units[defender_idx][0]

# 4. Resolve
weapon = get_weapon(weapon_id)
defender = get_unit_defense(defender_id)

result = resolve_attack(weapon, defender)

print("\n=== RESULT ===")
for k, v in result.items():
    print(f"{k}: {v}")
