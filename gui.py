import tkinter as tk
from tkinter import ttk

from db import (
    get_unit_defense,
    get_weapon,
    list_factions,
    list_units_by_faction,
    list_weapons_for_unit,
)
from dice_resolver import resolve_attack


class CombatGUI:
    def __init__(self, root):
        self.root = root
        root.title("40k Dice Resolver")

        # --- FACTIONS ---
        self.factions = list_factions()

        ttk.Label(root, text="Attacker Faction").grid(row=0, column=0)
        self.att_faction = ttk.Combobox(root, values=self.factions, state="readonly")
        self.att_faction.grid(row=1, column=0)
        self.att_faction.bind("<<ComboboxSelected>>", self.update_attacker_units)

        ttk.Label(root, text="Defender Faction").grid(row=0, column=1)
        self.def_faction = ttk.Combobox(root, values=self.factions, state="readonly")
        self.def_faction.grid(row=1, column=1)
        self.def_faction.bind("<<ComboboxSelected>>", self.update_defender_units)

        # --- UNITS ---
        ttk.Label(root, text="Attacker Unit").grid(row=2, column=0)
        self.att_unit = ttk.Combobox(root, state="readonly", width=70)
        self.att_unit.grid(row=3, column=0)
        self.att_unit.bind("<<ComboboxSelected>>", self.update_weapons)

        ttk.Label(root, text="Defender Unit").grid(row=2, column=1)
        self.def_unit = ttk.Combobox(root, state="readonly", width=70)
        self.def_unit.grid(row=3, column=1)

        # --- WEAPONS ---
        ttk.Label(root, text="Weapon").grid(row=4, column=0)
        self.weapon_box = ttk.Combobox(root, state="readonly", width=40)
        self.weapon_box.grid(row=5, column=0)

        # --- ACTION ---
        ttk.Button(root, text="Resolve Attack", command=self.resolve).grid(
            row=6, column=0, columnspan=2, pady=10
        )

        self.output = tk.Text(root, height=10, width=200)
        self.output.grid(row=7, column=0, columnspan=2)

    # Update all units

    def update_attacker_units(self, _):
        faction = self.att_faction.get()
        self.att_units = list_units_by_faction(faction)
        self.att_unit["values"] = [
            f"{u[2]} ({u[3]})  T{u[4]} Sv{u[5]} W{u[6]}" for u in self.att_units
        ]
        self.att_unit.set("")
        self.weapon_box.set("")
        self.weapon_box["values"] = []

    def update_defender_units(self, _):
        faction = self.def_faction.get()
        self.def_units = list_units_by_faction(faction)
        self.def_unit["values"] = [
            f"{u[2]} ({u[3]})  T{u[4]} Sv{u[5]} W{u[6]}" for u in self.def_units
        ]
        self.def_unit.set("")

    def update_weapons(self, _):
        idx = self.att_unit.current()
        raw_unit_id = self.att_units[idx][1]  # <-- raw BSD unit_id
        self.weapons = list_weapons_for_unit(raw_unit_id)
        self.weapon_box["values"] = [w[1] for w in self.weapons]
        self.weapon_box.set("")

    # ---------- Resolve ----------

    def resolve(self):
        if -1 in (
            self.att_unit.current(),
            self.def_unit.current(),
            self.weapon_box.current(),
        ):
            return

        attacker = self.att_units[self.att_unit.current()]
        defender = self.def_units[self.def_unit.current()]
        weapon_id = self.weapons[self.weapon_box.current()][0]

        weapon = get_weapon(weapon_id)
        defense = get_unit_defense(defender[0])

        result = resolve_attack(weapon, defense)

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Attacker: {attacker[2]}\n")
        self.output.insert(tk.END, f"Defender: {defender[2]}\n\n")
        for k, v in result.items():
            self.output.insert(tk.END, f"{k}: {v}\n")


if __name__ == "__main__":
    root = tk.Tk()
    CombatGUI(root)
    root.mainloop()
