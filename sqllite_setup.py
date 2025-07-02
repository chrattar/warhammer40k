import pandas as pd
import sqlite3
import numpy as np
from sqlalchemy import create_engine

# Convert Excel to SQLite database for better performance
def excel_to_sqlite(excel_file, db_file):
    """Convert Excel sheets to SQLite database"""
    engine = create_engine(f'sqlite:///{db_file}')
    
    # Read all sheets from Excel
    excel_data = pd.read_excel(excel_file, sheet_name=None)
    
    # Write to SQLite
    for table_name, df in excel_data.items():
        df.to_sql(table_name, engine, if_exists='replace', index=False)
    
    print(f"Database created: {db_file}")
    return engine

# Usage
engine = excel_to_sqlite('wh40k_complete_database.xlsx', 'wh40k_database.db')
