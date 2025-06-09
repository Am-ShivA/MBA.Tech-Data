import pandas as pd
import sqlite3
import os
import tempfile

def get_db_path():
    """Get the database path, using a temporary directory in Streamlit Cloud"""
    if os.path.exists('mba_tech_data.db'):
        return 'mba_tech_data.db'
    else:
        # In Streamlit Cloud, use a temporary directory
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, 'mba_tech_data.db')

def create_database():
    # Create a new SQLite database
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read Excel files
    excel_files = {
        'mba_tech_23': 'MBA.Tech 23.xlsx',
        'mba_tech_24': 'MBA.Tech 24.xlsx',
        'mba_tech_25': 'MBA.Tech 25.xlsx'
    }

    for table_name, excel_file in excel_files.items():
        if os.path.exists(excel_file):
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Clean column names (remove spaces and special characters)
            df.columns = [col.strip().replace(' ', '_').replace('.', '_') for col in df.columns]
            
            # Write to SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Created table {table_name} from {excel_file}")

    # Create a view for all batches
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS all_batches AS
    SELECT 'MBA.Tech 23' as Batch, * FROM mba_tech_23
    UNION ALL
    SELECT 'MBA.Tech 24' as Batch, * FROM mba_tech_24
    UNION ALL
    SELECT 'MBA.Tech 25' as Batch, * FROM mba_tech_25
    ''')

    conn.commit()
    conn.close()
    print(f"Database creation completed! Database location: {db_path}")

if __name__ == "__main__":
    create_database() 