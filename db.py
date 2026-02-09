import sqlite3

DB_NAME = "wh40k.db"


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


def get_unit_defense(unit_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT toughness, save, wounds
        FROM units
        WHERE id = ?
    """,
        (unit_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise ValueError("Unit not found")

    return {
        "toughness": row[0],
        "save": row[1],
        "wounds": row[2],
    }


def list_units(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, faction
        FROM units
        WHERE legends = 'TournamentPlay'
        ORDER BY faction, name
        LIMIT ?
    """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def list_weapons_for_unit(unit_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT w.id, w.name
        FROM weapons w
        JOIN unit_weapons uw ON uw.weapon_id = w.id
        WHERE uw.unit_id = ?
    """,
        (unit_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def list_units_with_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, faction, toughness, save, wounds
        FROM units
        WHERE legends = 'TournamentPlay'
        ORDER BY faction, name
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def list_factions():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT faction
        FROM units
        WHERE legends = 'TournamentPlay'
        ORDER BY faction
    """)
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def list_units_by_faction(faction):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, toughness, save, wounds
        FROM units
        WHERE faction = ?
            AND legends = 'TournamentPlay'
        ORDER BY name
    """,
        (faction,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows
