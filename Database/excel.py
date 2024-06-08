import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine  # For database interaction

# Database connection function using environment variables (recommended)
def get_db_connection():
    # Access database credentials from environment variables
    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'root')
    password = os.environ.get('DB_PASSWORD', '')  # Set a strong password! (Don't leave blank)
    database = os.environ.get('DB_NAME', 'login_register_db')

    if not all([host, user, password, database]):
        raise ValueError("One or more environment variables for the database connection are missing.")
    
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

# Function to process Excel data and generate INSERT statements
def process_excel_data(file_path, table_name):
    try:
        # Use openpyxl engine to read the Excel file
        excel_data = pd.read_excel(file_path, engine='openpyxl')

        # Clean up the column names by stripping any whitespace
        excel_data.columns = excel_data.columns.str.strip()

        insert_statements = []
        for _, row in excel_data.iterrows():
            # Escape single quotes within driver names for proper SQL syntax
            escaped_driver_name = row['Driver'].replace("'", r"\'")
            insert_statement = f"""
            INSERT INTO `{table_name}`
            (`time_date`, `latitude`, `longitude`, `driver`)
            VALUES (%(time_date)s, %(latitude)s, %(longitude)s, %(driver)s);
            """
            insert_statements.append(insert_statement)

        return insert_statements

    except FileNotFoundError:
        print(f"Error: Excel file '{file_path}' not found.")
        return None  # Indicate error
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return None  # Indicate error

# Sample usage (replace with your actual logic)
if __name__ == '__main__':
    # Get environment variables
    db_host = os.environ.get('DB_HOST')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')

    # Check if all environment variables are set
    if not all([db_host, db_user, db_password, db_name]):
        print("One or more environment variables for the database connection are missing.")
    else:
        # Print the connection string for debugging purposes
        connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
        print(f"Connection string: {connection_string}")

        # Get database connection using environment variables
        engine = create_engine(connection_string)

        # Replace with your actual Excel file path and table name
        excel_file_path = r'C:\Users\Abdou\Desktop\test.xlsx'
        table_name = 'driver_location'

        # Process Excel data and generate INSERT statements
        insert_statements = process_excel_data(excel_file_path, table_name)

        if insert_statements:  # Check if data was processed successfully
            with engine.connect() as connection:
                try:
                    # Use execute instead of executemany since insert_statements is a list of strings
                    for statement in insert_statements:
                        connection.execute(statement)
                    print("Data inserted successfully from Excel!")
                except pymysql.Error as err:
                    print(f"Error inserting data: {err}")
