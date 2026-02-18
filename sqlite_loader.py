import sqlite3
from pathlib import Path

DB_NAME = str(Path(__file__).resolve().parent / "wh40k.db")


def load_dataframes_to_sqlite(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # wipe tables first
    for table in ["units", "weapons", "abilities", "unit_weapons", "unit_abilities"]:
        cur.execute(f"DELETE FROM {table}")
    conn.commit()

    # ----- UNITS -----
    u = data["units"].copy()

    u["id"] = (
        u["faction"].astype(str)
        + "::"
        + u["unit_id"].astype(str)
        + "::"
        + u["profile_name"].astype(str)
    )

    u = u.drop_duplicates(subset=["id"]).copy()
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
    w = data["weapons"].copy()

    w["id"] = w["faction"].astype(str) + "::" + w["weapon_id"].astype(str)

    w = w.drop_duplicates(subset=["id"]).copy()
    w = w.rename(columns={"weapon_name": "name", "weapon_type": "type"})

    w[
        ["id", "name", "type", "range", "attacks", "skill", "strength", "ap", "damage"]
    ].to_sql("weapons", conn, if_exists="append", index=False)

    # ----- ABILITIES -----
    a = data["abilities"].copy()

    a["id"] = a["faction"].astype(str) + "::" + a["ability_id"].astype(str)

    a = a.drop_duplicates(subset=["id"]).copy()
    a = a.rename(columns={"ability_name": "name"})

    a[["id", "name", "description"]].to_sql(
        "abilities", conn, if_exists="append", index=False
    )

    # ----- LINKS -----

    # Build lookup for profile_name per (faction, unit_id)
    profile_lookup = (
        u[["faction", "unit_id", "profile_name"]]
        .drop_duplicates()
        .set_index(["faction", "unit_id"])
    )

    # Unit → Weapons
    uw = data["unit_weapons"].copy()

    uw = uw.merge(
        profile_lookup,
        left_on=["faction", "unit_id"],
        right_index=True,
        how="left",
    )

    uw["unit_id"] = (
        uw["faction"].astype(str)
        + "::"
        + uw["unit_id"].astype(str)
        + "::"
        + uw["profile_name"].astype(str)
    )

    uw["weapon_id"] = uw["faction"].astype(str) + "::" + uw["weapon_id"].astype(str)

    uw = uw.drop_duplicates(subset=["unit_id", "weapon_id"]).copy()

    uw[["unit_id", "weapon_id"]].to_sql(
        "unit_weapons", conn, if_exists="append", index=False
    )

    # Unit → Abilities
    ua = data["unit_abilities"].copy()

    ua = ua.merge(
        profile_lookup,
        left_on=["faction", "unit_id"],
        right_index=True,
        how="left",
    )

    ua["unit_id"] = (
        ua["faction"].astype(str)
        + "::"
        + ua["unit_id"].astype(str)
        + "::"
        + ua["profile_name"].astype(str)
    )

    ua["ability_id"] = ua["faction"].astype(str) + "::" + ua["ability_id"].astype(str)

    ua = ua.drop_duplicates(subset=["unit_id", "ability_id"]).copy()

    ua[["unit_id", "ability_id"]].to_sql(
        "unit_abilities", conn, if_exists="append", index=False
    )

    conn.close()
