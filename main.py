from pathlib import Path
from bsd_parser import process_all_factions
from sqlite_loader import load_dataframes_to_sqlite
from sqlite_setup import create_schema

# Resolve project root dynamically (works on any machine)
PROJECT_ROOT = Path(__file__).resolve().parent
REPO_PATH = PROJECT_ROOT / "wh40k-10e"

if __name__ == "__main__":

    if not REPO_PATH.exists():
        print(f"Data repository not found at: {REPO_PATH}")
        print("Please run: git clone https://github.com/BSData/wh40k-10e.git")
        exit(1)

    create_schema()

    data = process_all_factions(str(REPO_PATH))

    if data["units"].empty:
        print("No .cat files found or no units parsed. Skipping database load.")
        exit(0)

    load_dataframes_to_sqlite(data)

    print("Data loaded into SQLite successfully.")
