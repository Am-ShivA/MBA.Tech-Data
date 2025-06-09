import pandas as pd

def check_excel_columns():
    # Check MBA.Tech 25.xlsx
    print("\nChecking MBA.Tech 25.xlsx:")
    try:
        df = pd.read_excel("MBA.Tech 25.xlsx")
        print("Columns:")
        for col in df.columns:
            print(f"- {col}")
    except Exception as e:
        print(f"Error reading file: {e}")

    # Check MBA.Tech 26.xlsx
    print("\nChecking MBA.Tech 26.xlsx:")
    try:
        df = pd.read_excel("MBA.Tech 26.xlsx")
        print("Columns:")
        for col in df.columns:
            print(f"- {col}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_excel_columns() 