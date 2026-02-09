from bsd_parser import process_all_factions
from sqlite_loader import load_dataframes_to_sqlite
from sqlite_setup import create_schema

REPO_PATH = "wh40k-10e"

if __name__ == "__main__":
    create_schema()
    data = process_all_factions(REPO_PATH)
    load_dataframes_to_sqlite(data)
    print("Data loaded into SQLite.")
