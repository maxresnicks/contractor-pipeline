import duckdb
import os

def get_connection():
    # Ensure the db directory exists
    os.makedirs("db", exist_ok=True)
    # This creates or connects to a local file called warehouse.duckdb
    return duckdb.connect("db/warehouse.duckdb")