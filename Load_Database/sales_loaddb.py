import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
import numpy as np

# Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'returns_db'
DB_PORT = 3306  # Adjust if needed

# Define the directory path for sales data
sales_folders = {
    "2023": "Data/Sales/2023",
    "2024": "Data/Sales/2024"
}

# Map month numbers to month names
MONTH_MAP = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}

# Connect to MySQL database
def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        return connection
    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None

# Clean and standardize column names
def clean_column_name(col):
    col = col.strip()  # Remove leading/trailing whitespace
    col = col.replace(' ', '_').replace('-', '_')  # Replace spaces and dashes with underscores
    col = ''.join(c for c in col if c.isalnum() or c == '_')  # Keep only alphanumeric and underscore
    return col.lower()  # Convert to lowercase for consistency

# Create the sales table with dynamic column creation and cleaned column names
def create_sales_table(connection, sample_data):
    cursor = connection.cursor()

    # Clean and update column names
    sample_data.columns = [clean_column_name(col) for col in sample_data.columns]

    # Build the CREATE TABLE query with dynamic columns
    columns = []
    for col, dtype in sample_data.dtypes.items():
        mysql_type = infer_mysql_data_type(dtype)
        columns.append(f"`{col}` {mysql_type}")

    # Add month and year columns
    columns.extend(["month VARCHAR(50)", "year INT"])
    create_table_query = f"CREATE TABLE IF NOT EXISTS sales (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(columns)});"

    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()

# Infer MySQL data types based on pandas data types
def infer_mysql_data_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATETIME"
    else:
        return "TEXT"

# Load sales .txt data into MySQL with data cleaning
def load_txt_data_to_mysql(connection, folder_path, year):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            # Extract month and year from the filename
            month_num, _ = file_name.split('-')
            month_name = MONTH_MAP[int(month_num)]
            year = int(year)

            # Load .txt file with low_memory=False and encoding
            file_path = os.path.join(folder_path, file_name)
            data = pd.read_csv(file_path, sep='\t', encoding='ISO-8859-1', low_memory=False)

            # Clean column names in the data to match the table schema
            data.columns = [clean_column_name(col) for col in data.columns]

            # Add month and year columns
            data['month'] = month_name
            data['year'] = year

            # Convert any numeric columns to handle non-numeric values and replace NaN with 0 or None
            for col in data.select_dtypes(include=['float64', 'int64']).columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)

            # Replace NaN in columns with None for SQL compatibility
            data = data.where(pd.notnull(data), None)

            # Insert data into the sales table
            cursor = connection.cursor()
            for _, row in data.iterrows():
                placeholders = ", ".join(["%s"] * len(row))
                columns = ", ".join(f"`{col}`" for col in row.index)
                sql = f"INSERT INTO sales ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row))
            connection.commit()
            cursor.close()
            print(f"Data from {file_name} inserted successfully.")

# Main script to connect, create sales table, and load data
connection = create_database_connection()
if connection:
    # Use the first file as a sample to create the table structure
    sample_file_path = os.path.join(sales_folders["2023"], os.listdir(sales_folders["2023"])[0])
    sample_data = pd.read_csv(sample_file_path, sep='\t', encoding='ISO-8859-1', low_memory=False)
    create_sales_table(connection, sample_data)
    
    for year, path in sales_folders.items():
        load_txt_data_to_mysql(connection, path, year)
    
    connection.close()
else:
    print("Failed to connect to the database.")