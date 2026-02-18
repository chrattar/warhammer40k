from db import list_units_by_faction, list_weapons_for_unit

units = list_units_by_faction("Chaos Chaos Knights Library")

print("Sample unit tuple:", units[0])

unit_pk = units[0][0]  # <-- USE INDEX 0
print("Unit PK:", unit_pk)

weapons = list_weapons_for_unit(unit_pk)
print("Weapons found:", len(weapons))
print(weapons[:5])
