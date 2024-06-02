from db_connection import get_db

# Sample function to query data from the database
def query_data(query: str):
    db = next(get_db())
    result = db.execute(query).fetchall()
    return result

# Example usage
if __name__ == "__main__":
    sample_query = "SELECT * FROM your_table LIMIT 10;"
    data = query_data(sample_query)
    for row in data:
        print(row)
