import sqlite3
from pathlib import Path

DB_NAME = str(Path(__file__).parent / "wh40k.db")


def get_weapon(weapon_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT attacks, skill, strength, ap, damage
        FROM weapons
        WHERE id = ?
    """,
        (weapon_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError("Weapon not found")
    return {
        "attacks": row[0],
        "skill": row[1],
        "strength": row[2],
        "ap": row[3],
        "damage": row[4],
    }


def list_units_by_faction(faction):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, unit_id, name, profile_name, toughness, save, wounds
        FROM units
        WHERE faction = ?
          AND legends != 'Legends-NotActive'
        ORDER BY name, profile_name
    """,
        (faction,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_unit_defense(unit_pk_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT toughness, save, wounds
        FROM units
        WHERE id = ?
    """,
        (unit_pk_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError("Unit not found")
    return {"toughness": row[0], "save": row[1], "wounds": row[2]}


def list_weapons_for_unit(unit_pk_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT w.id, w.name
        FROM weapons w
        JOIN unit_weapons uw
            ON uw.weapon_id = w.id
        WHERE uw.unit_id = ?
        ORDER BY w.name
    """,
        (unit_pk_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def list_factions():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT faction
        FROM units
        WHERE faction IS NOT NULL AND faction != ''
        ORDER BY faction
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
