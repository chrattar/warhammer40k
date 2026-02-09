import sqlite3
from pathlib import Path

DB_NAME = str(Path(__file__).parent / "wh40k.db")


def load_dataframes_to_sqlite(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # wipe tables first (commit once)
    for table in ["units", "weapons", "abilities", "unit_weapons", "unit_abilities"]:
        cur.execute(f"DELETE FROM {table}")
    conn.commit()

    # ----- UNITS (fix primary key) -----
    u = data["units"].copy()
    u["id"] = u["unit_id"].astype(str) + "::" + u["profile_name"].astype(str)
    u = u.rename(columns={"unit_name": "name"})

    u[
        [
            "id",
            "unit_id",
            "name",
            "faction",
            "profile_name",
            "toughness",
            "save",
            "wounds",
            "leadership",
            "objective_control",
            "legends",
        ]
    ].to_sql("units", conn, if_exists="append", index=False)

    # ----- WEAPONS -----
    data["weapons"].rename(
        columns={"weapon_id": "id", "weapon_name": "name", "weapon_type": "type"}
    )[
        ["id", "name", "type", "range", "attacks", "skill", "strength", "ap", "damage"]
    ].to_sql("weapons", conn, if_exists="append", index=False)

    # ----- ABILITIES -----
    data["abilities"].rename(columns={"ability_id": "id", "ability_name": "name"})[
        ["id", "name", "description"]
    ].to_sql("abilities", conn, if_exists="append", index=False)

    # ----- LINKS -----
    data["unit_weapons"][["unit_id", "weapon_id"]].to_sql(
        "unit_weapons", conn, if_exists="append", index=False
    )
    data["unit_abilities"][["unit_id", "ability_id"]].to_sql(
        "unit_abilities", conn, if_exists="append", index=False
    )

    conn.close()
