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

def standardize_columns(df):
    """Standardize column names across different Excel files"""
    # Keys are common variations found in Excel, values are the desired standardized names.
    # All keys will be normalized (stripped, no spaces/dots, uppercase) for robust matching.
    # All values are the exact desired column names after standardization.
    column_mapping = {
        'ROLL NO.': 'Roll No.',
        'ROLL NO': 'Roll No.',
        'SAP ID': 'Sap Id',
        'SAPID': 'Sap Id',
        'NAME': 'Name',
        'BRANCH': 'Branch',
        'CAMPUS': 'Campus',
        'DIV': 'Div',
        'MIP COMPANY': 'Mip Company',
        'MAJOR': 'Major',

        # Variations for Contact Number
        'CONTACT NO.': 'Contact No.',
        'CONTACT NO': 'Contact No.',
        'CONTACT NUMBER': 'Contact No.',
        'Contact No': 'Contact No.',
        'Contact Number': 'Contact No.',
        'CONTACTNUMBER': 'Contact No.',
        'MOBILE NO': 'Contact No.',
        'MOBILE NUMBER': 'Contact No.',
        'PHONE': 'Contact No.',
        'PHONE NO': 'Contact No.',
        'PHONE NUMBER': 'Contact No.',
        'CELL NO': 'Contact No.',
        'CELL NUMBER': 'Contact No.',

        # Variations for NMIMS Email
        'NMIMS EMAIL ID': 'Nmims Email',
        'NMIMS EMAIL': 'Nmims Email',
        'NMIMS Email ID': 'Nmims Email',
        'NMIMS Email': 'Nmims Email',
        'Email': 'Nmims Email',
        'EMAIL': 'Nmims Email',
        'E-MAIL': 'Nmims Email',
        'STUDENT EMAIL': 'Nmims Email',
        'OFFICIAL EMAIL': 'Nmims Email',
    }

    # Create a reverse mapping for efficient lookup after normalization
    normalized_mapping = {key.strip().replace(' ', '').replace('.', '').replace('-', '').upper(): value for key, value in column_mapping.items()}

    new_columns = {}
    for col in df.columns:
        normalized_col = col.strip().replace(' ', '').replace('.', '').replace('-', '').upper()
        if normalized_col in normalized_mapping:
            new_columns[col] = normalized_mapping[normalized_col]
        else:
            # If not explicitly mapped, try to title case it.
            new_columns[col] = col.strip().replace('_', ' ').title()

    df = df.rename(columns=new_columns)
    return df

def create_database():
    # Create a new SQLite database
    db_path = get_db_path()
    print(f"Creating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read Excel files
    excel_files = {
        'mba_tech_25': 'MBA.Tech 25.xlsx',
        'mba_tech_26': 'MBA.Tech 26.xlsx'
    }

    print("\nProcessing Excel files:")
    available_tables = []
    for table_name, excel_file in excel_files.items():
        print(f"\nChecking for file: {excel_file}")
        if os.path.exists(excel_file):
            print(f"Found {excel_file}, creating table {table_name}")
            # Read Excel file
            df = pd.read_excel(excel_file)
            print(f"Read {len(df)} rows from {excel_file}")
            
            # Standardize column names
            df = standardize_columns(df)
            print(f"Columns in table: {', '.join(df.columns)}")
            
            # Write to SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Created table {table_name} from {excel_file}")
            available_tables.append(table_name)
        else:
            print(f"File not found: {excel_file}")

    # Create a view that combines all batches
    if available_tables:
        print("\nCreating view for all batches...")
        view_query = f"""
        CREATE VIEW IF NOT EXISTS all_batches AS
        SELECT 'MBA.Tech 25' as batch, * FROM mba_tech_25
        UNION ALL
        SELECT 'MBA.Tech 26' as batch, * FROM mba_tech_26
        """
        cursor.execute(view_query)
        print("Created view 'all_batches'")
    else:
        print("\nNo tables were created, skipping view creation")

    conn.commit()
    conn.close()
    print(f"\nDatabase creation completed! Database location: {db_path}")

if __name__ == "__main__":
    create_database() 