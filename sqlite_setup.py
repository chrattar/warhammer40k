import sqlite3

DB_NAME = "wh40k.db"


def create_schema():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS factions;
    DROP TABLE IF EXISTS units;
    DROP TABLE IF EXISTS weapons;
    DROP TABLE IF EXISTS abilities;
    DROP TABLE IF EXISTS unit_weapons;
    DROP TABLE IF EXISTS unit_abilities;

    CREATE TABLE factions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );

CREATE TABLE units (
    id TEXT PRIMARY KEY,
    unit_id TEXT,
    name TEXT,
    faction TEXT,
    profile_name TEXT,
    toughness INTEGER,
    save INTEGER,
    wounds INTEGER,
    leadership INTEGER,
    objective_control INTEGER,
    legends TEXT
);


    CREATE TABLE weapons (
        id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        range INTEGER,
        attacks INTEGER,
        skill INTEGER,
        strength INTEGER,
        ap INTEGER,
        damage INTEGER
    );

    CREATE TABLE abilities (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT
    );

    CREATE TABLE unit_weapons (
        unit_id TEXT,
        weapon_id TEXT
    );

    CREATE TABLE unit_abilities (
        unit_id TEXT,
        ability_id TEXT
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_schema()
    print("SQLite schema created.")
