import sqlite3
import pandas as pd
import os

def create_connection():
    """Create a connection to the SQLite database"""
    try:
        conn = sqlite3.connect('mba_tech_data.db')
        print("Successfully connected to SQLite database")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table(conn, table_name, columns):
    """Create a new table in the database"""
    try:
        cursor = conn.cursor()
        
        # Create table with specified columns
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(columns)}
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Successfully created table: {table_name}")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_data(conn, table_name, data):
    """Insert data into the table"""
    try:
        cursor = conn.cursor()
        
        # Get column names from the first row of data
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['?' for _ in data[0]])
        
        # Create insert query
        insert_query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        """
        
        # Insert each row of data
        for row in data:
            cursor.execute(insert_query, list(row.values()))
        
        conn.commit()
        print(f"Successfully inserted {len(data)} rows into {table_name}")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")

def insert_from_excel(conn, table_name, excel_file):
    """Insert data from Excel file into the table"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Clean column names
        df.columns = [col.strip().replace(' ', '_').replace('.', '_') for col in df.columns]
        
        # Insert data into table
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Successfully inserted data from {excel_file} into {table_name}")
    except Exception as e:
        print(f"Error inserting from Excel: {e}")

def view_data(conn, table_name):
    """View data from the table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Print data
        print(f"\nData in {table_name}:")
        print("Columns:", columns)
        for row in rows[:5]:  # Show first 5 rows
            print(row)
        print(f"... and {len(rows)-5} more rows")
    except sqlite3.Error as e:
        print(f"Error viewing data: {e}")

def main():
    # Create connection
    conn = create_connection()
    if conn is None:
        return

    # Example 1: Create a table and insert data manually
    print("\nExample 1: Manual data insertion")
    table_name = "example_table"
    columns = [
        "id INTEGER PRIMARY KEY",
        "name TEXT",
        "age INTEGER",
        "email TEXT"
    ]
    
    # Create table
    create_table(conn, table_name, columns)
    
    # Sample data
    data = [
        {"id": 1, "name": "John Doe", "age": 25, "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "age": 30, "email": "jane@example.com"},
        {"id": 3, "name": "Bob Johnson", "age": 35, "email": "bob@example.com"}
    ]
    
    # Insert data
    insert_data(conn, table_name, data)
    
    # View data
    view_data(conn, table_name)

    # Example 2: Insert data from Excel
    print("\nExample 2: Excel data insertion")
    excel_file = "MBA.Tech 25.xlsx"
    if os.path.exists(excel_file):
        table_name = "mba_tech_25"
        insert_from_excel(conn, table_name, excel_file)
        view_data(conn, table_name)
    else:
        print(f"Excel file {excel_file} not found")

    # Close connection
    conn.close()
    print("\nDatabase connection closed")

if __name__ == "__main__":
    main() 